import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/application/orchestrators/topic_markdown_image_orchestrator.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_markdown_image_state.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';

class TopicContentCubit extends Cubit<TopicContentState> {
  TopicContentCubit({
    required TopicsRepository topicsRepository,
    required SettingsCubit settingsCubit,
    required String route,
    String? name,
    String? description,
    TopicMarkdownImageOrchestrator? topicMarkdownImageOrchestrator,
  }) : _topicsRepository = topicsRepository,
       _settingsCubit = settingsCubit,
       _route = route,
       _initialName = name ?? '',
       _initialDescription = description ?? '',
       _topicMarkdownImageOrchestrator =
           topicMarkdownImageOrchestrator ??
           TopicMarkdownImageOrchestrator(topicsRepository: topicsRepository),
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
  final TopicMarkdownImageOrchestrator _topicMarkdownImageOrchestrator;
  StreamSubscription<String>? _settingsSubscription;
  int _activeRequestToken = 0;
  final Map<String, AppResult<TopicResource?>> _resourceCache =
      <String, AppResult<TopicResource?>>{};
  final Map<String, Future<AppResult<TopicResource?>>> _resourceRequests =
      <String, Future<AppResult<TopicResource?>>>{};

  Future<void> loadForLanguage(String language) async {
    final requestToken = ++_activeRequestToken;
    if (language.trim().isEmpty) {
      emit(
        state.copyWith(
          language: language,
          isLoading: false,
          markdownImages: const <String, TopicMarkdownImageState>{},
          markdownImagesTotalCount: 0,
          markdownImagesCompletedCount: 0,
          markdownImagesFailedCount: 0,
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
        markdownImages: const <String, TopicMarkdownImageState>{},
        markdownImagesTotalCount: 0,
        markdownImagesCompletedCount: 0,
        markdownImagesFailedCount: 0,
        clearFailure: true,
      ),
    );

    _resourceCache.clear();
    _resourceRequests.clear();

    if (_route.isEmpty) {
      emit(
        state.copyWith(
          route: _route,
          language: language,
          name: _initialName,
          description: _initialDescription,
          markdown: '',
          isLoading: false,
          markdownImages: const <String, TopicMarkdownImageState>{},
          markdownImagesTotalCount: 0,
          markdownImagesCompletedCount: 0,
          markdownImagesFailedCount: 0,
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
          markdownImages: const <String, TopicMarkdownImageState>{},
          markdownImagesTotalCount: 0,
          markdownImagesCompletedCount: 0,
          markdownImagesFailedCount: 0,
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

    final markdownImages = _topicMarkdownImageOrchestrator.collectAsyncImages(
      markdownResult.data,
    );

    emit(
      state.copyWith(
        route: _route,
        language: language,
        name: resolvedName,
        description: resolvedDescription,
        markdown: markdownResult.data,
        isLoading: false,
        markdownImages: _buildInitialMarkdownImages(markdownImages),
        markdownImagesTotalCount: markdownImages.length,
        markdownImagesCompletedCount: 0,
        markdownImagesFailedCount: 0,
        clearFailure: true,
      ),
    );

    if (markdownImages.isNotEmpty) {
      unawaited(_preloadMarkdownImages(markdownImages, requestToken));
    }
  }

  Future<AppResult<TopicResource?>> loadCommonResource(String key) async {
    final normalizedKey = key.trim();
    if (normalizedKey.isEmpty) {
      return const AppFailureResult<TopicResource?>(
        AppFailure.validation('Common resource key must not be empty.'),
      );
    }

    final cachedResult = _resourceCache[normalizedKey];
    if (cachedResult != null) {
      return cachedResult;
    }

    final activeRequest = _resourceRequests[normalizedKey];
    if (activeRequest != null) {
      return activeRequest;
    }

    final request = _topicsRepository
        .getCommonResource(normalizedKey)
        .then((result) {
          _resourceCache[normalizedKey] = result;
          return result;
        })
        .whenComplete(() {
          _resourceRequests.remove(normalizedKey);
        });

    _resourceRequests[normalizedKey] = request;
    return request;
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

  Map<String, TopicMarkdownImageState> _buildInitialMarkdownImages(
    List<RevelationMarkdownImageData> markdownImages,
  ) {
    final result = <String, TopicMarkdownImageState>{};
    for (final image in markdownImages) {
      result[image.cacheKey] = const TopicMarkdownImageState.loading();
    }
    return result;
  }

  Future<void> _preloadMarkdownImages(
    List<RevelationMarkdownImageData> markdownImages,
    int requestToken,
  ) async {
    await Future.wait(
      markdownImages.map((image) => _preloadMarkdownImage(image, requestToken)),
    );
  }

  Future<void> _preloadMarkdownImage(
    RevelationMarkdownImageData image,
    int requestToken,
  ) async {
    final result = await _topicMarkdownImageOrchestrator.loadImage(image);
    if (_isStale(requestToken)) {
      return;
    }

    final nextState = result.isSuccess
        ? TopicMarkdownImageState.ready(
            bytes: result.bytes!,
            mimeType: result.mimeType,
          )
        : const TopicMarkdownImageState.failure();

    final updatedImages = Map<String, TopicMarkdownImageState>.from(
      state.markdownImages,
    );
    final previousState = updatedImages[image.cacheKey];
    final wasCompleted =
        previousState != null &&
        previousState.status != TopicMarkdownImageStatus.loading;
    final wasFailure =
        previousState?.status == TopicMarkdownImageStatus.failure;

    updatedImages[image.cacheKey] = nextState;

    emit(
      state.copyWith(
        markdownImages: updatedImages,
        markdownImagesCompletedCount: wasCompleted
            ? state.markdownImagesCompletedCount
            : state.markdownImagesCompletedCount + 1,
        markdownImagesFailedCount: _nextFailedCount(
          currentFailedCount: state.markdownImagesFailedCount,
          wasFailure: wasFailure,
          isFailure: nextState.status == TopicMarkdownImageStatus.failure,
        ),
      ),
    );
  }

  int _nextFailedCount({
    required int currentFailedCount,
    required bool wasFailure,
    required bool isFailure,
  }) {
    if (wasFailure == isFailure) {
      return currentFailedCount;
    }
    if (isFailure) {
      return currentFailedCount + 1;
    }
    return currentFailedCount > 0 ? currentFailedCount - 1 : 0;
  }

  @override
  Future<void> close() async {
    await _settingsSubscription?.cancel();
    return super.close();
  }
}
