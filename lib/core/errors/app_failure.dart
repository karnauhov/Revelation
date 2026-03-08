enum AppFailureType { validation, notFound, dataSource, unknown }

class AppFailure implements Exception {
  const AppFailure({
    required this.type,
    required this.message,
    this.cause,
    this.stackTrace,
  });

  final AppFailureType type;
  final String message;
  final Object? cause;
  final StackTrace? stackTrace;

  const AppFailure.validation(
    String message, {
    Object? cause,
    StackTrace? stackTrace,
  }) : this(
         type: AppFailureType.validation,
         message: message,
         cause: cause,
         stackTrace: stackTrace,
       );

  const AppFailure.notFound(
    String message, {
    Object? cause,
    StackTrace? stackTrace,
  }) : this(
         type: AppFailureType.notFound,
         message: message,
         cause: cause,
         stackTrace: stackTrace,
       );

  const AppFailure.dataSource(
    String message, {
    Object? cause,
    StackTrace? stackTrace,
  }) : this(
         type: AppFailureType.dataSource,
         message: message,
         cause: cause,
         stackTrace: stackTrace,
       );

  const AppFailure.unknown(
    String message, {
    Object? cause,
    StackTrace? stackTrace,
  }) : this(
         type: AppFailureType.unknown,
         message: message,
         cause: cause,
         stackTrace: stackTrace,
       );

  @override
  String toString() {
    return 'AppFailure(type: $type, message: $message, cause: $cause)';
  }
}
