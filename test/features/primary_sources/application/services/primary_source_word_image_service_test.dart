import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/application/services/manuscript_greek_text_converter.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_text_formatter.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';

void main() {
  test('loadWordImages crops valid words and keeps unavailable rows', () async {
    final source = _buildSource(
      id: 'U001',
      pages: [
        model.Page(
          name: '325v',
          content: 'Rev 1',
          image: 'u001_325v.png',
          words: [
            PageWord('ΑΒ', [PageRect(0.25, 0.25, 0.75, 0.75)]),
            PageWord('No rects', const []),
          ],
        ),
      ],
    );
    final imageLoader = _FakeImageLoadingOrchestrator(_png(20, 20));
    final service = PrimarySourceWordImageService(
      referenceResolver: PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository([source]),
      ),
      imageLoadingOrchestrator: imageLoader,
      wordTextFormatter: PrimarySourceWordTextFormatter(
        manuscriptGreekTextConverter: ManuscriptGreekTextConverter(
          letterReplacements: const {'Α': 'Ⲁ', 'Β': 'Ⲃ'},
        ),
      ),
    );

    final result = await service.loadWordImages(
      targets: const [
        PrimarySourceWordLinkTarget(
          sourceId: 'U001',
          pageName: '325v',
          wordIndex: 0,
        ),
        PrimarySourceWordLinkTarget(
          sourceId: 'U001',
          pageName: '325v',
          wordIndex: 1,
        ),
        PrimarySourceWordLinkTarget(
          sourceId: 'missing',
          pageName: '325v',
          wordIndex: 0,
        ),
        PrimarySourceWordLinkTarget(sourceId: 'U001'),
        PrimarySourceWordLinkTarget(sourceId: 'U001', pageName: '325v'),
        PrimarySourceWordLinkTarget(
          sourceId: 'U001',
          pageName: 'missing',
          wordIndex: 0,
        ),
      ],
      isWeb: false,
      isMobileWeb: false,
    );

    expect(result, hasLength(6));
    expect(result[0].sourceTitle, 'Title U001');
    expect(result[0].hasImage, isTrue);
    expect(
      result[0].unavailableReason,
      PrimarySourceWordImageUnavailableReason.none,
    );
    expect(result[0].displayWordText, 'ⲀⲂ');
    expect(img.decodeImage(result[0].imageBytes!)!.width, greaterThan(0));
    expect(result[1].hasImage, isFalse);
    expect(result[1].sourceTitle, 'Title U001');
    expect(
      result[1].unavailableReason,
      PrimarySourceWordImageUnavailableReason.imageUnavailable,
    );
    expect(result[1].displayWordText, 'No rects');
    expect(result[2].hasImage, isFalse);
    expect(result[2].sourceTitle, 'missing');
    expect(
      result[2].unavailableReason,
      PrimarySourceWordImageUnavailableReason.sourceUnavailable,
    );
    expect(result[3].sourceTitle, 'Title U001');
    expect(
      result[3].unavailableReason,
      PrimarySourceWordImageUnavailableReason.pageUnavailable,
    );
    expect(result[4].sourceTitle, 'Title U001');
    expect(
      result[4].unavailableReason,
      PrimarySourceWordImageUnavailableReason.wordUnavailable,
    );
    expect(result[5].sourceTitle, 'Title U001');
    expect(
      result[5].unavailableReason,
      PrimarySourceWordImageUnavailableReason.pageUnavailable,
    );
    expect(imageLoader.loadCalls, 1);
  });

  test('cropWordImage returns null for invalid image or empty rectangles', () {
    final service = PrimarySourceWordImageService();

    expect(
      service.cropWordImage(
        imageData: Uint8List.fromList([1, 2, 3]),
        word: PageWord('Word', [PageRect(0, 0, 1, 1)]),
      ),
      isNull,
    );
    expect(
      service.cropWordImage(
        imageData: _png(10, 10),
        word: PageWord('Word', const []),
      ),
      isNull,
    );
  });

  test('cropWordImage stitches multiple rectangles in listed order', () {
    final service = PrimarySourceWordImageService();

    final croppedBytes = service.cropWordImage(
      imageData: _splitWordPng(),
      word: PageWord('Split', [
        PageRect(0.7, 0, 0.8, 0.5),
        PageRect(0, 0.5, 0.1, 1),
      ]),
      padding: 0,
    );

    final cropped = img.decodeImage(croppedBytes!);
    expect(cropped, isNotNull);
    expect(cropped!.width, 20);
    expect(cropped.height, 10);

    final firstFragmentPixel = cropped.getPixel(5, 5);
    expect(firstFragmentPixel.r, 0);
    expect(firstFragmentPixel.g, 0);
    expect(firstFragmentPixel.b, 255);

    final secondFragmentPixel = cropped.getPixel(15, 5);
    expect(secondFragmentPixel.r, 255);
    expect(secondFragmentPixel.g, 0);
    expect(secondFragmentPixel.b, 0);
  });

  test(
    'loadDialogData adds shared strong details for a single non-null strong',
    () async {
      final source = _buildSource(
        id: 'U001',
        pages: [
          model.Page(
            name: '325v',
            content: 'Rev 1',
            image: 'u001_325v.png',
            words: [
              PageWord('Alpha', [PageRect(0.25, 0.25, 0.75, 0.75)], sn: 602),
              PageWord('Beta', [PageRect(0.25, 0.25, 0.75, 0.75)], sn: 602),
              PageWord('Gamma', [PageRect(0.25, 0.25, 0.75, 0.75)], sn: 603),
              PageWord('Delta', [PageRect(0.25, 0.25, 0.75, 0.75)]),
            ],
          ),
        ],
      );
      final service = PrimarySourceWordImageService(
        referenceResolver: PrimarySourceReferenceService(
          repository: _FakePrimarySourcesDbRepository([source]),
        ),
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(_png(20, 20)),
        descriptionService: _FakeDescriptionContentService(),
      );

      final localizations = lookupAppLocalizations(const Locale('en'));
      final sameStrongData = await service.loadDialogData(
        localizations: localizations,
        targets: const [
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 0,
          ),
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 1,
          ),
        ],
        isWeb: false,
        isMobileWeb: false,
      );
      final mixedStrongData = await service.loadDialogData(
        localizations: localizations,
        targets: const [
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 0,
          ),
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 2,
          ),
        ],
        isWeb: false,
        isMobileWeb: false,
      );
      final oneStrongWithNoStrongData = await service.loadDialogData(
        localizations: localizations,
        targets: const [
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 0,
          ),
          PrimarySourceWordLinkTarget(
            sourceId: 'U001',
            pageName: '325v',
            wordIndex: 3,
          ),
        ],
        isWeb: false,
        isMobileWeb: false,
      );

      expect(sameStrongData.sharedWordDetailsMarkdown, 'shared-details');
      expect(mixedStrongData.sharedWordDetailsMarkdown, isNull);
      expect(
        oneStrongWithNoStrongData.sharedWordDetailsMarkdown,
        'shared-details',
      );
    },
  );
}

