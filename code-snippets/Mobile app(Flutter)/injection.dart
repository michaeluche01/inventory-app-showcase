import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../network/api_client.dart';
import '../router/navigation_keys.dart';
import '../services/biometric_service.dart';
import '../storage/secure_storage.dart';
import '../../features/auth/data/repositories/auth_repository_impl.dart';
import '../../features/auth/data/repositories/password_reset_repository_impl.dart';
import '../../features/auth/domain/repositories/auth_repository.dart';
import '../../features/auth/domain/repositories/password_reset_repository.dart';
import '../../features/auth/presentation/bloc/password_reset_bloc.dart';
import '../../features/dashboard/data/repositories/dashboard_repository_impl.dart';
import '../../features/dashboard/domain/repositories/dashboard_repository.dart';
import '../../features/dashboard/presentation/bloc/dashboard_bloc.dart';
import '../../shared/blocs/auth/auth_bloc.dart';

final getIt = GetIt.instance;

/// Bootstrap all dependencies. Call once in [main] before [runApp].
///
/// Registration order:
///   1. Navigation keys
///   2. External SDK singletons (SharedPrefs, SecureStorage)
///   3. Network (ApiClient needs SecureStorage)
///   4. Services (BiometricService)
///   5. Repositories (need ApiClient)
///   6. Feature BLoCs/Cubits
Future<void> configureDependencies() async {
  // ── Navigation ───────────────────────────────────────────────────────────
  getIt.registerSingleton<NavigationKeys>(NavigationKeys.instance);

  // ── External ─────────────────────────────────────────────────────────────
  final sharedPrefs = await SharedPreferences.getInstance();
  getIt.registerSingleton<SharedPreferences>(sharedPrefs);

  const secureStorageInstance = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  // ── Storage ───────────────────────────────────────────────────────────────
  getIt.registerSingleton<AppSecureStorage>(
    AppSecureStorage(secureStorageInstance),
  );

  // ── Network ───────────────────────────────────────────────────────────────
  await ApiClient.init(getIt<AppSecureStorage>());
  getIt.registerSingleton<ApiClient>(ApiClient.instance);

  // ── Services ──────────────────────────────────────────────────────────────
  getIt.registerSingleton<BiometricService>(BiometricService());

  // ── Auth feature ──────────────────────────────────────────────────────────
  getIt.registerSingleton<AuthRepository>(
    AuthRepositoryImpl(getIt<ApiClient>()),
  );

  // AuthBloc singleton — survives route changes.
  // main.dart uses BlocProvider.value so GetIt owns the lifecycle.
  getIt.registerSingleton<AuthBloc>(
    AuthBloc(
      secureStorage: getIt<AppSecureStorage>(),
      authRepository: getIt<AuthRepository>(),
      biometricService: getIt<BiometricService>(),
    ),
  );

  // ── Password reset — factory (fresh per screen, in-memory token) ──────────
  getIt.registerFactory<PasswordResetRepository>(
    () => PasswordResetRepositoryImpl(getIt<ApiClient>()),
  );
  getIt.registerFactory<PasswordResetBloc>(
    () => PasswordResetBloc(repository: getIt<PasswordResetRepository>()),
  );

  // ── Dashboard feature ─────────────────────────────────────────────────────
  // Singleton — the dashboard persists across shell tab switches.
  // Prevents redundant fetches on every tab tap.
  getIt.registerSingleton<DashboardRepository>(
    DashboardRepositoryImpl(getIt<ApiClient>()),
  );
  getIt.registerSingleton<DashboardBloc>(
    DashboardBloc(repository: getIt<DashboardRepository>()),
  );

  // ── Future feature modules ────────────────────────────────────────────────
  // await _registerProductDependencies();
  // await _registerStockDependencies();
}