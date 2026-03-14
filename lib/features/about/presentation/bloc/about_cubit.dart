import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';

class AboutCubit extends Cubit<AboutState> {
  AboutCubit({
    Future<PackageInfo> Function()? packageInfoLoader,
    Future<String> Function()? changelogLoader,
    bool autoLoad = true,
  }) : _packageInfoLoader = packageInfoLoader ?? PackageInfo.fromPlatform,
       _changelogLoader = changelogLoader ?? _loadChangelogFromBundle,
       super(AboutState.initial()) {
    if (autoLoad) {
      load();
    }
  }

  final Future<PackageInfo> Function() _packageInfoLoader;
  final Future<String> Function() _changelogLoader;

  Future<void> load() async {
    emit(state.copyWith(isLoading: true, clearFailure: true));
    try {
      final packageInfo = await _packageInfoLoader();
      final changelog = await _changelogLoader();
      emit(
        state.copyWith(
          appVersion: packageInfo.version,
          buildNumber: packageInfo.buildNumber,
          changelog: changelog,
          isLoading: false,
          clearFailure: true,
        ),
      );
    } catch (error, stackTrace) {
      emit(
        state.copyWith(
          isLoading: false,
          failure: AppFailure.dataSource(
            'Unable to load about screen data.',
            cause: error,
            stackTrace: stackTrace,
          ),
        ),
      );
    }
  }

  void setChangelogExpanded(bool expanded) {
    emit(state.copyWith(isChangelogExpanded: expanded));
  }

  void setAcknowledgementsExpanded(bool expanded) {
    emit(state.copyWith(isAcknowledgementsExpanded: expanded));
  }

  void setRecommendedExpanded(bool expanded) {
    emit(state.copyWith(isRecommendedExpanded: expanded));
  }

  static Future<String> _loadChangelogFromBundle() async {
    try {
      return await rootBundle.loadString('CHANGELOG.md');
    } catch (_) {
      return 'No changelog available.';
    }
  }
}
