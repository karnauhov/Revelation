import 'package:revelation/core/errors/app_failure.dart';

sealed class AppResult<T> {
  const AppResult();

  bool get isSuccess => this is AppSuccess<T>;

  bool get isFailure => this is AppFailureResult<T>;

  R when<R>({
    required R Function(T data) success,
    required R Function(AppFailure failure) failure,
  }) {
    final self = this;
    if (self is AppSuccess<T>) {
      return success(self.data);
    }
    return failure((self as AppFailureResult<T>).error);
  }
}

final class AppSuccess<T> extends AppResult<T> {
  const AppSuccess(this.data);

  final T data;
}

final class AppFailureResult<T> extends AppResult<T> {
  const AppFailureResult(this.error);

  final AppFailure error;
}
