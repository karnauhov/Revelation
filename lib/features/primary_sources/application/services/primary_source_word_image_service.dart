import 'dart:collection';
import 'dart:convert';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_text_formatter.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
    this.isLoading = false,
  });

  factory PrimarySourceWordImageResult.loading({
    required PrimarySourceWordLinkTarget target,
    required String sourceTitle,
    String? displayWordText,
  }) {
    return PrimarySourceWordImageResult(
      target: target,
      sourceTitle: sourceTitle,
      imageBytes: null,
      unavailableReason: PrimarySourceWordImageUnavailableReason.none,
      displayWordText: displayWordText,
      isLoading: true,
    );
  }

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
  final bool isLoading;

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
            isLoading == other.isLoading &&
            listEquals(imageBytes, other.imageBytes);
  }

  @override
  int get hashCode => Object.hash(
    target,
    sourceTitle,
    unavailableReason,
    displayWordText,
    isLoading,
    imageBytes == null ? null : Object.hashAll(imageBytes!),
  );
}

class PrimarySourceWordImageService {
  PrimarySourceWordImageService({
    PrimarySourceReferenceService? referenceResolver,
    PrimarySourceImageLoadingOrchestrator? imageLoadingOrchestrator,
    PrimarySourceWordTextFormatter? wordTextFormatter,
    DescriptionContentService? descriptionService,
    PrimarySourceWordCropCache? cropCache,
    PrimarySourceWordImageCropper? imageCropper,
    PrimarySourceWordImageCropper? webImageCropper,
  }) : _referenceResolver =
           referenceResolver ?? PrimarySourceReferenceService(),
       _imageLoadingOrchestrator =
           imageLoadingOrchestrator ?? PrimarySourceImageLoadingOrchestrator(),
       _wordTextFormatter =
           wordTextFormatter ?? PrimarySourceWordTextFormatter(),
       _descriptionService = descriptionService ?? DescriptionContentService(),
       _cropCache = cropCache ?? PrimarySourceWordCropCache(),
       _imageCropper = imageCropper ?? DartPrimarySourceWordImageCropper(),
       _webImageCropper =
           webImageCropper ?? CanvasPrimarySourceWordImageCropper();

  final PrimarySourceReferenceService _referenceResolver;
  final PrimarySourceImageLoadingOrchestrator _imageLoadingOrchestrator;
  final PrimarySourceWordTextFormatter _wordTextFormatter;
  final DescriptionContentService _descriptionService;
  final PrimarySourceWordCropCache _cropCache;
  final PrimarySourceWordImageCropper _imageCropper;
  final PrimarySourceWordImageCropper _webImageCropper;

  Future<List<PrimarySourceWordImageResult>> loadWordImages({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
  }) async {
    PrimarySourceWordsDialogData? latest;
    await for (final data in _loadDialogDataStream(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
    )) {
      latest = data;
    }
    return latest?.items ?? const <PrimarySourceWordImageResult>[];
  }

