import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_text_formatter.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';

enum PrimarySourceWordImageUnavailableReason {
  none,
  sourceUnavailable,
  pageUnavailable,
  wordUnavailable,
  imageUnavailable,
}

class PrimarySourceWordsDialogData {
  PrimarySourceWordsDialogData({
    required List<PrimarySourceWordImageResult> items,
    this.sharedWordDetailsMarkdown,
  }) : items = List<PrimarySourceWordImageResult>.unmodifiable(items);

  final List<PrimarySourceWordImageResult> items;
  final String? sharedWordDetailsMarkdown;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceWordsDialogData &&
            runtimeType == other.runtimeType &&
            sharedWordDetailsMarkdown == other.sharedWordDetailsMarkdown &&
            listEquals(items, other.items);
  }

  @override
  int get hashCode =>
      Object.hash(sharedWordDetailsMarkdown, Object.hashAll(items));
}

class PrimarySourceWordImageResult {
  const PrimarySourceWordImageResult({
    required this.target,
    required this.sourceTitle,
    required this.imageBytes,
    required this.unavailableReason,
    this.displayWordText,
  });

  factory PrimarySourceWordImageResult.unavailable({
    required PrimarySourceWordLinkTarget target,
    String? sourceTitle,
    String? displayWordText,
    PrimarySourceWordImageUnavailableReason reason =
        PrimarySourceWordImageUnavailableReason.imageUnavailable,
  }) {
    return PrimarySourceWordImageResult(
      target: target,
      sourceTitle: sourceTitle ?? target.sourceId,
      imageBytes: null,
      unavailableReason: reason,
      displayWordText: displayWordText,
    );
  }

  final PrimarySourceWordLinkTarget target;
  final String sourceTitle;
  final Uint8List? imageBytes;
  final PrimarySourceWordImageUnavailableReason unavailableReason;
  final String? displayWordText;

  bool get hasImage => imageBytes != null && imageBytes!.isNotEmpty;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceWordImageResult &&
            runtimeType == other.runtimeType &&
            target == other.target &&
            sourceTitle == other.sourceTitle &&
            unavailableReason == other.unavailableReason &&
            displayWordText == other.displayWordText &&
            listEquals(imageBytes, other.imageBytes);
  }

  @override
  int get hashCode => Object.hash(
    target,
    sourceTitle,
    unavailableReason,
    displayWordText,
    imageBytes == null ? null : Object.hashAll(imageBytes!),
  );
}

class PrimarySourceWordImageService {
  PrimarySourceWordImageService({
    PrimarySourceReferenceService? referenceResolver,
    PrimarySourceImageLoadingOrchestrator? imageLoadingOrchestrator,
    PrimarySourceWordTextFormatter? wordTextFormatter,
    DescriptionContentService? descriptionService,
  }) : _referenceResolver =
           referenceResolver ?? PrimarySourceReferenceService(),
       _imageLoadingOrchestrator =
           imageLoadingOrchestrator ?? PrimarySourceImageLoadingOrchestrator(),
       _wordTextFormatter =
           wordTextFormatter ?? PrimarySourceWordTextFormatter(),
       _descriptionService = descriptionService ?? DescriptionContentService();

  final PrimarySourceReferenceService _referenceResolver;
  final PrimarySourceImageLoadingOrchestrator _imageLoadingOrchestrator;
  final PrimarySourceWordTextFormatter _wordTextFormatter;
  final DescriptionContentService _descriptionService;

  Future<List<PrimarySourceWordImageResult>> loadWordImages({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
  }) async {
    final data = await _loadDialogData(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
    );
    return data.items;
  }

