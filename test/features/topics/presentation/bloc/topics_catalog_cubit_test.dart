import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test('constructor loads topics and icons for active language', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final repository = _FakeTopicsRepository(
      topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
        'en': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic EN',
            idIcon: 'icon-en',
            description: 'Description EN',
            route: 'en-route',
          ),
        ]),
      },
      iconByKey: <String, AppResult<CommonResource?>>{
        'icon-en': AppSuccess<CommonResource?>(_buildSvgResource('icon-en')),
      },
    );
    final cubit = TopicsCatalogCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);

    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNull);
    expect(cubit.state.language, 'en');
    expect(cubit.state.topics, hasLength(1));
    expect(cubit.state.topics.single.route, 'en-route');
    expect(cubit.state.iconByKey['icon-en'], isNotNull);
    expect(repository.requestedLanguages, <String>['en']);
    expect(repository.requestedIconKeys, <String>['icon-en']);
  });

  test('loadForLanguage emits validation failure for empty language', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final cubit = TopicsCatalogCubit(
      topicsRepository: _FakeTopicsRepository(
        topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
          'en': const AppSuccess<List<TopicInfo>>(<TopicInfo>[]),
        },
      ),
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);
    await _flushAsync();

    await cubit.loadForLanguage('  ');

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNotNull);
    expect(cubit.state.failure!.type, AppFailureType.validation);
    expect(cubit.state.failure!.message, 'Language must not be empty.');
  });

  test('reacts to language changes from SettingsCubit', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final repository = _FakeTopicsRepository(
      topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
        'en': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic EN',
            idIcon: '',
            description: 'Description EN',
            route: 'en-route',
          ),
        ]),
        'ru': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic RU',
            idIcon: '',
            description: 'Description RU',
            route: 'ru-route',
          ),
        ]),
      },
    );
    final cubit = TopicsCatalogCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);
    await _flushAsync();

    await settingsCubit.changeLanguage('ru');
    await _flushAsync();

    expect(cubit.state.failure, isNull);
    expect(cubit.state.language, 'ru');
    expect(cubit.state.topics, hasLength(1));
    expect(cubit.state.topics.single.route, 'ru-route');
    expect(repository.requestedLanguages, contains('en'));
    expect(repository.requestedLanguages.last, 'ru');
  });

  test('loads failure state when repository returns failure result', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final cubit = TopicsCatalogCubit(
      topicsRepository: _FakeTopicsRepository(
        topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
          'en': const AppFailureResult<List<TopicInfo>>(
            AppFailure.dataSource('forced topics failure'),
          ),
        },
      ),
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);

    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNotNull);
    expect(cubit.state.failure!.type, AppFailureType.dataSource);
    expect(cubit.state.failure!.message, 'forced topics failure');
  });
}

Future<void> _flushAsync() async {
  await Future<void>.delayed(Duration.zero);
  await Future<void>.delayed(Duration.zero);
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

CommonResource _buildSvgResource(String key) {
  return CommonResource(
    key: key,
    fileName: '$key.svg',
    mimeType: 'image/svg+xml',
    data: Uint8List.fromList(
      utf8.encode(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>',
      ),
    ),
  );
}

class _FakeSettingsRepository extends SettingsRepository {
  _FakeSettingsRepository({required this.initialSettings});

  AppSettings initialSettings;

  @override
  Future<AppSettings> getSettings() async => initialSettings;

  @override
  Future<void> saveSettings(AppSettings settings) async {
    initialSettings = settings;
  }
}

class _FakeTopicsRepository extends TopicsRepository {
  _FakeTopicsRepository({
    required this.topicsByLanguage,
    this.iconByKey = const <String, AppResult<CommonResource?>>{},
  }) : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<List<TopicInfo>>> topicsByLanguage;
  final Map<String, AppResult<CommonResource?>> iconByKey;
  final List<String> requestedLanguages = <String>[];
  final List<String> requestedIconKeys = <String>[];

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    requestedLanguages.add(language);
    return topicsByLanguage[language] ??
        const AppFailureResult<List<TopicInfo>>(
          AppFailure.notFound('No fake topics for requested language.'),
        );
  }

  @override
  Future<AppResult<CommonResource?>> getCommonResource(String key) async {
    requestedIconKeys.add(key);
    return iconByKey[key] ?? const AppSuccess<CommonResource?>(null);
  }
}

class _NoopTopicsDataSource implements TopicsDataSource {
  @override
  Future<void> updateLanguage(String language) async {}

  @override
  Future<List<Article>> fetchArticles({bool onlyVisible = true}) async =>
      const <Article>[];

  @override
  Future<String> fetchArticleMarkdown(String route) async => '';

  @override
  Future<Article?> fetchArticleByRoute(String route) async => null;

  @override
  Future<CommonResource?> fetchCommonResource(String key) async => null;
}
