import 'package:dio/dio.dart';
import '../../errors/exceptions.dart';

/// Maps all HTTP error responses and network failures to typed exceptions.
/// These are caught in repositories and converted to [Failure] objects.
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.type) {
      case DioExceptionType.connectionError:
      case DioExceptionType.unknown:
        return handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: const NetworkException(),
            type: err.type,
          ),
        );

      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: const NetworkException(
              'Connection timed out. Check your internet and retry.',
            ),
            type: err.type,
          ),
        );

      case DioExceptionType.badResponse:
        final statusCode = err.response?.statusCode ?? 0;
        final data = err.response?.data;
        final errorCode = _extractErrorCode(data);
        final message = _extractMessage(data, statusCode);

        // 401 — auth failure (handled by RefreshInterceptor first, but catches edge cases)
        if (statusCode == 401) {
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: AuthException(message),
              response: err.response,
              type: err.type,
            ),
          );
        }

        // 403 with subscription code
        if (statusCode == 403 && errorCode == 'SUBSCRIPTION_EXPIRED') {
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: SubscriptionException(message: message),
              response: err.response,
              type: err.type,
            ),
          );
        }

        // 403 — general permission denied
        if (statusCode == 403) {
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: PermissionException(message),
              response: err.response,
              type: err.type,
            ),
          );
        }

        // 202 — pending approval (stock adjust)
        if (statusCode == 202) {
          final transactionId = data?['transaction_id'] as String?;
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: PendingApprovalException(
                message: message,
                transactionId: transactionId,
              ),
              response: err.response,
              type: err.type,
            ),
          );
        }

        // All other HTTP errors
        return handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: ServerException(
              message: message,
              statusCode: statusCode,
              errorCode: errorCode,
            ),
            response: err.response,
            type: err.type,
          ),
        );

      default:
        handler.next(err);
    }
  }

  String _extractErrorCode(dynamic data) {
    if (data is Map<String, dynamic>) {
      return (data['error']?['code'] as String?) ?? '';
    }
    return '';
  }

  String _extractMessage(dynamic data, int statusCode) {
    if (data is Map<String, dynamic>) {
      return (data['error']?['message'] as String?) ??
          (data['detail'] as String?) ??
          _defaultMessage(statusCode);
    }
    return _defaultMessage(statusCode);
  }

  String _defaultMessage(int statusCode) {
    switch (statusCode) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Your session has expired. Please sign in again.';
      case 403:
        return "You don't have permission to perform this action.";
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'A conflict occurred. The resource may already exist.';
      case 422:
        return 'Validation error. Please check your input.';
      case 500:
      default:
        return 'Server error. Please try again later.';
    }
  }
}
