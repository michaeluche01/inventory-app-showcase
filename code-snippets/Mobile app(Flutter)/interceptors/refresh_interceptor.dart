import 'dart:async';

import 'package:dio/dio.dart';

import '../../constants/api_endpoints.dart';
import '../../storage/secure_storage.dart';
import '../auth_event_bus.dart';

/// On 401 responses, silently refreshes the access token and retries the
/// original request.
///
/// **Concurrent 401 handling (production-safe):**
/// If multiple in-flight requests all get a 401 simultaneously (e.g. user
/// opens app after a long idle), only ONE actual refresh call is made. Every
/// other failing request *awaits* the same [Completer] and then retries with
/// the new token — preventing thundering-herd refresh and race conditions.
///
/// On refresh failure, all queued requests fail, tokens are cleared, and a
/// [ForceLogoutEvent] is fired on [AuthEventBus] so [AuthBloc] redirects to
/// login without any coupling between the network and presentation layers.
class RefreshInterceptor extends Interceptor {
  RefreshInterceptor(this._secureStorage, this._dio);

  final AppSecureStorage _secureStorage;
  final Dio _dio;

  /// Non-null while a refresh request is in-flight.
  /// All concurrent 401s await this and share the refreshed token.
  Completer<String>? _refreshCompleter;

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final statusCode = err.response?.statusCode;
    final requestPath = err.requestOptions.path;

    // Only intercept 401s; skip the refresh endpoint itself to prevent loops.
    if (statusCode != 401 || requestPath.contains(ApiEndpoints.refresh)) {
      return handler.next(err);
    }

    // ── Piggyback on an in-flight refresh ──────────────────────────────────
    // If refresh is already running, wait for its result and retry immediately.
    if (_refreshCompleter != null) {
      try {
        final newToken = await _refreshCompleter!.future;
        handler.resolve(await _retry(err.requestOptions, newToken));
      } catch (_) {
        handler.next(err);
      }
      return;
    }

    // ── Initiate a new refresh ─────────────────────────────────────────────
    _refreshCompleter = Completer<String>();

    try {
      final refreshToken = await _secureStorage.getRefreshToken();
      if (refreshToken == null) throw Exception('No refresh token stored.');

      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.refresh,
        data: {'refresh_token': refreshToken},
      );

      final data = response.data;
      if (data == null) throw Exception('Empty refresh response.');

      final newAccessToken = data['access_token'] as String;
      final newRefreshToken = data['refresh_token'] as String? ?? refreshToken;

      await _secureStorage.saveTokens(
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
      );

      // Unblock all waiting requests.
      _refreshCompleter!.complete(newAccessToken);
      _refreshCompleter = null;

      handler.resolve(await _retry(err.requestOptions, newAccessToken));
    } catch (e) {
      _refreshCompleter?.completeError(e);
      _refreshCompleter = null;
      await _forceLogout('Token refresh failed.');
      handler.next(err);
    }
  }

  Future<Response<dynamic>> _retry(
    RequestOptions options,
    String newToken,
  ) {
    options.headers['Authorization'] = 'Bearer $newToken';
    return _dio.fetch(options);
  }

  Future<void> _forceLogout(String reason) async {
    await _secureStorage.clearAll();
    AuthEventBus.instance.fire(ForceLogoutEvent(reason));
  }
}