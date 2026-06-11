import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
// import '../errors/exceptions.dart';
import '../storage/secure_storage.dart';
import 'interceptors/auth_interceptor.dart';
import 'interceptors/refresh_interceptor.dart';
import 'interceptors/error_interceptor.dart';

class ApiClient {
  ApiClient._({required Dio dio}) : _dio = dio;

  static ApiClient? _instance;
  final Dio _dio;

  static ApiClient get instance {
    assert(_instance != null, 'Call ApiClient.init() in main.dart first');
    return _instance!;
  }

  /// Call once in [main.dart] during bootstrap.
  static Future<void> init(AppSecureStorage secureStorage) async {
    final baseUrl =
        '${dotenv.env['BASE_URL'] ?? 'http://localhost:8000'}'
        '${dotenv.env['API_VERSION'] ?? '/api/v1'}';

    final dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    // Interceptors run in order — auth must be before error
    dio.interceptors.addAll([
      AuthInterceptor(secureStorage),
      RefreshInterceptor(secureStorage, dio),
      ErrorInterceptor(),
      if (kDebugMode)
        PrettyDioLogger(
          requestHeader: false,
          requestBody: true,
          responseBody: true,
          error: true,
          compact: true,
        ),
    ]);

    _instance = ApiClient._(dio: dio);
  }

  // ── HTTP helpers ─────────────────────────────────────

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) =>
      _dio.get<T>(path, queryParameters: queryParameters);

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) =>
      _dio.post<T>(path, data: data, queryParameters: queryParameters);

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
  }) =>
      _dio.put<T>(path, data: data);

  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
  }) =>
      _dio.patch<T>(path, data: data);

  Future<Response<T>> delete<T>(String path) => _dio.delete<T>(path);
}
