import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_dictionary_dialog.dart';
import 'package:revelation/features/settings/settings.dart'
    show SettingsCubit, SettingsRepository;
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';

typedef StrongDialogPresenter =
    void Function(BuildContext context, int strongNumber);
typedef PrimarySourceNavigator =
    void Function(BuildContext context, PrimarySourceRouteArgs routeArgs);
typedef AppBootstrapProgressCallback =
    void Function(AppBootstrapProgress progress);

const int appBootstrapVisibleStepCount = 5;

enum AppBootstrapStep {
  preparing,
  loadingSettings,
  initializingServer,
  initializingDatabases,
  configuringLinks,
  ready,
}

extension AppBootstrapStepX on AppBootstrapStep {
  int get stepNumber {
    switch (this) {
      case AppBootstrapStep.preparing:
        return 1;
      case AppBootstrapStep.loadingSettings:
        return 2;
      case AppBootstrapStep.initializingServer:
        return 3;
      case AppBootstrapStep.initializingDatabases:
        return 4;
      case AppBootstrapStep.configuringLinks:
      case AppBootstrapStep.ready:
        return 5;
    }
  }

  double get progressValue {
    switch (this) {
      case AppBootstrapStep.preparing:
        return 0.12;
      case AppBootstrapStep.loadingSettings:
        return 0.32;
      case AppBootstrapStep.initializingServer:
        return 0.52;
      case AppBootstrapStep.initializingDatabases:
        return 0.74;
      case AppBootstrapStep.configuringLinks:
        return 0.9;
      case AppBootstrapStep.ready:
        return 1;
    }
  }
}

class AppBootstrapProgress {
  const AppBootstrapProgress(this.step, {this.selectedLanguageCode});

  final AppBootstrapStep step;
  final String? selectedLanguageCode;
}

class AppBootstrap {
  AppBootstrap({
    required Talker talker,
    DatabaseRuntime? databaseRuntime,
    PrimarySourceReferenceService? referenceResolver,
    StrongDialogPresenter? showStrongDialog,
    PrimarySourceNavigator? navigateToPrimarySource,
  }) : _talker = talker,
       _databaseRuntime = databaseRuntime ?? DbManagerDatabaseRuntime(),
       _referenceResolver =
           referenceResolver ?? PrimarySourceReferenceService(),
       _showStrongDialog = showStrongDialog ?? _defaultShowStrongDialog,
       _navigateToPrimarySource =
           navigateToPrimarySource ?? _defaultNavigateToPrimarySource;

  final Talker _talker;
  final DatabaseRuntime _databaseRuntime;
  final PrimarySourceReferenceService _referenceResolver;
  final StrongDialogPresenter _showStrongDialog;
  final PrimarySourceNavigator _navigateToPrimarySource;
  StreamSubscription<String>? _languageSubscription;

  static void _defaultShowStrongDialog(BuildContext context, int strongNumber) {
    showStrongDictionaryDialog(context, strongNumber);
  }

  static void _defaultNavigateToPrimarySource(
    BuildContext context,
    PrimarySourceRouteArgs routeArgs,
  ) {
    context.push('/primary_source', extra: routeArgs);
  }

  Future<SettingsCubit> initialize({
    AppBootstrapProgressCallback? onProgress,
  }) async {
    SettingsCubit? settingsCubit;

    try {
      onProgress?.call(const AppBootstrapProgress(AppBootstrapStep.preparing));
      WidgetsFlutterBinding.ensureInitialized();
      _configureGlobalErrorHandling();
      await _initializePlatform();

      onProgress?.call(
        const AppBootstrapProgress(AppBootstrapStep.loadingSettings),
      );
      settingsCubit = SettingsCubit(SettingsRepository());
      await settingsCubit.loadSettings();
      final selectedLanguage = settingsCubit.state.settings.selectedLanguage;

      onProgress?.call(
        AppBootstrapProgress(
          AppBootstrapStep.initializingServer,
          selectedLanguageCode: selectedLanguage,
        ),
      );
      await ServerManager().init();

      onProgress?.call(
        AppBootstrapProgress(
          AppBootstrapStep.initializingDatabases,
          selectedLanguageCode: selectedLanguage,
        ),
      );
      await _initializeDatabases(settingsCubit);

      onProgress?.call(
        AppBootstrapProgress(
          AppBootstrapStep.configuringLinks,
          selectedLanguageCode: selectedLanguage,
        ),
      );
      _configureStrongHandlers();
      onProgress?.call(
        AppBootstrapProgress(
          AppBootstrapStep.ready,
          selectedLanguageCode: selectedLanguage,
        ),
      );

      return settingsCubit;
    } catch (_) {
      if (settingsCubit != null && !settingsCubit.isClosed) {
        await settingsCubit.close();
      }
      rethrow;
    }
  }

  void _configureGlobalErrorHandling() {
    FlutterError.onError = (FlutterErrorDetails details) {
      _talker.handle(
        details.exception,
        details.stack ?? StackTrace.current,
        'Flutter framework error',
      );
      FlutterError.presentError(details);
    };

    PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
      _talker.handle(error, stack, 'PlatformDispatcher uncaught error');
      return true;
    };
  }

  Future<void> _initializePlatform() async {
    if (isWeb()) {
      final userAgent = getUserAgent();
      final mobileBrowser = isMobileBrowser() ? ' (mobile browser)' : '';
      log.info("Started on web '$userAgent'$mobileBrowser");
    } else {
      log.info('Started on ${getPlatform()}');
    }

    if (!isDesktop()) {
      return;
    }
  }

  Future<void> _initializeDatabases(SettingsCubit settingsCubit) async {
    try {
      await _databaseRuntime.initialize(
        settingsCubit.state.settings.selectedLanguage,
      );
      await _languageSubscription?.cancel();
      _languageSubscription = settingsCubit.stream
          .map((state) => state.settings.selectedLanguage)
          .distinct()
          .listen((language) {
            unawaited(_databaseRuntime.updateLanguage(language));
          });
    } catch (error, stackTrace) {
      _talker.handle(error, stackTrace, 'Failed to initialize local databases');
    }
  }

  void _configureStrongHandlers() {
    setDefaultGreekStrongTapHandler((strongNumber, context) {
      _showStrongDialog(context, strongNumber);
    });
    setDefaultGreekStrongPickerTapHandler((strongNumber, context) {
      _showStrongDialog(context, strongNumber);
    });
    setDefaultWordTapHandler((sourceId, pageName, wordIndex, context) {
      final source = _referenceResolver.findSourceById(sourceId);
      if (source == null) {
        log.warning("Primary source '$sourceId' was not found for word link.");
        return;
      }

      if (pageName != null &&
          _referenceResolver.findPageByName(source, pageName) == null) {
        log.warning("Page '$pageName' was not found in source '$sourceId'.");
        return;
      }

      _navigateToPrimarySource(
        context,
        PrimarySourceRouteArgs(
          primarySource: source,
          pageName: pageName,
          wordIndex: wordIndex,
        ),
      );
    });
  }
}
