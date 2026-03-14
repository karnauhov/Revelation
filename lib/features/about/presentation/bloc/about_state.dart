import 'package:revelation/core/errors/app_failure.dart';

class AboutState {
  const AboutState({
    required this.appVersion,
    required this.buildNumber,
    required this.changelog,
    required this.isLoading,
    required this.isChangelogExpanded,
    required this.isAcknowledgementsExpanded,
    required this.isRecommendedExpanded,
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
    );
  }

  final String appVersion;
  final String buildNumber;
  final String changelog;
  final bool isLoading;
  final bool isChangelogExpanded;
  final bool isAcknowledgementsExpanded;
  final bool isRecommendedExpanded;
  final AppFailure? failure;

  AboutState copyWith({
    String? appVersion,
    String? buildNumber,
    String? changelog,
    bool? isLoading,
    bool? isChangelogExpanded,
    bool? isAcknowledgementsExpanded,
    bool? isRecommendedExpanded,
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
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }
}