  Future<PrimarySourceWordsDialogData> loadDialogData({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) async {
    return _loadDialogData(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      localizations: localizations,
    );
  }

  Future<PrimarySourceWordsDialogData> _loadDialogData({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    AppLocalizations? localizations,
  }) async {
    final imageCache = <String, Future<Uint8List?>>{};

    final items = <PrimarySourceWordImageResult>[];
    final resolvedWords = <PageWord>[];
    for (final target in targets) {
      final loaded = await _loadWordImage(
        target: target,
        isWeb: isWeb,
        isMobileWeb: isMobileWeb,
        imageCache: imageCache,
      );
      items.add(loaded.result);
      final resolvedWord = loaded.resolvedWord;
      if (resolvedWord != null) {
        resolvedWords.add(resolvedWord);
      }
    }

    final sharedWordDetailsMarkdown = localizations == null
        ? null
        : _descriptionService
              .buildSharedWordSupplementContent(localizations, resolvedWords)
              ?.markdown;

    return PrimarySourceWordsDialogData(
      items: items,
      sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
    );
  }

  Future<_LoadedWordImageData> _loadWordImage({
    required PrimarySourceWordLinkTarget target,
    required bool isWeb,
    required bool isMobileWeb,
    required Map<String, Future<Uint8List?>> imageCache,
  }) async {
    final source = _referenceResolver.findSourceById(target.sourceId);
    if (source == null) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          reason: PrimarySourceWordImageUnavailableReason.sourceUnavailable,
        ),
      );
    }

    final sourceTitle = source.title;
    final pageName = target.pageName;
    if (pageName == null || pageName.isEmpty) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          reason: PrimarySourceWordImageUnavailableReason.pageUnavailable,
        ),
      );
    }

    final page = _referenceResolver.findPageByName(source, pageName);
    if (page == null) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          reason: PrimarySourceWordImageUnavailableReason.pageUnavailable,
        ),
      );
    }

    final wordIndex = target.wordIndex;
    if (wordIndex == null || wordIndex < 0 || wordIndex >= page.words.length) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          reason: PrimarySourceWordImageUnavailableReason.wordUnavailable,
        ),
      );
    }

    final word = page.words[wordIndex];
    final displayWordText = _wordTextFormatter.format(word).trim();
    if (!source.permissionsReceived || word.rectangles.isEmpty) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          displayWordText: displayWordText,
          reason: PrimarySourceWordImageUnavailableReason.imageUnavailable,
        ),
        resolvedWord: word,
      );
    }

    final cacheKey = '${source.id}|${page.image}';
    final imageData = await imageCache.putIfAbsent(
      cacheKey,
      () => _loadPageImage(
        pageImage: page.image,
        sourceHashCode: source.hashCode,
        isWeb: isWeb,
        isMobileWeb: isMobileWeb,
      ),
    );
    if (imageData == null || imageData.isEmpty) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          displayWordText: displayWordText,
          reason: PrimarySourceWordImageUnavailableReason.imageUnavailable,
        ),
        resolvedWord: word,
      );
    }

    final cropped = cropWordImage(imageData: imageData, word: word);
    if (cropped == null || cropped.isEmpty) {
      return _LoadedWordImageData(
        result: PrimarySourceWordImageResult.unavailable(
          target: target,
          sourceTitle: sourceTitle,
          displayWordText: displayWordText,
          reason: PrimarySourceWordImageUnavailableReason.imageUnavailable,
        ),
        resolvedWord: word,
      );
    }

    return _LoadedWordImageData(
      result: PrimarySourceWordImageResult(
        target: target,
        sourceTitle: sourceTitle,
        imageBytes: cropped,
        displayWordText: displayWordText,
        unavailableReason: PrimarySourceWordImageUnavailableReason.none,
      ),
      resolvedWord: word,
    );
  }

  Future<Uint8List?> _loadPageImage({
    required String pageImage,
    required int sourceHashCode,
    required bool isWeb,
    required bool isMobileWeb,
  }) async {
    final loadResult = await _imageLoadingOrchestrator.loadPageImage(
      page: pageImage,
      sourceHashCode: sourceHashCode,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      isReload: false,
    );
    if (loadResult.contentAction != ImageContentAction.replace) {
      return null;
    }
    return loadResult.imageData;
  }

  @visibleForTesting
  Uint8List? cropWordImage({
    required Uint8List imageData,
    required PageWord word,
    int padding = 3,
  }) {
    if (word.rectangles.isEmpty) {
      return null;
    }

    final img.Image? sourceImage;
    try {
      sourceImage = img.decodeImage(imageData);
    } catch (_) {
      return null;
    }
    if (sourceImage == null ||
        sourceImage.width <= 0 ||
        sourceImage.height <= 0) {
      return null;
    }

    final bounds = _resolveWordBounds(
      rects: word.rectangles,
      imageWidth: sourceImage.width,
      imageHeight: sourceImage.height,
      padding: padding,
    );
    if (bounds.isEmpty) {
      return null;
    }

    final fragments = <img.Image>[];
    for (final bound in bounds) {
      fragments.add(
        img.copyCrop(
          sourceImage,
          x: bound.left,
          y: bound.top,
          width: bound.width,
          height: bound.height,
        ),
      );
    }

    final cropped = fragments.length == 1
        ? fragments.single
        : _stitchFragments(fragments);
    return Uint8List.fromList(img.encodePng(cropped));
  }

  List<_PixelRect> _resolveWordBounds({
    required List<PageRect> rects,
    required int imageWidth,
    required int imageHeight,
    required int padding,
  }) {
    final bounds = <_PixelRect>[];
    for (final rect in rects) {
      final bound = _resolveRectBounds(
        rect: rect,
        imageWidth: imageWidth,
        imageHeight: imageHeight,
        padding: padding,
      );
      if (bound != null) {
        bounds.add(bound);
      }
    }
    return bounds;
  }

  _PixelRect? _resolveRectBounds({
    required PageRect rect,
    required int imageWidth,
    required int imageHeight,
    required int padding,
  }) {
    final rectLeft = math
        .min(rect.startX, rect.endX)
        .clamp(0.0, 1.0)
        .toDouble();
    final rectTop = math.min(rect.startY, rect.endY).clamp(0.0, 1.0).toDouble();
    final rectRight = math
        .max(rect.startX, rect.endX)
        .clamp(0.0, 1.0)
        .toDouble();
    final rectBottom = math
        .max(rect.startY, rect.endY)
        .clamp(0.0, 1.0)
        .toDouble();
    if (rectRight <= rectLeft || rectBottom <= rectTop) {
      return null;
    }

    final left = rectLeft * imageWidth;
    final top = rectTop * imageHeight;
    final right = rectRight * imageWidth;
    final bottom = rectBottom * imageHeight;
    final x = math.max(0, left.floor() - padding);
    final y = math.max(0, top.floor() - padding);
    final maxRight = math.min(imageWidth, right.ceil() + padding);
    final maxBottom = math.min(imageHeight, bottom.ceil() + padding);
    final width = maxRight - x;
    final height = maxBottom - y;

    if (width <= 0 || height <= 0) {
      return null;
    }
    return _PixelRect(left: x, top: y, width: width, height: height);
  }

  img.Image _stitchFragments(List<img.Image> fragments) {
    final width = fragments.fold<int>(
      0,
      (total, fragment) => total + fragment.width,
    );
    final height = fragments.fold<int>(
      0,
      (maxHeight, fragment) => math.max(maxHeight, fragment.height),
    );
    final canvas = img.Image(width: width, height: height);
    img.fill(canvas, color: img.ColorRgb8(255, 255, 255));

    var nextX = 0;
    for (final fragment in fragments) {
      img.compositeImage(
        canvas,
        fragment,
        dstX: nextX,
        dstY: 0,
        blend: img.BlendMode.direct,
      );
      nextX += fragment.width;
    }
    return canvas;
  }
}

class _PixelRect {
  const _PixelRect({
    required this.left,
    required this.top,
    required this.width,
    required this.height,
  });

  final int left;
  final int top;
  final int width;
  final int height;
}

class _LoadedWordImageData {
  const _LoadedWordImageData({required this.result, this.resolvedWord});

  final PrimarySourceWordImageResult result;
  final PageWord? resolvedWord;
}
