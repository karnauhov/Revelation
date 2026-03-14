import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:revelation/features/primary_sources/presentation/detail/strong_dictionary_dialog.dart';
import 'package:revelation/features/settings/settings.dart'
    show SettingsCubit, SettingsRepository;
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';

class AppBootstrap {
  AppBootstrap({required Talker talker, DatabaseRuntime? databaseRuntime})
    : _talker = talker,
      _databaseRuntime = databaseRuntime ?? DbManagerDatabaseRuntime();

  final Talker _talker;
  final DatabaseRuntime _databaseRuntime;
  StreamSubscription<String>? _languageSubscription;

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
      showStrongDictionaryDialog(context, strongNumber);
    });
    setDefaultGreekStrongPickerTapHandler((strongNumber, context) {
      showStrongDictionaryDialog(context, strongNumber);
    });
  }
}
