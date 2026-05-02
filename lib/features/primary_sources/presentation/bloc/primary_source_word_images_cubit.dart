import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_state.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';

class PrimarySourceWordImagesCubit extends Cubit<PrimarySourceWordImagesState> {
  PrimarySourceWordImagesCubit({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
    PrimarySourceWordImageService? imageService,
    bool autoLoad = true,
  }) : _targets = List<PrimarySourceWordLinkTarget>.unmodifiable(targets),
       _isWeb = isWeb,
       _isMobileWeb = isMobileWeb,
       _localizations = localizations,
       _imageService = imageService ?? PrimarySourceWordImageService(),
       super(PrimarySourceWordImagesState.loading()) {
    if (autoLoad) {
      unawaited(load());
    }
  }

  final List<PrimarySourceWordLinkTarget> _targets;
  final bool _isWeb;
  final bool _isMobileWeb;
  final AppLocalizations _localizations;
  final PrimarySourceWordImageService _imageService;
  final LatestRequestGuard _loadRequestGuard = LatestRequestGuard();

  Future<void> load() async {
    final requestToken = _loadRequestGuard.start();
    emit(PrimarySourceWordImagesState.loading());

    try {
      PrimarySourceWordsDialogData? latestData;
      await for (final data in _imageService.loadDialogDataStream(
        targets: _targets,
        isWeb: _isWeb,
        isMobileWeb: _isMobileWeb,
        localizations: _localizations,
      )) {
        if (!_canApply(requestToken)) {
          return;
        }
        latestData = data;
        emit(
          PrimarySourceWordImagesState.loading(
            items: data.items,
            sharedWordDetailsMarkdown: data.sharedWordDetailsMarkdown,
          ),
        );
      }
      if (!_canApply(requestToken)) {
        return;
      }
      final data =
          latestData ??
          PrimarySourceWordsDialogData(
            items: _targets
                .map(
                  (target) =>
                      PrimarySourceWordImageResult.unavailable(target: target),
                )
                .toList(growable: false),
          );
      emit(
        PrimarySourceWordImagesState.loaded(
          items: data.items,
          sharedWordDetailsMarkdown: data.sharedWordDetailsMarkdown,
        ),
      );
    } catch (error, stackTrace) {
      if (!_canApply(requestToken)) {
        return;
      }
      log.error('Primary source word image loading error: $error', stackTrace);
      emit(
        PrimarySourceWordImagesState.loaded(
          items: _targets
              .map(
                (target) =>
                    PrimarySourceWordImageResult.unavailable(target: target),
              )
              .toList(growable: false),
        ),
      );
    }
  }

  bool _canApply(RequestToken token) {
    return !isClosed && _loadRequestGuard.isActive(token);
  }

  @override
  Future<void> close() {
    _loadRequestGuard.cancelActive();
    return super.close();
  }
}
