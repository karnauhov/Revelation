@Tags(['widget'])
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_card.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_list.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

void main() {
  testWidgets('TopicList shows loading indicator while request is pending', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final repository = _ControlledTopicsRepository();
    final cubit = TopicsCatalogCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);

    await tester.pumpWidget(_buildApp(cubit));
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.byType(ErrorMessage), findsNothing);

    repository.completeRequest(
      0,
      const AppSuccess<List<TopicInfo>>(<TopicInfo>[]),
    );
    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.byType(ErrorMessage), findsNothing);
  });

  testWidgets('TopicList shows error fallback when repository fails', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final cubit = TopicsCatalogCubit(
      topicsRepository: _FixedTopicsRepository(
        topicsResult: const AppFailureResult<List<TopicInfo>>(
          AppFailure.dataSource('widget forced topics failure'),
        ),
      ),
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);

    await tester.pumpWidget(_buildApp(cubit));
    await tester.pumpAndSettle();

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.byType(TopicCard), findsNothing);
  });

  testWidgets('TopicList renders topic cards after successful load', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final cubit = TopicsCatalogCubit(
      topicsRepository: _FixedTopicsRepository(
        topicsResult: AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic EN',
            idIcon: 'topic-icon',
            description: 'Description EN',
            route: 'topic-en',
          ),
        ]),
        iconByKey: <String, AppResult<TopicResource?>>{
          'topic-icon': AppSuccess<TopicResource?>(_buildSvgResource()),
        },
      ),
      settingsCubit: settingsCubit,
    );
    addTearDown(cubit.close);

    await tester.pumpWidget(_buildApp(cubit));
    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.byType(ErrorMessage), findsNothing);
    expect(find.byType(TopicCard), findsOneWidget);
    expect(find.text('Topic EN'), findsOneWidget);
    expect(find.text('Description EN'), findsOneWidget);
  });
}

Widget _buildApp(TopicsCatalogCubit cubit) {
  return BlocProvider<TopicsCatalogCubit>.value(
    value: cubit,
    child: MaterialApp(
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: const Scaffold(body: TopicList()),
    ),
  );
}

TopicResource _buildSvgResource() {
  return TopicResource(
    fileName: 'topic-icon.svg',
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

class _FixedTopicsRepository extends TopicsRepository {
  _FixedTopicsRepository({
    required this.topicsResult,
    this.iconByKey = const <String, AppResult<TopicResource?>>{},
  }) : super(dataSource: _NoopTopicsDataSource());

  final AppResult<List<TopicInfo>> topicsResult;
  final Map<String, AppResult<TopicResource?>> iconByKey;

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    return topicsResult;
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return iconByKey[key] ?? const AppSuccess<TopicResource?>(null);
  }
}

class _ControlledTopicsRepository extends TopicsRepository {
  _ControlledTopicsRepository() : super(dataSource: _NoopTopicsDataSource());

  final List<Completer<AppResult<List<TopicInfo>>>> _requests =
      <Completer<AppResult<List<TopicInfo>>>>[];

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({required String language}) {
    final completer = Completer<AppResult<List<TopicInfo>>>();
    _requests.add(completer);
    return completer.future;
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return const AppSuccess<TopicResource?>(null);
  }

  void completeRequest(int index, AppResult<List<TopicInfo>> result) {
    _requests[index].complete(result);
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
