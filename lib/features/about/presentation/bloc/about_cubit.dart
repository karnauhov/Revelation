import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';

class AboutCubit extends Cubit<AboutState> {
  AboutCubit() : super(AboutState.initial()) {
    load();
  }

  Future<void> load() async {
    emit(state.copyWith(isLoading: true, clearFailure: true));
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      final changelog = await _loadChangelog();
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

  Future<String> _loadChangelog() async {
    try {
      return await rootBundle.loadString('CHANGELOG.md');
    } catch (_) {
      return 'No changelog available.';
    }
  }
}
