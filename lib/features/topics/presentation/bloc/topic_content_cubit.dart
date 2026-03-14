import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';

class TopicContentCubit extends Cubit<TopicContentState> {
  TopicContentCubit({
    required TopicsRepository topicsRepository,
    required SettingsCubit settingsCubit,
    required String route,
    String? name,
    String? description,
  }) : _topicsRepository = topicsRepository,
       _settingsCubit = settingsCubit,
       _route = route,
       _initialName = name ?? '',
       _initialDescription = description ?? '',
       super(
         TopicContentState.initial().copyWith(
           route: route,
           name: name ?? '',
           description: description ?? '',
         ),
       ) {
    _settingsSubscription = _settingsCubit.stream
        .map((settingsState) => settingsState.settings.selectedLanguage)
        .distinct()
        .listen(loadForLanguage);
    unawaited(loadForLanguage(_settingsCubit.state.settings.selectedLanguage));
  }

  final TopicsRepository _topicsRepository;
  final SettingsCubit _settingsCubit;
  final String _route;
  final String _initialName;
  final String _initialDescription;
  StreamSubscription<String>? _settingsSubscription;
  int _activeRequestToken = 0;

  Future<void> loadForLanguage(String language) async {
    final requestToken = ++_activeRequestToken;
    if (language.trim().isEmpty) {
      emit(
        state.copyWith(
          language: language,
          isLoading: false,
          failure: const AppFailure.validation('Language must not be empty.'),
        ),
      );
      return;
    }

    emit(
      state.copyWith(
        route: _route,
        language: language,
        name: _initialName,
        description: _initialDescription,
        markdown: '',
        isLoading: true,
        clearFailure: true,
      ),
    );

    if (_route.isEmpty) {
      emit(
        state.copyWith(
          route: _route,
          language: language,
          name: _initialName,
          description: _initialDescription,
          markdown: '',
          isLoading: false,
          clearFailure: true,
        ),
      );
      return;
    }

    final markdownResult = await _topicsRepository.getArticleMarkdown(
      route: _route,
      language: language,
    );
    if (_isStale(requestToken)) {
      return;
    }
    if (markdownResult is! AppSuccess<String>) {
      final failure = markdownResult is AppFailureResult<String>
          ? markdownResult.error
          : const AppFailure.unknown('Unable to load topic markdown.');
      emit(
        state.copyWith(
          route: _route,
          language: language,
          name: _initialName,
          description: _initialDescription,
          markdown: '',
          isLoading: false,
          failure: failure,
        ),
      );
      return;
    }

    var resolvedName = _initialName;
    var resolvedDescription = _initialDescription;

    if (resolvedName.isEmpty || resolvedDescription.isEmpty) {
      final articleResult = await _topicsRepository.getTopicByRoute(
        route: _route,
        language: language,
      );
      if (_isStale(requestToken)) {
        return;
      }
      if (articleResult is AppSuccess<TopicInfo?>) {
        resolvedName = _firstNonEmpty(resolvedName, articleResult.data?.name);
        resolvedDescription = _firstNonEmpty(
          resolvedDescription,
          articleResult.data?.description,
        );
      }
    }

    emit(
      state.copyWith(
        route: _route,
        language: language,
        name: resolvedName,
        description: resolvedDescription,
        markdown: markdownResult.data,
        isLoading: false,
        clearFailure: true,
      ),
    );
  }

  String _firstNonEmpty(String? first, String? second, [String fallback = '']) {
    if (first != null && first.trim().isNotEmpty) {
      return first;
    }
    if (second != null && second.trim().isNotEmpty) {
      return second;
    }
    return fallback;
  }

  bool _isStale(int requestToken) =>
      isClosed || requestToken != _activeRequestToken;

  @override
  Future<void> close() async {
    await _settingsSubscription?.cancel();
    return super.close();
  }
}
