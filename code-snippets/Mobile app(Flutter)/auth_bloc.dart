import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/network/auth_event_bus.dart';
import '../../../core/services/biometric_service.dart';
import '../../../core/storage/secure_storage.dart';
import '../../../features/auth/domain/repositories/auth_repository.dart';
import '../../models/user_model.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc({
    required AppSecureStorage secureStorage,
    required AuthRepository authRepository,
    required BiometricService biometricService,
  })  : _secureStorage = secureStorage,
        _authRepository = authRepository,
        _biometricService = biometricService,
        super(const AuthInitial()) {
    on<AuthCheckRequested>(_onCheckRequested);
    on<LoginSubmitted>(_onLoginSubmitted);
    on<BiometricLoginRequested>(_onBiometricLoginRequested);
    on<AuthUserLoaded>(_onUserLoaded);
    on<AuthSignOutRequested>(_onSignOutRequested);
    on<AuthTokenRefreshed>(_onTokenRefreshed);
    on<_AuthForcedLogout>(_onForcedLogout);

    // The RefreshInterceptor fires on this bus when a silent token refresh
    // fails — no direct coupling between the network layer and the BLoC.
    _busSubscription = AuthEventBus.instance.stream.listen((event) {
      if (event is ForceLogoutEvent) add(_AuthForcedLogout(event.reason));
    });
  }

  final AppSecureStorage _secureStorage;
  final AuthRepository _authRepository;
  final BiometricService _biometricService;
  late final StreamSubscription<AuthBusEvent> _busSubscription;

  static final _epoch = DateTime.utc(1970);

  // ── App startup check ──────────────────────────────────────────────────────

  Future<void> _onCheckRequested(
    AuthCheckRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());
    try {
      final token = await _secureStorage.getAccessToken();
      if (token == null) {
        emit(const AuthUnauthenticated());
        return;
      }

      // Emit a lightweight authenticated state using cached role so the
      // router can gate navigation immediately while /me is fetched in the
      // background by SubscriptionCubit. A subsequent AuthUserLoaded event
      // will upgrade this to the full user model once available.
      emit(
        AuthAuthenticated(
          UserModel(
            id: 'pending',
            name: '',
            email: '',
            role: UserRole.fromString(
              await _secureStorage.getUserRole() ?? 'staff',
            ),
            businessId: await _secureStorage.getBusinessId(),
            isActive: true,
            createdAt: _epoch,
            updatedAt: _epoch,
          ),
        ),
      );
    } catch (_) {
      emit(const AuthUnauthenticated());
    }
  }

  // ── Password login ─────────────────────────────────────────────────────────

  Future<void> _onLoginSubmitted(
    LoginSubmitted event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    // 1. Authenticate against the backend.
    final loginResult = await _authRepository.login(
      email: event.email,
      password: event.password,
    );

    await loginResult.fold(
      (failure) async => emit(AuthError(failure.message)),
      (authResponse) async {
        // 2. Persist tokens and decoded JWT claims before any further calls.
        await _secureStorage.saveTokens(
          accessToken: authResponse.accessToken,
          refreshToken: authResponse.refreshToken,
        );
        await _secureStorage.saveUserInfo(
          userId: '', // populated from /me below
          role: authResponse.role,
          businessId: authResponse.businessId ?? '',
        );

        // 3. Fetch the full user profile now that the access token is stored.
        //    The AuthInterceptor will attach it automatically.
        final meResult = await _authRepository.getMe();

        await meResult.fold(
          (failure) async {
            // /me failed but we have a valid token — emit a partial user so
            // the router can proceed; the profile will re-fetch on next open.
            emit(
              AuthAuthenticated(
                UserModel(
                  id: '',
                  name: '',
                  email: event.email,
                  role: UserRole.fromString(authResponse.role),
                  businessId: authResponse.businessId,
                  isActive: true,
                  createdAt: _epoch,
                  updatedAt: _epoch,
                ),
              ),
            );
          },
          (user) async {
            // 4. Persist the resolved user identifiers.
            await _secureStorage.saveUserInfo(
              userId: user.id,
              role: user.role.value,
              businessId: user.businessId ?? '',
            );
            emit(AuthAuthenticated(user));
          },
        );
      },
    );
  }

  // ── Biometric login ────────────────────────────────────────────────────────

  Future<void> _onBiometricLoginRequested(
    BiometricLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    // 1. Trigger OS biometric prompt.
    final authenticated = await _biometricService.authenticate();
    if (!authenticated) {
      // User cancelled or biometric failed — stay on login screen silently.
      return;
    }

    emit(const AuthLoading());

    // 2. Use the stored refresh token to obtain a new access token without
    //    requiring the user to re-enter their password.
    final storedRefreshToken = await _secureStorage.getRefreshToken();
    if (storedRefreshToken == null) {
      emit(const AuthError(
        'Session expired. Please sign in with your password.',
      ));
      return;
    }

    final refreshResult =
        await _authRepository.refreshTokens(storedRefreshToken);

    await refreshResult.fold(
      (failure) async => emit(AuthError(failure.message)),
      (authResponse) async {
        await _secureStorage.saveTokens(
          accessToken: authResponse.accessToken,
          refreshToken: authResponse.refreshToken,
        );

        final meResult = await _authRepository.getMe();
        await meResult.fold(
          (failure) async => emit(AuthError(failure.message)),
          (user) async {
            await _secureStorage.saveUserInfo(
              userId: user.id,
              role: user.role.value,
              businessId: user.businessId ?? '',
            );
            emit(AuthAuthenticated(user));
          },
        );
      },
    );
  }

  // ── Shared handlers ────────────────────────────────────────────────────────

  void _onUserLoaded(AuthUserLoaded event, Emitter<AuthState> emit) =>
      emit(AuthAuthenticated(event.user));

  Future<void> _onSignOutRequested(
    AuthSignOutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _secureStorage.clearAll();
    emit(const AuthUnauthenticated());
  }

  void _onTokenRefreshed(AuthTokenRefreshed event, Emitter<AuthState> emit) =>
      emit(AuthAuthenticated(event.user));

  Future<void> _onForcedLogout(
    _AuthForcedLogout event,
    Emitter<AuthState> emit,
  ) async {
    // Tokens already cleared by RefreshInterceptor before this event fires.
    emit(const AuthUnauthenticated());
  }

  @override
  Future<void> close() {
    _busSubscription.cancel();
    return super.close();
  }
}

/// Internal event — fired only by [AuthEventBus], never from UI code.
final class _AuthForcedLogout extends AuthEvent {
  const _AuthForcedLogout(this.reason);

  final String reason;

  @override
  List<Object?> get props => [reason];
}
