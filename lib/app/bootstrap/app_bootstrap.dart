import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:revelation/common_widgets/strong_dictionary_dialog.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/viewmodels/settings_view_model.dart';
import 'package:revelation/managers/db_manager.dart';
import 'package:revelation/managers/server_manager.dart';
import 'package:revelation/utils/app_link_handler.dart';
import 'package:revelation/utils/common.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:window_manager/window_manager.dart';

class AppBootstrap {
  AppBootstrap({required Talker talker}) : _talker = talker;

  final Talker _talker;

  Future<SettingsViewModel> initialize() async {
    WidgetsFlutterBinding.ensureInitialized();
    _configureGlobalErrorHandling();
    await _initializePlatform();

    final settingsViewModel = SettingsViewModel(SettingsRepository());
    await settingsViewModel.loadSettings();

    await ServerManager().init();
    await _initializeDatabases(settingsViewModel);
    _configureStrongHandlers();

    return settingsViewModel;
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

    await windowManager.ensureInitialized();
    const windowOptions = WindowOptions(
      size: Size(800, 650),
      minimumSize: Size(800, 650),
      center: true,
    );
    windowManager.waitUntilReadyToShow(windowOptions, () async {
      await windowManager.setIcon('assets/images/UI/app_icon.png');
      await windowManager.show();
      await windowManager.focus();
    });
  }

  Future<void> _initializeDatabases(SettingsViewModel settingsViewModel) async {
    try {
      await DBManager().init(settingsViewModel.settings.selectedLanguage);
      settingsViewModel.addListener(() {
        DBManager().updateLanguage(settingsViewModel.settings.selectedLanguage);
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