class _FakeImageLoadingOrchestrator
    extends PrimarySourceImageLoadingOrchestrator {
  _FakeImageLoadingOrchestrator(this.imageBytes);

  final Uint8List imageBytes;
  int loadCalls = 0;

  @override
  Future<PageImageLoadResult> loadPageImage({
    required String page,
    required int sourceHashCode,
    required bool isWeb,
    required bool isMobileWeb,
    required bool isReload,
    bool? previousPageLoaded,
  }) async {
    loadCalls++;
    return PageImageLoadResult(
      contentAction: ImageContentAction.replace,
      imageData: imageBytes,
      imageName: page,
      pageLoaded: true,
      refreshError: false,
    );
  }
}

class _FakePrimarySourcesDbRepository extends PrimarySourcesDbRepository {
  _FakePrimarySourcesDbRepository(this._sources);

  final List<PrimarySource> _sources;

  @override
  List<PrimarySource> getAllSourcesSync() => _sources;
}

class _FakeDescriptionContentService extends DescriptionContentService {
  @override
  DescriptionContent? buildSharedWordSupplementContent(
    AppLocalizations localizations,
    Iterable<PageWord> words,
  ) {
    final resolvedWords = words.toList(growable: false);
    if (resolvedWords.isEmpty) {
      return null;
    }

    final strongWords = resolvedWords
        .where((word) => word.sn != null)
        .toList(growable: false);
    if (strongWords.isEmpty) {
      return null;
    }

    final strongNumber = strongWords.first.sn;
    for (final word in strongWords.skip(1)) {
      if (word.sn != strongNumber) {
        return null;
      }
    }

    return const DescriptionContent(
      markdown: 'shared-details',
      kind: DescriptionKind.word,
    );
  }
}

PrimarySource _buildSource({
  required String id,
  required List<model.Page> pages,
}) {
  return PrimarySource(
    id: id,
    title: 'Title $id',
    date: '',
    content: '',
    quantity: 1,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: pages,
    attributes: const [],
    permissionsReceived: true,
  );
}

Uint8List _png(int width, int height) {
  final image = img.Image(width: width, height: height);
  img.fill(image, color: img.ColorRgb8(255, 255, 255));
  return Uint8List.fromList(img.encodePng(image));
}

Uint8List _splitWordPng() {
  final image = img.Image(width: 100, height: 20);
  img.fill(image, color: img.ColorRgb8(255, 255, 255));
  _fillRect(
    image,
    left: 70,
    top: 0,
    width: 10,
    height: 10,
    color: img.ColorRgb8(0, 0, 255),
  );
  _fillRect(
    image,
    left: 0,
    top: 10,
    width: 10,
    height: 10,
    color: img.ColorRgb8(255, 0, 0),
  );
  return Uint8List.fromList(img.encodePng(image));
}

void _fillRect(
  img.Image image, {
  required int left,
  required int top,
  required int width,
  required int height,
  required img.Color color,
}) {
  for (var y = top; y < top + height; y++) {
    for (var x = left; x < left + width; x++) {
      image.setPixel(x, y, color);
    }
  }
}
