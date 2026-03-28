import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/core/errors/app_failure.dart';

class AppStartupState {
  const AppStartupState({
    required this.step,
    required this.appVersion,
    required this.buildNumber,
    required this.localeCode,
    required this.isLoading,
    required this.isReady,
    this.failure,
  });

  factory AppStartupState.initial({required String localeCode}) {
    return AppStartupState(
      step: AppBootstrapStep.preparing,
      appVersion: '',
      buildNumber: '',
      localeCode: localeCode,
      isLoading: true,
      isReady: false,
    );
  }

  final AppBootstrapStep step;
  final String appVersion;
  final String buildNumber;
  final String localeCode;
  final bool isLoading;
  final bool isReady;
  final AppFailure? failure;

  double get progressValue => step.progressValue;

  int get stepNumber => step.stepNumber;

  AppStartupState copyWith({
    AppBootstrapStep? step,
    String? appVersion,
    String? buildNumber,
    String? localeCode,
    bool? isLoading,
    bool? isReady,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return AppStartupState(
      step: step ?? this.step,
      appVersion: appVersion ?? this.appVersion,
      buildNumber: buildNumber ?? this.buildNumber,
      localeCode: localeCode ?? this.localeCode,
      isLoading: isLoading ?? this.isLoading,
      isReady: isReady ?? this.isReady,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AppStartupState &&
            runtimeType == other.runtimeType &&
            step == other.step &&
            appVersion == other.appVersion &&
            buildNumber == other.buildNumber &&
            localeCode == other.localeCode &&
            isLoading == other.isLoading &&
            isReady == other.isReady &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    step,
    appVersion,
    buildNumber,
    localeCode,
    isLoading,
    isReady,
    failure,
  );
}
