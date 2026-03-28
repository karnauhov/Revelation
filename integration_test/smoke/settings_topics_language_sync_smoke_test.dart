import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_list.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'smoke_test_harness.dart';

void main() {
  testWidgets('Settings language change propagates to topics catalog', (
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

    final topicsRepository = _FakeTopicsRepository(
      topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
        'en': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic EN',
            idIcon: '',
            description: 'Description EN',
            route: 'topic-en',
          ),
        ]),
        'ru': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic RU',
            idIcon: '',
            description: 'Description RU',
            route: 'topic-ru',
          ),
        ]),
      },
    );
    final topicsCubit = TopicsCatalogCubit(
      topicsRepository: topicsRepository,
      settingsCubit: settingsCubit,
    );
    addTearDown(topicsCubit.close);

    await tester.pumpWidget(
      MultiBlocProvider(
        providers: <BlocProvider>[
          BlocProvider<SettingsCubit>.value(value: settingsCubit),
          BlocProvider<TopicsCatalogCubit>.value(value: topicsCubit),
        ],
        child: MaterialApp(
          locale: const Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          routes: <String, WidgetBuilder>{
            '/': (_) => const _TopicsHostScreen(),
            '/settings': (_) => const SettingsScreen(),
          },
        ),
      ),
    );
    await pumpAndSettleSmoke(tester);

    expect(find.text('Topic EN'), findsOneWidget);

    await tester.tap(find.byKey(const Key('open-settings')));
    await pumpAndSettleSmoke(tester);

    final settingsContext = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(settingsContext)!;
    final russianLanguageLabel = AppConstants.languages['ru']!;
    await tester.tap(find.text(l10n.language));
    await pumpAndSettleSmoke(tester);
    await tester.tap(find.text(russianLanguageLabel).last);
    await pumpAndSettleSmoke(tester);

    await tester.pageBack();
    await pumpAndSettleSmoke(tester);

    expect(find.text('Topic RU'), findsOneWidget);
    expect(topicsRepository.requestedLanguages, contains('en'));
    expect(topicsRepository.requestedLanguages, contains('ru'));
  });
}

class _TopicsHostScreen extends StatelessWidget {
  const _TopicsHostScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: <Widget>[
          IconButton(
            key: const Key('open-settings'),
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).pushNamed('/settings'),
          ),
        ],
      ),
      body: const TopicList(),
    );
  }
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
  _FakeTopicsRepository({required this.topicsByLanguage})
    : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<List<TopicInfo>>> topicsByLanguage;
  final List<String> requestedLanguages = <String>[];

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    requestedLanguages.add(language);
    return topicsByLanguage[language] ??
        const AppFailureResult<List<TopicInfo>>(
          AppFailure.notFound('No topics for requested language.'),
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
