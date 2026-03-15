import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test('loadSettings updates state from repository result', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(
        language: 'en',
        theme: 'midnight',
        fontSize: 'large',
        soundEnabled: false,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNull);
    expect(cubit.state.settings.selectedLanguage, 'en');
    expect(cubit.state.settings.selectedTheme, 'midnight');
    expect(cubit.state.settings.selectedFontSize, 'large');
    expect(cubit.state.settings.soundEnabled, isFalse);
  });

  test('changeLanguage persists updated language', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en'),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();
    await cubit.changeLanguage('ru');

    expect(cubit.state.failure, isNull);
    expect(cubit.state.settings.selectedLanguage, 'ru');
    expect(repository.savedSettings, hasLength(1));
    expect(repository.savedSettings.single.selectedLanguage, 'ru');
  });

  test('loadSettings emits data-source failure on repository throw', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en'),
      throwOnLoad: true,
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();

    expect(cubit.state.isLoading, isFalse);
    expect(
      cubit.state.failure,
      const AppFailure.dataSource('Unable to load app settings.'),
    );
  });

  test('changeTheme keeps optimistic state and reports save failure', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en', theme: 'manuscript'),
      throwOnSave: true,
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();
    await cubit.changeTheme('midnight');

    expect(cubit.state.settings.selectedTheme, 'midnight');
    expect(
      cubit.state.failure,
      const AppFailure.dataSource('Unable to persist app settings.'),
    );
    expect(repository.savedSettings, isEmpty);
  });

  test(
    'loadSettings returns safely when cubit closes before load completes',
    () async {
      final loadCompleter = Completer<AppSettings>();
      final repository = _FakeSettingsRepository(
        initialSettings: _buildSettings(language: 'en'),
        loadCompleter: loadCompleter,
      );
      final cubit = SettingsCubit(repository);

      final loadFuture = cubit.loadSettings();
      await Future<void>.delayed(Duration.zero);
      await cubit.close();

      loadCompleter.complete(_buildSettings(language: 'ru'));
      await loadFuture;

      expect(cubit.isClosed, isTrue);
    },
  );

  test(
    'changeTheme returns safely when cubit closes before save fails',
    () async {
      final saveCompleter = Completer<void>();
      final repository = _FakeSettingsRepository(
        initialSettings: _buildSettings(language: 'en'),
        saveCompleter: saveCompleter,
      );
      final cubit = SettingsCubit(repository);
      addTearDown(() async {
        if (!cubit.isClosed) {
          await cubit.close();
        }
      });
      await cubit.loadSettings();

      final changeFuture = cubit.changeTheme('midnight');
      await Future<void>.delayed(Duration.zero);
      await cubit.close();

      saveCompleter.completeError(StateError('forced delayed save failure'));
      await changeFuture;

      expect(cubit.isClosed, isTrue);
    },
  );
}

AppSettings _buildSettings({
  required String language,
  String theme = 'manuscript',
  String fontSize = 'medium',
  bool soundEnabled = true,
}) {
  return AppSettings(
    selectedLanguage: language,
    selectedTheme: theme,
    selectedFontSize: fontSize,
    soundEnabled: soundEnabled,
  );
}

class _FakeSettingsRepository extends SettingsRepository {
  _FakeSettingsRepository({
    required this.initialSettings,
    this.throwOnLoad = false,
    this.throwOnSave = false,
    this.loadCompleter,
    this.saveCompleter,
  });

  AppSettings initialSettings;
  final bool throwOnLoad;
  final bool throwOnSave;
  final Completer<AppSettings>? loadCompleter;
  final Completer<void>? saveCompleter;
  final List<AppSettings> savedSettings = <AppSettings>[];

  @override
  Future<AppSettings> getSettings() async {
    if (loadCompleter != null) {
      return loadCompleter!.future;
    }
    if (throwOnLoad) {
      throw StateError('forced load failure');
    }
    return initialSettings;
  }

  @override
  Future<void> saveSettings(AppSettings settings) async {
    if (saveCompleter != null) {
      await saveCompleter!.future;
      initialSettings = settings;
      savedSettings.add(settings);
      return;
    }
    if (throwOnSave) {
      throw StateError('forced save failure');
    }
    initialSettings = settings;
    savedSettings.add(settings);
  }
}
