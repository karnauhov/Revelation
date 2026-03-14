import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_state.dart';

class TopicsCatalogCubit extends Cubit<TopicsCatalogState> {
  TopicsCatalogCubit({
    required TopicsRepository topicsRepository,
    required SettingsCubit settingsCubit,
  }) : _topicsRepository = topicsRepository,
       _settingsCubit = settingsCubit,
       super(TopicsCatalogState.initial()) {
    _settingsSubscription = _settingsCubit.stream
        .map((settingsState) => settingsState.settings.selectedLanguage)
        .distinct()
        .listen(loadForLanguage);
    unawaited(loadForLanguage(_settingsCubit.state.settings.selectedLanguage));
  }

  final TopicsRepository _topicsRepository;
  final SettingsCubit _settingsCubit;
  StreamSubscription<String>? _settingsSubscription;

  Future<void> loadForLanguage(String language) async {
    if (language.trim().isEmpty) {
      emit(
        state.copyWith(
          isLoading: false,
          failure: const AppFailure.validation('Language must not be empty.'),
        ),
      );
      return;
    }

    emit(
      state.copyWith(language: language, isLoading: true, clearFailure: true),
    );

    final topicsResult = await _topicsRepository.getTopics(language: language);
    if (topicsResult is! AppSuccess<List<TopicInfo>>) {
      final failure = topicsResult is AppFailureResult<List<TopicInfo>>
          ? topicsResult.error
          : const AppFailure.unknown('Unable to load topics.');
      emit(state.copyWith(isLoading: false, failure: failure));
      return;
    }

    final topics = topicsResult.data;
    final iconByKey = await _loadIcons(topics);
    emit(
      state.copyWith(
        language: language,
        topics: topics,
        iconByKey: iconByKey,
        isLoading: false,
        clearFailure: true,
      ),
    );
  }

  Future<Map<String, TopicResource?>> _loadIcons(List<TopicInfo> topics) async {
    final keys = topics
        .map((topic) => topic.idIcon.trim())
        .where((key) => key.isNotEmpty)
        .toSet()
        .toList(growable: false);
    if (keys.isEmpty) {
      return <String, TopicResource?>{};
    }

    final loadedPairs = await Future.wait(
      keys.map((key) async {
        final result = await _topicsRepository.getCommonResource(key);
        if (result is AppSuccess<TopicResource?>) {
          return MapEntry<String, TopicResource?>(key, result.data);
        }
        return MapEntry<String, TopicResource?>(key, null);
      }),
    );
    return Map<String, TopicResource?>.fromEntries(loadedPairs);
  }

  @override
  Future<void> close() async {
    await _settingsSubscription?.cancel();
    return super.close();
  }
}
