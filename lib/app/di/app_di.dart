import 'package:get_it/get_it.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:nested/nested.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/features/bible/data/repositories/bible_bookmark_store.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_bookmarks_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_catalog_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_passage_preview_cubit.dart';
import 'package:revelation/features/allusion_search/data/repositories/allusion_search_repository.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/strongs_dictionary/data/repositories/strongs_dictionary_repository.dart';
import 'package:revelation/features/strongs_dictionary/data/repositories/strong_dictionary_reading_store.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/features/topics/topics.dart'
    show TopicsCatalogCubit, TopicsRepository;
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/infra/content/markdown_images/default_markdown_image_loader.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:talker_flutter/talker_flutter.dart';

class AppDi {
  AppDi._();

  static final GetIt _getIt = GetIt.instance;
  static SettingsCubit? _settingsCubit;
  static BibleLibraryRepository get bibleLibrary {
    if (!_getIt.isRegistered<BibleLibraryRepository>()) {
      _getIt.registerLazySingleton<BibleLibraryRepository>(
        () => BibleLibraryRepository(
          loadSettings: () async =>
              settingsCubitOrNull?.state.settings ??
              await SettingsRepository().getSettings(),
        ),
      );
    }
    return _getIt<BibleLibraryRepository>();
  }

  static BibleCatalogCubit createBibleCatalogCubit() =>
      BibleCatalogCubit(bibleLibrary);

  static final _bibleBookmarkStore = BibleBookmarkStore();
  static BibleBookmarksCubit createBibleBookmarksCubit() =>
      BibleBookmarksCubit(_bibleBookmarkStore);

  static BiblePassagePreviewCubit createBiblePassagePreviewCubit() =>
      BiblePassagePreviewCubit(bibleLibrary);
  static AllusionSearchCubit get allusionSearchCubit {
    if (!_getIt.isRegistered<AllusionSearchCubit>()) {
      _getIt.registerLazySingleton<AllusionSearchCubit>(
        () => AllusionSearchCubit(
          AllusionSearchRepository(
            loadVerseMap: () async =>
                bibleVerseMapOrNull ?? await BibleVerseMap.loadFromAssets(),
          ),
          bibleLibrary,
          initialVerseMap: bibleVerseMapOrNull,
        ),
        dispose: (cubit) => cubit.close(),
      );
    }
    return _getIt<AllusionSearchCubit>();
  }

  static SettingsCubit? get settingsCubitOrNull =>
      _settingsCubit?.isClosed == false ? _settingsCubit : null;
  static final _dictionary = StrongsDictionaryRepository();
  static final strongDictionaryReadingStore = StrongDictionaryReadingStore();
  static String? greekWord(int number) => _dictionary.findGreekWord(number);

  static void registerCore({
    required Talker talker,
    AppAnalyticsReporter? analyticsReporter,
  }) {
    if (_getIt.isRegistered<Talker>()) {
      _getIt.unregister<Talker>();
    }
    _getIt.registerSingleton<Talker>(talker);

    if (_getIt.isRegistered<AppAnalyticsReporter>()) {
      _getIt.unregister<AppAnalyticsReporter>();
    }
    _getIt.registerSingleton<AppAnalyticsReporter>(
      analyticsReporter ?? const NoopAppAnalyticsReporter(),
    );

    if (_getIt.isRegistered<MarkdownImageLoader>()) {
      _getIt.unregister<MarkdownImageLoader>();
    }
    _getIt.registerLazySingleton<MarkdownImageLoader>(
      createMarkdownImageLoader,
    );
  }

  static List<SingleChildWidget> appBlocProviders({
    required SettingsCubit settingsCubit,
  }) {
    _settingsCubit = settingsCubit;
    return <SingleChildWidget>[
      BlocProvider<SettingsCubit>.value(value: settingsCubit),
      BlocProvider<TopicsCatalogCubit>(
        create: (_) => TopicsCatalogCubit(
          topicsRepository: createTopicsRepository(),
          settingsCubit: settingsCubit,
        ),
      ),
      BlocProvider<PrimarySourcesCubit>(
        create: (_) => PrimarySourcesCubit(createPrimarySourcesDbRepository()),
      ),
    ];
  }

  static TopicsRepository createTopicsRepository() => TopicsRepository();

  static MarkdownImageLoader createMarkdownImageLoader() {
    return DefaultMarkdownImageLoader();
  }

  static PrimarySourcesDbRepository createPrimarySourcesDbRepository() {
    return PrimarySourcesDbRepository();
  }

  static PagesRepository createPagesRepository() => PagesRepository();

  static BibleRepository createBibleRepository() =>
      BibleRepository(loadModuleCatalog: bibleLibrary.availableCatalog);

  static void registerBibleVerseMap(BibleVerseMap verseMap) {
    if (_getIt.isRegistered<BibleVerseMap>()) {
      _getIt.unregister<BibleVerseMap>();
    }
    _getIt.registerSingleton<BibleVerseMap>(verseMap);
  }

  static BibleVerseMap? get bibleVerseMapOrNull {
    if (_getIt.isRegistered<BibleVerseMap>()) {
      return _getIt<BibleVerseMap>();
    }
    return null;
  }

  static PrimarySourcePageSettingsOrchestrator
  createPrimarySourcePageSettingsOrchestrator({
    PagesRepository? pagesRepository,
  }) {
    return PrimarySourcePageSettingsOrchestrator(
      pagesRepository ?? createPagesRepository(),
    );
  }

  static PrimarySourcePageSettingsCubit createPrimarySourcePageSettingsCubit({
    PrimarySourcePageSettingsOrchestrator? pageSettingsOrchestrator,
  }) {
    return PrimarySourcePageSettingsCubit(
      pageSettingsOrchestrator ?? createPrimarySourcePageSettingsOrchestrator(),
    );
  }

  static TopicContentCubit createTopicContentCubit({
    required SettingsCubit settingsCubit,
    required String route,
    String? name,
    String? description,
    TopicsRepository? topicsRepository,
  }) {
    final resolvedTopicsRepository =
        topicsRepository ?? createTopicsRepository();
    return TopicContentCubit(
      topicsRepository: resolvedTopicsRepository,
      settingsCubit: settingsCubit,
      route: route,
      name: name,
      description: description,
    );
  }
}