  Future<PrimarySourceWordsDialogData> loadDialogData({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) async {
    PrimarySourceWordsDialogData? latest;
    await for (final data in loadDialogDataStream(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      localizations: localizations,
    )) {
      latest = data;
    }
    return latest ?? PrimarySourceWordsDialogData(items: const []);
  }

  Stream<PrimarySourceWordsDialogData> loadDialogDataStream({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) {
    return _loadDialogDataStream(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      localizations: localizations,
    );
  }

  Stream<PrimarySourceWordsDialogData> _loadDialogDataStream({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    AppLocalizations? localizations,
  }) async* {
    final totalStopwatch = Stopwatch()..start();
    final resolveStopwatch = Stopwatch()..start();
    final resolvedTargets = _resolveTargets(targets);
    final items = resolvedTargets
        .map((resolved) => resolved.initialResult)
        .toList(growable: true);
    final resolvedWords = resolvedTargets
        .map((resolved) => resolved.resolvedWord)
        .whereType<PageWord>()
        .toList(growable: false);
    final sharedWordDetailsMarkdown = localizations == null
        ? null
        : _descriptionService
              .buildSharedWordSupplementContent(localizations, resolvedWords)
              ?.markdown;
    _traceWebTiming(
      isWeb,
      'resolved ${targets.length} targets in ${resolveStopwatch.elapsedMilliseconds} ms',
    );

    yield PrimarySourceWordsDialogData(
      items: items,
      sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
    );

    final pendingTargets = resolvedTargets
        .where((resolved) => resolved.needsCrop)
        .toList(growable: false);
    if (pendingTargets.isEmpty) {
      _traceWebTiming(
        isWeb,
        'finished without crop work in ${totalStopwatch.elapsedMilliseconds} ms',
      );
      return;
    }

    var changed = await _applyCachedCrops(pendingTargets, items, isWeb: isWeb);
    if (changed) {
      yield PrimarySourceWordsDialogData(
        items: items,
        sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
      );
    }

    final uncachedTargets = pendingTargets
        .where((resolved) => !items[resolved.index].hasImage)
        .toList(growable: false);
    final groupedTargets = _groupTargetsByPage(uncachedTargets);
    final imageCache = <String, Future<Uint8List?>>{};
    final cropper = isWeb ? _webImageCropper : _imageCropper;

    for (final group in groupedTargets.values) {
      if (isWeb) {
        await _yieldForWeb();
      }

      final pageStopwatch = Stopwatch()..start();
      final first = group.first;
      final imageData = await imageCache.putIfAbsent(
        first.pageCacheKey,
        () => _loadPageImage(
          pageImage: first.page!.image,
          sourceHashCode: first.source!.hashCode,
          isWeb: isWeb,
          isMobileWeb: isMobileWeb,
        ),
      );
      if (imageData == null || imageData.isEmpty) {
        _applyUnavailableGroup(group, items);
        yield PrimarySourceWordsDialogData(
          items: items,
          sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
        );
        continue;
      }

      final cropRequests = group
          .map(
            (resolved) => PrimarySourceWordCropRequest(
              cacheKey: resolved.cropCacheKey!,
              word: resolved.word!,
            ),
          )
          .toList(growable: false);
      final croppedImages = await cropper.cropWordImages(
        imageData: imageData,
        requests: cropRequests,
      );
      for (var i = 0; i < group.length; i++) {
        final resolved = group[i];
        final cropped = i < croppedImages.length ? croppedImages[i] : null;
        if (cropped == null || cropped.isEmpty) {
          items[resolved.index] = resolved.imageUnavailableResult;
        } else {
          await _cropCache.write(
            resolved.cropCacheKey!,
            cropped,
            persist: isWeb,
          );
          items[resolved.index] = resolved.availableResult(cropped);
        }
      }
      _traceWebTiming(
        isWeb,
        'processed page ${first.source!.id}:${first.page!.name} with ${group.length} words in ${pageStopwatch.elapsedMilliseconds} ms',
      );
      yield PrimarySourceWordsDialogData(
        items: items,
        sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
      );
    }

    _traceWebTiming(
      isWeb,
      'finished ${targets.length} targets in ${totalStopwatch.elapsedMilliseconds} ms',
    );
  }

  List<_ResolvedWordTarget> _resolveTargets(
    List<PrimarySourceWordLinkTarget> targets,
  ) {
    final resolvedTargets = <_ResolvedWordTarget>[];
    for (var index = 0; index < targets.length; index++) {
      final target = targets[index];
      final source = _referenceResolver.findSourceById(target.sourceId);
      if (source == null) {
        resolvedTargets.add(
          _ResolvedWordTarget.finalResult(
            index: index,
            initialResult: PrimarySourceWordImageResult.unavailable(
              target: target,
              reason: PrimarySourceWordImageUnavailableReason.sourceUnavailable,
            ),
          ),
        );
        continue;
      }

      final sourceTitle = source.title;
      final pageName = target.pageName;
      if (pageName == null || pageName.isEmpty) {
        resolvedTargets.add(
          _ResolvedWordTarget.finalResult(
            index: index,
            initialResult: PrimarySourceWordImageResult.unavailable(
              target: target,
              sourceTitle: sourceTitle,
              reason: PrimarySourceWordImageUnavailableReason.pageUnavailable,
            ),
          ),
        );
        continue;
      }

      final page = _referenceResolver.findPageByName(source, pageName);
      if (page == null) {
        resolvedTargets.add(
          _ResolvedWordTarget.finalResult(
            index: index,
            initialResult: PrimarySourceWordImageResult.unavailable(
              target: target,
              sourceTitle: sourceTitle,
              reason: PrimarySourceWordImageUnavailableReason.pageUnavailable,
            ),
          ),
        );
        continue;
      }

      final wordIndex = target.wordIndex;
      if (wordIndex == null ||
          wordIndex < 0 ||
          wordIndex >= page.words.length) {
        resolvedTargets.add(
          _ResolvedWordTarget.finalResult(
            index: index,
            initialResult: PrimarySourceWordImageResult.unavailable(
              target: target,
              sourceTitle: sourceTitle,
              reason: PrimarySourceWordImageUnavailableReason.wordUnavailable,
            ),
          ),
        );
        continue;
      }

      final word = page.words[wordIndex];
      final displayWordText = _wordTextFormatter.format(word).trim();
      if (!source.permissionsReceived || word.rectangles.isEmpty) {
        resolvedTargets.add(
          _ResolvedWordTarget.finalResult(
            index: index,
            initialResult: PrimarySourceWordImageResult.unavailable(
              target: target,
              sourceTitle: sourceTitle,
              displayWordText: displayWordText,
              reason: PrimarySourceWordImageUnavailableReason.imageUnavailable,
            ),
            resolvedWord: word,
          ),
        );
        continue;
      }

      resolvedTargets.add(
        _ResolvedWordTarget.pending(
          index: index,
          target: target,
          source: source,
          page: page,
          word: word,
          wordIndex: wordIndex,
          displayWordText: displayWordText,
          cropCacheKey: _cropCacheKey(
            source: source,
            page: page,
            wordIndex: wordIndex,
            word: word,
            padding: PrimarySourceWordImageCropper.defaultPadding,
          ),
        ),
      );
    }
    return resolvedTargets;
  }

  Future<bool> _applyCachedCrops(
    List<_ResolvedWordTarget> pendingTargets,
    List<PrimarySourceWordImageResult> items, {
    required bool isWeb,
  }) async {
    var changed = false;
    for (final resolved in pendingTargets) {
      final cached = await _cropCache.read(
        resolved.cropCacheKey!,
        persist: isWeb,
      );
      if (cached != null && cached.isNotEmpty) {
        items[resolved.index] = resolved.availableResult(cached);
        changed = true;
      }
    }
    return changed;
  }

  LinkedHashMap<String, List<_ResolvedWordTarget>> _groupTargetsByPage(
    List<_ResolvedWordTarget> targets,
  ) {
    final groups = LinkedHashMap<String, List<_ResolvedWordTarget>>();
    for (final target in targets) {
      groups.putIfAbsent(target.pageCacheKey, () => []).add(target);
    }
    return groups;
  }

  void _applyUnavailableGroup(
    List<_ResolvedWordTarget> group,
    List<PrimarySourceWordImageResult> items,
  ) {
    for (final resolved in group) {
      items[resolved.index] = resolved.imageUnavailableResult;
    }
  }

  String _cropCacheKey({
    required PrimarySource source,
    required model.Page page,
    required int wordIndex,
    required PageWord word,
    required int padding,
  }) {
    final rawKey =
        'v4|${source.id}|${page.name}|${page.image}|$wordIndex|$padding|'
        '${_rectanglesCacheFingerprint(word.rectangles)}';
    return base64Url.encode(utf8.encode(rawKey)).replaceAll('=', '');
  }

  String _rectanglesCacheFingerprint(List<PageRect> rectangles) {
    return rectangles
        .map(
          (rect) =>
              '${rect.startX.toStringAsFixed(6)},'
              '${rect.startY.toStringAsFixed(6)},'
              '${rect.endX.toStringAsFixed(6)},'
              '${rect.endY.toStringAsFixed(6)}',
        )
        .join(';');
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
    return DartPrimarySourceWordImageCropper().cropWordImageSync(
      imageData: imageData,
      word: word,
      padding: padding,
    );
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

class PrimarySourceWordCropRequest {
  const PrimarySourceWordCropRequest({
    required this.cacheKey,
    required this.word,
  });

  final String cacheKey;
  final PageWord word;
}

abstract class PrimarySourceWordImageCropper {
  static const int defaultPadding = 3;

  Future<List<Uint8List?>> cropWordImages({
    required Uint8List imageData,
    required List<PrimarySourceWordCropRequest> requests,
  });
}

class DartPrimarySourceWordImageCropper
    implements PrimarySourceWordImageCropper {
  @override
  Future<List<Uint8List?>> cropWordImages({
    required Uint8List imageData,
    required List<PrimarySourceWordCropRequest> requests,
  }) async {
    final sourceImage = _decodeImage(imageData);
    if (sourceImage == null) {
      return List<Uint8List?>.filled(requests.length, null, growable: false);
    }

    return requests
        .map(
          (request) => _cropWordFromDecodedImage(
            sourceImage: sourceImage,
            word: request.word,
            padding: PrimarySourceWordImageCropper.defaultPadding,
          ),
        )
        .toList(growable: false);
  }

  Uint8List? cropWordImageSync({
    required Uint8List imageData,
    required PageWord word,
    int padding = PrimarySourceWordImageCropper.defaultPadding,
  }) {
    final sourceImage = _decodeImage(imageData);
    if (sourceImage == null) {
      return null;
    }
    return _cropWordFromDecodedImage(
      sourceImage: sourceImage,
      word: word,
      padding: padding,
    );
  }

  img.Image? _decodeImage(Uint8List imageData) {
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
    return sourceImage;
  }
}

class CanvasPrimarySourceWordImageCropper
    implements PrimarySourceWordImageCropper {
  @override
  Future<List<Uint8List?>> cropWordImages({
    required Uint8List imageData,
    required List<PrimarySourceWordCropRequest> requests,
  }) async {
    final codec = await ui.instantiateImageCodec(imageData);
    try {
      final frame = await codec.getNextFrame();
      final sourceImage = frame.image;
      try {
        final results = <Uint8List?>[];
        for (final request in requests) {
          results.add(
            await _cropWordFromUiImage(
              sourceImage: sourceImage,
              word: request.word,
              padding: PrimarySourceWordImageCropper.defaultPadding,
            ),
          );
          await _yieldForWeb();
        }
        return results;
      } finally {
        sourceImage.dispose();
      }
    } finally {
      codec.dispose();
    }
  }

  Future<Uint8List?> _cropWordFromUiImage({
    required ui.Image sourceImage,
    required PageWord word,
    required int padding,
  }) async {
    if (word.rectangles.isEmpty) {
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

    final width = bounds.fold<int>(0, (total, bound) => total + bound.width);
    final height = bounds.fold<int>(
      0,
      (maxHeight, bound) => math.max(maxHeight, bound.height),
    );
    final recorder = ui.PictureRecorder();
    final canvas = ui.Canvas(
      recorder,
      ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
    );
    final paint = ui.Paint()..filterQuality = ui.FilterQuality.high;
    canvas.drawRect(
      ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
      ui.Paint()..color = const ui.Color(0xFFFFFFFF),
    );

    var nextX = 0.0;
    for (final bound in bounds) {
      canvas.drawImageRect(
        sourceImage,
        ui.Rect.fromLTWH(
          bound.left.toDouble(),
          bound.top.toDouble(),
          bound.width.toDouble(),
          bound.height.toDouble(),
        ),
        ui.Rect.fromLTWH(
          nextX,
          0,
          bound.width.toDouble(),
          bound.height.toDouble(),
        ),
        paint,
      );
      nextX += bound.width;
    }

    final picture = recorder.endRecording();
    try {
      final croppedImage = await picture.toImage(width, height);
      try {
        final byteData = await croppedImage.toByteData(
          format: ui.ImageByteFormat.png,
        );
        return byteData?.buffer.asUint8List();
      } finally {
        croppedImage.dispose();
      }
    } finally {
      picture.dispose();
    }
  }
}

class PrimarySourceWordCropCache {
  PrimarySourceWordCropCache({
    Map<String, Uint8List>? memoryCache,
    Future<SharedPreferences>? preferences,
    int maxMemoryEntries = 250,
    int maxPersistentBytes = 256 * 1024,
  }) : _memoryCache = memoryCache ?? _defaultMemoryCache,
       _preferences = preferences,
       _maxMemoryEntries = maxMemoryEntries,
       _maxPersistentBytes = maxPersistentBytes;

  static const _preferencesPrefix = 'primary_source_word_crop_v1.';
  static final LinkedHashMap<String, Uint8List> _defaultMemoryCache =
      LinkedHashMap<String, Uint8List>();

  final Map<String, Uint8List> _memoryCache;
  final Future<SharedPreferences>? _preferences;
  final int _maxMemoryEntries;
  final int _maxPersistentBytes;

  Future<Uint8List?> read(String key, {required bool persist}) async {
    final memoryHit = _memoryCache[key];
    if (memoryHit != null && memoryHit.isNotEmpty) {
      return memoryHit;
    }
    if (!persist) {
      return null;
    }

    final prefs = await (_preferences ?? SharedPreferences.getInstance());
    final encoded = prefs.getString('$_preferencesPrefix$key');
    if (encoded == null || encoded.isEmpty) {
      return null;
    }
    try {
      final bytes = Uint8List.fromList(base64Decode(encoded));
      _remember(key, bytes);
      return bytes;
    } catch (_) {
      await prefs.remove('$_preferencesPrefix$key');
      return null;
    }
  }

  Future<void> write(
    String key,
    Uint8List bytes, {
    required bool persist,
  }) async {
    if (bytes.isEmpty) {
      return;
    }
    _remember(key, bytes);
    if (!persist || bytes.length > _maxPersistentBytes) {
      return;
    }

    final prefs = await (_preferences ?? SharedPreferences.getInstance());
    await prefs.setString('$_preferencesPrefix$key', base64Encode(bytes));
  }

  void _remember(String key, Uint8List bytes) {
    if (_memoryCache is LinkedHashMap<String, Uint8List>) {
      final linked = _memoryCache;
      linked.remove(key);
      linked[key] = bytes;
      while (linked.length > _maxMemoryEntries) {
        linked.remove(linked.keys.first);
      }
      return;
    }

    _memoryCache[key] = bytes;
    if (_memoryCache.length > _maxMemoryEntries) {
      _memoryCache.remove(_memoryCache.keys.first);
    }
  }
}

class _ResolvedWordTarget {
  const _ResolvedWordTarget({
    required this.index,
    required this.initialResult,
    this.source,
    this.page,
    this.word,
    this.resolvedWord,
    this.cropCacheKey,
  });

  factory _ResolvedWordTarget.finalResult({
    required int index,
    required PrimarySourceWordImageResult initialResult,
    PageWord? resolvedWord,
  }) {
    return _ResolvedWordTarget(
      index: index,
      initialResult: initialResult,
      resolvedWord: resolvedWord,
    );
  }

  factory _ResolvedWordTarget.pending({
    required int index,
    required PrimarySourceWordLinkTarget target,
    required PrimarySource source,
    required model.Page page,
    required PageWord word,
    required int wordIndex,
    required String displayWordText,
    required String cropCacheKey,
  }) {
    return _ResolvedWordTarget(
      index: index,
      source: source,
      page: page,
      word: word,
      resolvedWord: word,
      cropCacheKey: cropCacheKey,
      initialResult: PrimarySourceWordImageResult.loading(
        target: target,
        sourceTitle: source.title,
        displayWordText: displayWordText,
      ),
    );
  }

  final int index;
  final PrimarySourceWordImageResult initialResult;
  final PrimarySource? source;
  final model.Page? page;
  final PageWord? word;
  final PageWord? resolvedWord;
  final String? cropCacheKey;

  bool get needsCrop => source != null && page != null && word != null;

  String get pageCacheKey => '${source!.id}|${page!.image}';

  PrimarySourceWordImageResult get imageUnavailableResult {
    return PrimarySourceWordImageResult.unavailable(
      target: initialResult.target,
      sourceTitle: initialResult.sourceTitle,
      displayWordText: initialResult.displayWordText,
      reason: PrimarySourceWordImageUnavailableReason.imageUnavailable,
    );
  }

  PrimarySourceWordImageResult availableResult(Uint8List imageBytes) {
    return PrimarySourceWordImageResult(
      target: initialResult.target,
      sourceTitle: initialResult.sourceTitle,
      imageBytes: imageBytes,
      displayWordText: initialResult.displayWordText,
      unavailableReason: PrimarySourceWordImageUnavailableReason.none,
    );
  }
}

Uint8List? _cropWordFromDecodedImage({
  required img.Image sourceImage,
  required PageWord word,
  required int padding,
}) {
  if (word.rectangles.isEmpty) {
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
  final rectLeft = math.min(rect.startX, rect.endX).clamp(0.0, 1.0).toDouble();
  final rectTop = math.min(rect.startY, rect.endY).clamp(0.0, 1.0).toDouble();
  final rectRight = math.max(rect.startX, rect.endX).clamp(0.0, 1.0).toDouble();
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

Future<void> _yieldForWeb() {
  return Future<void>.delayed(Duration.zero);
}

void _traceWebTiming(bool isWeb, String message) {
  if (isWeb && kDebugMode) {
    debugPrint('[PrimarySourceWordImageService] $message');
  }
}
