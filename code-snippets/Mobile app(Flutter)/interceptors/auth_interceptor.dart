import 'package:dio/dio.dart';
import '../../storage/secure_storage.dart';

/// Attaches the JWT access token to every outgoing request.
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._secureStorage);

  final AppSecureStorage _secureStorage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _secureStorage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}
