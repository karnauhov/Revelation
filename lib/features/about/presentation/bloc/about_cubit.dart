import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';
import 'package:revelation/infra/db/connectors/shared.dart';
import 'package:revelation/shared/config/app_constants.dart';

typedef DbLastUpdateLoader = Future<DateTime?> Function(String dbFile);

class AboutCubit extends Cubit<AboutState> {
  AboutCubit({
    Future<PackageInfo> Function()? packageInfoLoader,
    Future<String> Function()? changelogLoader,
    DbLastUpdateLoader? dbLastUpdateLoader,
    String? initialLanguageCode,
    bool autoLoad = true,
  }) : _packageInfoLoader = packageInfoLoader ?? PackageInfo.fromPlatform,
       _changelogLoader = changelogLoader ?? _loadChangelogFromBundle,
       _dbLastUpdateLoader = dbLastUpdateLoader ?? getLocalDatabaseUpdatedAt,
       _initialLanguageCode = _normalizeLanguageCode(initialLanguageCode),
       super(AboutState.initial()) {
    if (autoLoad) {
      load(languageCode: _initialLanguageCode);
    }
  }

  final Future<PackageInfo> Function() _packageInfoLoader;
  final Future<String> Function() _changelogLoader;
  final DbLastUpdateLoader _dbLastUpdateLoader;
  final String _initialLanguageCode;

  Future<void> load({String? languageCode}) async {
    emit(state.copyWith(isLoading: true, clearFailure: true));
    try {
      final normalizedLanguageCode = _resolveLanguageCode(languageCode);
      final packageInfo = await _packageInfoLoader();
      if (isClosed) {
        return;
      }
      final changelog = await _changelogLoader();
      if (isClosed) {
        return;
      }
      final dbUpdateInfo = await _loadDbUpdateInfo(normalizedLanguageCode);
      if (isClosed) {
        return;
      }
      emit(
        state.copyWith(
          appVersion: packageInfo.version,
          buildNumber: packageInfo.buildNumber,
          changelog: changelog,
          commonDbUpdatedAt: dbUpdateInfo.commonDbUpdatedAt,
          localizedDbUpdatedAt: dbUpdateInfo.localizedDbUpdatedAt,
          isLoading: false,
          clearFailure: true,
        ),
      );
    } catch (error, stackTrace) {
      if (isClosed) {
        return;
      }
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

  String _resolveLanguageCode(String? languageCode) {
    return _normalizeLanguageCode(languageCode ?? _initialLanguageCode);
  }

  Future<_DbUpdateInfo> _loadDbUpdateInfo(String languageCode) async {
    final localizedDbFile = AppConstants.localizedDB.replaceAll(
      '@loc',
      languageCode,
    );
    final timestamps = await Future.wait<DateTime?>([
      _safeLoadDbUpdatedAt(AppConstants.commonDB),
      _safeLoadDbUpdatedAt(localizedDbFile),
    ]);
    return _DbUpdateInfo(
      commonDbUpdatedAt: timestamps[0],
      localizedDbUpdatedAt: timestamps[1],
    );
  }

  Future<DateTime?> _safeLoadDbUpdatedAt(String dbFile) async {
    try {
      return await _dbLastUpdateLoader(
        dbFile,
      ).timeout(const Duration(milliseconds: 500), onTimeout: () => null);
    } catch (_) {
      return null;
    }
  }

  static String _normalizeLanguageCode(String? languageCode) {
    final normalized = (languageCode ?? 'en').toLowerCase();
    if (AppConstants.languages.containsKey(normalized)) {
      return normalized;
    }
    return 'en';
  }

  static Future<String> _loadChangelogFromBundle() async {
    try {
      return await rootBundle.loadString('CHANGELOG.md');
    } catch (_) {
      return 'No changelog available.';
    }
  }
}

class _DbUpdateInfo {
  const _DbUpdateInfo({
    required this.commonDbUpdatedAt,
    required this.localizedDbUpdatedAt,
  });

  final DateTime? commonDbUpdatedAt;
  final DateTime? localizedDbUpdatedAt;
}
