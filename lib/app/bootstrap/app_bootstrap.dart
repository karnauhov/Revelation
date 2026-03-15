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

  Future<SettingsCubit> initialize() async {
    WidgetsFlutterBinding.ensureInitialized();
    _configureGlobalErrorHandling();
    await _initializePlatform();

    final settingsCubit = SettingsCubit(SettingsRepository());
    await settingsCubit.loadSettings();

    await ServerManager().init();
    await _initializeDatabases(settingsCubit);
    _configureStrongHandlers();

    return settingsCubit;
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
