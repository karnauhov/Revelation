@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test_harness/test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  test('registerCore replaces existing Talker singleton', () async {
    final first = Talker(settings: TalkerSettings(useConsoleLogs: false));
    final second = Talker(settings: TalkerSettings(useConsoleLogs: false));

    AppDi.registerCore(talker: first);
    expect(GetIt.I<Talker>(), same(first));
    expect(GetIt.I<AppAnalyticsReporter>(), isA<NoopAppAnalyticsReporter>());
    expect(GetIt.I<MarkdownImageLoader>(), isA<MarkdownImageLoader>());

    const analyticsReporter = _FakeAppAnalyticsReporter();
    AppDi.registerCore(talker: second, analyticsReporter: analyticsReporter);
    expect(GetIt.I<Talker>(), same(second));
    expect(GetIt.I<AppAnalyticsReporter>(), same(analyticsReporter));
    expect(GetIt.I<MarkdownImageLoader>(), isA<MarkdownImageLoader>());
  });

  testWidgets(
    'appBlocProviders wires settings, topics and primary sources cubits',
    (tester) async {
      AppDi.registerCore(
        talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
      );
      final settingsCubit = SettingsCubit(
        FakeSettingsRepository(initialSettings: _testSettings),
      );
      addTearDown(settingsCubit.close);
      await settingsCubit.loadSettings();

      TopicsCatalogCubit? topicsCatalogCubit;
      PrimarySourcesCubit? primarySourcesCubit;
      SettingsCubit? providedSettingsCubit;

      await tester.pumpWidget(
        MultiBlocProvider(
          providers: AppDi.appBlocProviders(settingsCubit: settingsCubit),
          child: MaterialApp(
            home: Builder(
              builder: (context) {
                providedSettingsCubit = context.read<SettingsCubit>();
                topicsCatalogCubit = context.read<TopicsCatalogCubit>();
                primarySourcesCubit = context.read<PrimarySourcesCubit>();
                return const SizedBox.shrink();
              },
            ),
          ),
        ),
      );
      await pumpFrames(tester, count: 2);

      expect(providedSettingsCubit, same(settingsCubit));
      expect(topicsCatalogCubit, isA<TopicsCatalogCubit>());
      expect(primarySourcesCubit, isA<PrimarySourcesCubit>());
    },
  );

  test('factory helpers return expected types and support overrides', () async {
    AppDi.registerCore(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    final settingsCubit = SettingsCubit(
      FakeSettingsRepository(initialSettings: _testSettings),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final topicsRepository = AppDi.createTopicsRepository();
    final primarySourcesRepository = AppDi.createPrimarySourcesDbRepository();
    final pagesRepository = AppDi.createPagesRepository();
    final markdownImageLoader = AppDi.createMarkdownImageLoader();
    final explicitOrchestrator =
        AppDi.createPrimarySourcePageSettingsOrchestrator(
          pagesRepository: pagesRepository,
        );
    final fallbackOrchestrator =
        AppDi.createPrimarySourcePageSettingsOrchestrator();
    final cubitFromExplicit = AppDi.createPrimarySourcePageSettingsCubit(
      pageSettingsOrchestrator: explicitOrchestrator,
    );
    final cubitFromFallback = AppDi.createPrimarySourcePageSettingsCubit();
    final topicCubitWithExplicitRepo = AppDi.createTopicContentCubit(
      settingsCubit: settingsCubit,
      route: '',
      topicsRepository: topicsRepository,
      name: 'Typed',
      description: 'Description',
    );
    final topicCubitWithFallbackRepo = AppDi.createTopicContentCubit(
      settingsCubit: settingsCubit,
      route: '',
    );

    addTearDown(cubitFromExplicit.close);
    addTearDown(cubitFromFallback.close);
    addTearDown(topicCubitWithExplicitRepo.close);
    addTearDown(topicCubitWithFallbackRepo.close);

    expect(topicsRepository, isA<TopicsRepository>());
    expect(primarySourcesRepository, isA<PrimarySourcesDbRepository>());
    expect(pagesRepository, isA<PagesRepository>());
    expect(markdownImageLoader, isA<MarkdownImageLoader>());
    expect(explicitOrchestrator, isA<PrimarySourcePageSettingsOrchestrator>());
    expect(fallbackOrchestrator, isA<PrimarySourcePageSettingsOrchestrator>());
    expect(cubitFromExplicit, isA<PrimarySourcePageSettingsCubit>());
    expect(cubitFromFallback, isA<PrimarySourcePageSettingsCubit>());
    expect(topicCubitWithExplicitRepo, isA<TopicContentCubit>());
    expect(topicCubitWithFallbackRepo, isA<TopicContentCubit>());
  });
}

final _testSettings = AppSettings(
  selectedLanguage: 'en',
  selectedTheme: 'manuscript',
  selectedFontSize: 'medium',
  soundEnabled: false,
);

class _FakeAppAnalyticsReporter implements AppAnalyticsReporter {
  const _FakeAppAnalyticsReporter();

  @override
  Future<void> setAppContext(AppAnalyticsAppContext context) async {}

  @override
  Future<void> setDataContext(AppAnalyticsDataContext context) async {}

  @override
  Future<void> trackAppSessionStarted(AppAnalyticsDataContext context) async {}

  @override
  Future<void> captureException(
    Object error,
    StackTrace stackTrace, {
    required String source,
    bool fatal = false,
  }) async {}
}
