import 'package:revelation/core/errors/app_failure.dart';

class AboutState {
  static const Object _unset = Object();

  const AboutState({
    required this.appVersion,
    required this.buildNumber,
    required this.changelog,
    required this.isLoading,
    required this.isChangelogExpanded,
    required this.isAcknowledgementsExpanded,
    required this.isRecommendedExpanded,
    this.commonDbUpdatedAt,
    this.localizedDbUpdatedAt,
    this.failure,
  });

  factory AboutState.initial() {
    return const AboutState(
      appVersion: '',
      buildNumber: '',
      changelog: '',
      isLoading: true,
      isChangelogExpanded: false,
      isAcknowledgementsExpanded: false,
      isRecommendedExpanded: false,
      commonDbUpdatedAt: null,
      localizedDbUpdatedAt: null,
    );
  }

  final String appVersion;
  final String buildNumber;
  final String changelog;
  final bool isLoading;
  final bool isChangelogExpanded;
  final bool isAcknowledgementsExpanded;
  final bool isRecommendedExpanded;
  final DateTime? commonDbUpdatedAt;
  final DateTime? localizedDbUpdatedAt;
  final AppFailure? failure;

  AboutState copyWith({
    String? appVersion,
    String? buildNumber,
    String? changelog,
    bool? isLoading,
    bool? isChangelogExpanded,
    bool? isAcknowledgementsExpanded,
    bool? isRecommendedExpanded,
    Object? commonDbUpdatedAt = _unset,
    Object? localizedDbUpdatedAt = _unset,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return AboutState(
      appVersion: appVersion ?? this.appVersion,
      buildNumber: buildNumber ?? this.buildNumber,
      changelog: changelog ?? this.changelog,
      isLoading: isLoading ?? this.isLoading,
      isChangelogExpanded: isChangelogExpanded ?? this.isChangelogExpanded,
      isAcknowledgementsExpanded:
          isAcknowledgementsExpanded ?? this.isAcknowledgementsExpanded,
      isRecommendedExpanded:
          isRecommendedExpanded ?? this.isRecommendedExpanded,
      commonDbUpdatedAt: identical(commonDbUpdatedAt, _unset)
          ? this.commonDbUpdatedAt
          : commonDbUpdatedAt as DateTime?,
      localizedDbUpdatedAt: identical(localizedDbUpdatedAt, _unset)
          ? this.localizedDbUpdatedAt
          : localizedDbUpdatedAt as DateTime?,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AboutState &&
            runtimeType == other.runtimeType &&
            appVersion == other.appVersion &&
            buildNumber == other.buildNumber &&
            changelog == other.changelog &&
            isLoading == other.isLoading &&
            isChangelogExpanded == other.isChangelogExpanded &&
            isAcknowledgementsExpanded == other.isAcknowledgementsExpanded &&
            isRecommendedExpanded == other.isRecommendedExpanded &&
            commonDbUpdatedAt == other.commonDbUpdatedAt &&
            localizedDbUpdatedAt == other.localizedDbUpdatedAt &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    appVersion,
    buildNumber,
    changelog,
    isLoading,
    isChangelogExpanded,
    isAcknowledgementsExpanded,
    isRecommendedExpanded,
    commonDbUpdatedAt,
    localizedDbUpdatedAt,
    failure,
  );
}
