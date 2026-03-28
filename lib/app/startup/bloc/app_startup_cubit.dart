import 'dart:async';
import 'dart:ui';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/shared/config/app_constants.dart';
import 'package:talker_flutter/talker_flutter.dart';

typedef AppBootstrapFactory = AppBootstrap Function(Talker talker);
typedef StartupSettingsCubitLoader =
    Future<SettingsCubit> Function(Talker talker);

class AppStartupCubit extends Cubit<AppStartupState> {
  AppStartupCubit({
    required Talker talker,
    AppBootstrapFactory? appBootstrapFactory,
    StartupSettingsCubitLoader? initializeSettingsCubit,
    Future<PackageInfo> Function()? packageInfoLoader,
    String? initialLocaleCode,
    bool autoStart = true,
  }) : _talker = talker,
       _appBootstrapFactory =
           appBootstrapFactory ??
           ((resolvedTalker) => AppBootstrap(talker: resolvedTalker)),
       _initializeSettingsCubit = initializeSettingsCubit,
       _packageInfoLoader = packageInfoLoader ?? PackageInfo.fromPlatform,
       super(
         AppStartupState.initial(
           localeCode: _normalizeLanguageCode(
             initialLocaleCode ??
                 PlatformDispatcher.instance.locale.languageCode,
           ),
         ),
       ) {
    if (autoStart) {
      unawaited(start());
    }
  }

  final Talker _talker;
  final AppBootstrapFactory _appBootstrapFactory;
  final StartupSettingsCubitLoader? _initializeSettingsCubit;
  final Future<PackageInfo> Function() _packageInfoLoader;

  bool _isStarting = false;
  SettingsCubit? _initializedSettingsCubit;

  SettingsCubit? get initializedSettingsCubit => _initializedSettingsCubit;

  Future<void> start() async {
    if (_isStarting || state.isReady) {
      return;
    }

    _isStarting = true;
    emit(
      state.copyWith(
        step: AppBootstrapStep.preparing,
        isLoading: true,
        isReady: false,
        clearFailure: true,
      ),
    );
    unawaited(_loadPackageInfo());

    try {
      final settingsCubit = await _initializeApp();
      if (isClosed) {
        if (!settingsCubit.isClosed) {
          await settingsCubit.close();
        }
        return;
      }

      _initializedSettingsCubit = settingsCubit;
      emit(
        state.copyWith(
          step: AppBootstrapStep.ready,
          localeCode: _normalizeLanguageCode(
            settingsCubit.state.settings.selectedLanguage,
          ),
          isLoading: false,
          isReady: true,
          clearFailure: true,
        ),
      );
    } catch (error, stackTrace) {
      _talker.handle(
        error,
        stackTrace,
        'Failed to initialize app startup flow',
      );
      if (isClosed) {
        return;
      }

      emit(
        state.copyWith(
          isLoading: false,
          isReady: false,
          failure: error is AppFailure
              ? error
              : AppFailure.dataSource(
                  'Unable to initialize the app.',
                  cause: error,
                  stackTrace: stackTrace,
                ),
        ),
      );
    } finally {
      _isStarting = false;
    }
  }

  Future<void> retry() async {
    await start();
  }

  Future<void> _loadPackageInfo() async {
    try {
      final packageInfo = await _packageInfoLoader();
      if (isClosed) {
        return;
      }
      emit(
        state.copyWith(
          appVersion: packageInfo.version,
          buildNumber: packageInfo.buildNumber,
        ),
      );
    } catch (error, stackTrace) {
      _talker.handle(
        error,
        stackTrace,
        'Failed to resolve startup app version',
      );
    }
  }

  Future<SettingsCubit> _initializeApp() async {
    final initializeSettingsCubit = _initializeSettingsCubit;
    if (initializeSettingsCubit != null) {
      _applyProgress(
        const AppBootstrapProgress(AppBootstrapStep.loadingSettings),
      );
      return initializeSettingsCubit(_talker);
    }

    return _appBootstrapFactory(_talker).initialize(onProgress: _applyProgress);
  }

  void _applyProgress(AppBootstrapProgress progress) {
    if (isClosed) {
      return;
    }
    emit(
      state.copyWith(
        step: progress.step,
        localeCode: _normalizeLanguageCode(
          progress.selectedLanguageCode ?? state.localeCode,
        ),
      ),
    );
  }

  static String _normalizeLanguageCode(String? languageCode) {
    final normalized = (languageCode ?? 'en').trim().toLowerCase();
    if (AppConstants.languages.containsKey(normalized)) {
      return normalized;
    }
    return 'en';
  }

  @override
  Future<void> close() async {
    final settingsCubit = _initializedSettingsCubit;
    if (settingsCubit != null && !settingsCubit.isClosed) {
      await settingsCubit.close();
    }
    return super.close();
  }
}
