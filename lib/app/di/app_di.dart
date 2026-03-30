import 'package:get_it/get_it.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:nested/nested.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
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
import 'package:talker_flutter/talker_flutter.dart';

class AppDi {
  AppDi._();

  static final GetIt _getIt = GetIt.instance;

  static void registerCore({required Talker talker}) {
    if (_getIt.isRegistered<Talker>()) {
      _getIt.unregister<Talker>();
    }
    _getIt.registerSingleton<Talker>(talker);

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
