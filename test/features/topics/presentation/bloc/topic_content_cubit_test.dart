import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test(
    'loads markdown and resolves missing metadata from repository',
    () async {
      final settingsCubit = SettingsCubit(
        _FakeSettingsRepository(
          initialSettings: _buildSettings(language: 'en'),
        ),
      );
      addTearDown(settingsCubit.close);
      await settingsCubit.loadSettings();

      final repository = _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'intro|en': const AppSuccess<String>('# Intro markdown'),
        },
        topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
          'intro|en': AppSuccess<TopicInfo?>(
            TopicInfo(
              name: 'Resolved Name',
              idIcon: '',
              description: 'Resolved Description',
              route: 'intro',
            ),
          ),
        },
      );
      final cubit = TopicContentCubit(
        topicsRepository: repository,
        settingsCubit: settingsCubit,
        route: 'intro',
        name: '',
        description: '',
      );
      addTearDown(cubit.close);

      await _flushAsync();

      expect(cubit.state.isLoading, isFalse);
      expect(cubit.state.failure, isNull);
      expect(cubit.state.language, 'en');
      expect(cubit.state.markdown, '# Intro markdown');
      expect(cubit.state.name, 'Resolved Name');
      expect(cubit.state.description, 'Resolved Description');
      expect(repository.markdownRequests, <String>['intro|en']);
      expect(repository.topicByRouteRequests, <String>['intro|en']);
    },
  );

  test('keeps preset metadata and skips topic lookup', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final repository = _FakeTopicsRepository(
      markdownByRouteLanguage: <String, AppResult<String>>{
        'intro|en': const AppSuccess<String>('preset markdown'),
      },
      topicByRouteLanguage: const <String, AppResult<TopicInfo?>>{},
    );
    final cubit = TopicContentCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
      route: 'intro',
      name: 'Preset Name',
      description: 'Preset Description',
    );
    addTearDown(cubit.close);

    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNull);
    expect(cubit.state.name, 'Preset Name');
    expect(cubit.state.description, 'Preset Description');
    expect(cubit.state.markdown, 'preset markdown');
    expect(repository.topicByRouteRequests, isEmpty);
  });

  test('emits failure when markdown result is unsuccessful', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final cubit = TopicContentCubit(
      topicsRepository: _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'intro|en': const AppFailureResult<String>(
            AppFailure.dataSource('forced markdown failure'),
          ),
        },
        topicByRouteLanguage: const <String, AppResult<TopicInfo?>>{},
      ),
      settingsCubit: settingsCubit,
      route: 'intro',
    );
    addTearDown(cubit.close);

    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.markdown, isEmpty);
    expect(cubit.state.failure, isNotNull);
    expect(cubit.state.failure!.type, AppFailureType.dataSource);
    expect(cubit.state.failure!.message, 'forced markdown failure');
  });

  test(
    'loadCommonResource caches result and avoids duplicate requests',
    () async {
      final settingsCubit = SettingsCubit(
        _FakeSettingsRepository(
          initialSettings: _buildSettings(language: 'en'),
        ),
      );
      addTearDown(settingsCubit.close);
      await settingsCubit.loadSettings();

      final repository = _FakeTopicsRepository(
        markdownByRouteLanguage: const <String, AppResult<String>>{},
        topicByRouteLanguage: const <String, AppResult<TopicInfo?>>{},
        resourceByKey: <String, AppResult<TopicResource?>>{
          'icon': AppSuccess<TopicResource?>(
            TopicResource(
              fileName: 'icon.svg',
              mimeType: 'image/svg+xml',
              data: Uint8List(0),
            ),
          ),
        },
      );
      final cubit = TopicContentCubit(
        topicsRepository: repository,
        settingsCubit: settingsCubit,
        route: '',
      );
      addTearDown(cubit.close);

      await _flushAsync();

      final firstResult = await cubit.loadCommonResource(' icon ');
      final secondResult = await cubit.loadCommonResource('icon');

      expect(firstResult, isA<AppSuccess<TopicResource?>>());
      expect(secondResult, isA<AppSuccess<TopicResource?>>());
      expect(repository.resourceRequests, <String>['icon']);
    },
  );

  test('loadCommonResource returns validation failure for empty key', () async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _buildSettings(language: 'en')),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final repository = _FakeTopicsRepository(
      markdownByRouteLanguage: const <String, AppResult<String>>{},
      topicByRouteLanguage: const <String, AppResult<TopicInfo?>>{},
    );
    final cubit = TopicContentCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
      route: '',
    );
    addTearDown(cubit.close);

    await _flushAsync();

    final result = await cubit.loadCommonResource('   ');

    expect(result, isA<AppFailureResult<TopicResource?>>());
    expect(repository.resourceRequests, isEmpty);
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
    required this.markdownByRouteLanguage,
    required this.topicByRouteLanguage,
    this.resourceByKey = const <String, AppResult<TopicResource?>>{},
  }) : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<String>> markdownByRouteLanguage;
  final Map<String, AppResult<TopicInfo?>> topicByRouteLanguage;
  final Map<String, AppResult<TopicResource?>> resourceByKey;
  final List<String> markdownRequests = <String>[];
  final List<String> topicByRouteRequests = <String>[];
  final List<String> resourceRequests = <String>[];

  @override
  Future<AppResult<String>> getArticleMarkdown({
    required String route,
    required String language,
  }) async {
    final requestKey = '$route|$language';
    markdownRequests.add(requestKey);
    return markdownByRouteLanguage[requestKey] ??
        const AppFailureResult<String>(
          AppFailure.notFound('No fake markdown configured.'),
        );
  }

  @override
  Future<AppResult<TopicInfo?>> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    final requestKey = '$route|$language';
    topicByRouteRequests.add(requestKey);
    return topicByRouteLanguage[requestKey] ??
        const AppFailureResult<TopicInfo?>(
          AppFailure.notFound('No fake topic metadata configured.'),
        );
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    resourceRequests.add(key);
    return resourceByKey[key] ??
        const AppFailureResult<TopicResource?>(
          AppFailure.notFound('No fake common resource configured.'),
        );
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
