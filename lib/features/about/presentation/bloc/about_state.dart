import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

class AboutState {
  static const Object _unset = Object();

  const AboutState({
    required this.appVersion,
    required this.buildNumber,
    required this.appBuildTimestamp,
    required this.changelog,
    required this.isLoading,
    required this.isChangelogExpanded,
    required this.isAcknowledgementsExpanded,
    required this.isRecommendedExpanded,
    this.commonDbVersionInfo,
    this.localizedDbVersionInfo,
    this.failure,
  });

  factory AboutState.initial() {
    return const AboutState(
      appVersion: '',
      buildNumber: '',
      appBuildTimestamp: null,
      changelog: '',
      isLoading: true,
      isChangelogExpanded: false,
      isAcknowledgementsExpanded: false,
      isRecommendedExpanded: false,
      commonDbVersionInfo: null,
      localizedDbVersionInfo: null,
    );
  }

  final String appVersion;
  final String buildNumber;
  final DateTime? appBuildTimestamp;
  final String changelog;
  final bool isLoading;
  final bool isChangelogExpanded;
  final bool isAcknowledgementsExpanded;
  final bool isRecommendedExpanded;
  final DatabaseVersionInfo? commonDbVersionInfo;
  final DatabaseVersionInfo? localizedDbVersionInfo;
  final AppFailure? failure;

  AboutState copyWith({
    String? appVersion,
    String? buildNumber,
    Object? appBuildTimestamp = _unset,
    String? changelog,
    bool? isLoading,
    bool? isChangelogExpanded,
    bool? isAcknowledgementsExpanded,
    bool? isRecommendedExpanded,
    Object? commonDbVersionInfo = _unset,
    Object? localizedDbVersionInfo = _unset,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return AboutState(
      appVersion: appVersion ?? this.appVersion,
      buildNumber: buildNumber ?? this.buildNumber,
      appBuildTimestamp: identical(appBuildTimestamp, _unset)
          ? this.appBuildTimestamp
          : appBuildTimestamp as DateTime?,
      changelog: changelog ?? this.changelog,
      isLoading: isLoading ?? this.isLoading,
      isChangelogExpanded: isChangelogExpanded ?? this.isChangelogExpanded,
      isAcknowledgementsExpanded:
          isAcknowledgementsExpanded ?? this.isAcknowledgementsExpanded,
      isRecommendedExpanded:
          isRecommendedExpanded ?? this.isRecommendedExpanded,
      commonDbVersionInfo: identical(commonDbVersionInfo, _unset)
          ? this.commonDbVersionInfo
          : commonDbVersionInfo as DatabaseVersionInfo?,
      localizedDbVersionInfo: identical(localizedDbVersionInfo, _unset)
          ? this.localizedDbVersionInfo
          : localizedDbVersionInfo as DatabaseVersionInfo?,
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
            appBuildTimestamp == other.appBuildTimestamp &&
            changelog == other.changelog &&
            isLoading == other.isLoading &&
            isChangelogExpanded == other.isChangelogExpanded &&
            isAcknowledgementsExpanded == other.isAcknowledgementsExpanded &&
            isRecommendedExpanded == other.isRecommendedExpanded &&
            commonDbVersionInfo == other.commonDbVersionInfo &&
            localizedDbVersionInfo == other.localizedDbVersionInfo &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    appVersion,
    buildNumber,
    appBuildTimestamp,
    changelog,
    isLoading,
    isChangelogExpanded,
    isAcknowledgementsExpanded,
    isRecommendedExpanded,
    commonDbVersionInfo,
    localizedDbVersionInfo,
    failure,
  );
}
