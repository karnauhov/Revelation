@Tags(['widget'])
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/verse.dart';

void main() {
  testWidgets(
    'ImagePreview clears stale geometry before decoding a new page image',
    (tester) async {
      final controller = ImagePreviewController(20.0);
      addTearDown(controller.dispose);

      controller.setImageSize(const Size(120, 80), 800, 600);
      final imageData = _loadPreviewBytes();

      await tester.pumpWidget(
        _buildHost(
          child: _buildPreview(
            controller: controller,
            imageName: 'page_1',
            imageData: imageData,
            onRestorePositionAndScale: () {},
          ),
        ),
      );
      await tester.pump();
      expect(controller.imageSize, const Size(120, 80));

      await tester.pumpWidget(
        _buildHost(
          child: _buildPreview(
            controller: controller,
            imageName: 'page_2',
            imageData: imageData,
            onRestorePositionAndScale: () {},
          ),
        ),
      );
      await tester.pump();

      expect(controller.imageSize, isNull);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    },
  );

  testWidgets('ImagePreview requests restore once per image lifecycle change', (
    tester,
  ) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    final imageData = _loadPreviewBytes();
    var restoreCalls = 0;

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_1',
          imageData: imageData,
          onRestorePositionAndScale: () {
            restoreCalls++;
          },
        ),
      ),
    );
    await tester.pump();
    expect(restoreCalls, 1);

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_1',
          imageData: imageData,
          onRestorePositionAndScale: () {
            restoreCalls++;
          },
        ),
      ),
    );
    await tester.pump();
    expect(restoreCalls, 1);

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_2',
          imageData: imageData,
          onRestorePositionAndScale: () {
            restoreCalls++;
          },
        ),
      ),
    );
    await tester.pump();
    expect(restoreCalls, 2);
  });

  testWidgets('select area mode reports chosen region on drag end', (
    tester,
  ) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    controller.setImageSize(const Size(800, 600), 800, 600);

    Rect? selected;
    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_area',
          imageData: _loadSolidPng(800, 600, const Color(0xFFFF0000)),
          selectAreaMode: true,
          onFinishSelectAreaMode: (rect) {
            selected = rect;
          },
          onRestorePositionAndScale: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final panDetector = tester
        .widgetList<GestureDetector>(find.byType(GestureDetector))
        .firstWhere((widget) => widget.onPanStart != null);
    panDetector.onPanStart!(
      DragStartDetails(globalPosition: const Offset(100, 120)),
    );
    panDetector.onPanUpdate!(
      DragUpdateDetails(globalPosition: const Offset(180, 210)),
    );
    panDetector.onPanEnd!(DragEndDetails());
    await tester.pump();

    expect(selected, isNotNull);
    expect(selected!.width, greaterThan(0));
    expect(selected!.height, greaterThan(0));
  });

  testWidgets('tap on verse label invokes verse callback', (tester) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    controller.setImageSize(const Size(800, 600), 800, 600);

    int? tappedVerse;
    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_verse',
          imageData: _loadSolidPng(800, 600, const Color(0xFFFFFFFF)),
          verses: const [
            Verse(
              chapterNumber: 1,
              verseNumber: 1,
              labelPosition: Offset(0.1, 0.1),
            ),
          ],
          showVerseNumbers: true,
          onVerseTap: (index) {
            tappedVerse = index;
          },
          onRestorePositionAndScale: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final tapDetector = tester
        .widgetList<GestureDetector>(find.byType(GestureDetector))
        .firstWhere((widget) => widget.onTapDown != null);
    tapDetector.onTapDown!(
      TapDownDetails(globalPosition: const Offset(120, 85)),
    );
    await tester.pump();

    expect(tappedVerse, 0);
  });

  testWidgets(
    'tap on strong number invokes strong callback before word callback',
    (tester) async {
      final controller = ImagePreviewController(20.0);
      addTearDown(controller.dispose);
      controller.setImageSize(const Size(800, 600), 800, 600);

      int? tappedStrong;
      int? tappedWord;
      final words = [
        PageWord('Word', [PageRect(0.1, 0.1, 0.2, 0.2)], sn: 123),
      ];

      await tester.pumpWidget(
        _buildHost(
          child: _buildPreview(
            controller: controller,
            imageName: 'page_strong',
            imageData: _loadSolidPng(800, 600, const Color(0xFFFFFFFF)),
            words: words,
            showStrongNumbers: true,
            onStrongNumberTap: (number) {
              tappedStrong = number;
            },
            onWordTap: (index) {
              tappedWord = index;
            },
            onRestorePositionAndScale: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final tapDetector = tester
          .widgetList<GestureDetector>(find.byType(GestureDetector))
          .firstWhere((widget) => widget.onTapDown != null);
      tapDetector.onTapDown!(
        TapDownDetails(globalPosition: const Offset(82, 58)),
      );
      await tester.pump();

      expect(tappedStrong, 123);
      expect(tappedWord, isNull);
    },
  );

  testWidgets('tap on word rect invokes word callback', (tester) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    controller.setImageSize(const Size(800, 600), 800, 600);

    int? tappedWord;
    final words = [
      PageWord('Word', [PageRect(0.1, 0.1, 0.2, 0.2)]),
    ];

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_word',
          imageData: _loadSolidPng(800, 600, const Color(0xFFFFFFFF)),
          words: words,
          onWordTap: (index) {
            tappedWord = index;
          },
          onRestorePositionAndScale: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final tapDetector = tester
        .widgetList<GestureDetector>(find.byType(GestureDetector))
        .firstWhere((widget) => widget.onTapDown != null);
    tapDetector.onTapDown!(
      TapDownDetails(globalPosition: const Offset(90, 90)),
    );
    await tester.pump();

    expect(tappedWord, 0);
  });

  testWidgets(
    'selected word overlays and color replacement branch are rendered',
    (tester) async {
      final controller = ImagePreviewController(20.0);
      addTearDown(controller.dispose);
      controller.setImageSize(const Size(200, 120), 200, 120);
      final words = <PageWord>[
        PageWord('a', [PageRect(0.1, 0.1, 0.2, 0.2)], sn: 10),
        PageWord('b', [PageRect(0.3, 0.2, 0.4, 0.3)], sn: 10),
      ];

      await tester.pumpWidget(
        _buildHost(
          child: _buildPreview(
            controller: controller,
            imageName: 'page_overlay',
            imageData: _loadSolidPng(200, 120, const Color(0xFFCCCCCC)),
            words: words,
            showWordSeparators: true,
            showStrongNumbers: true,
            isNegative: true,
            isMonochrome: true,
            replaceRegion: const Rect.fromLTWH(10, 10, 30, 20),
            tolerance: 10,
            currentDescriptionType: DescriptionKind.word,
            currentDescriptionNumber: 0,
            onRestorePositionAndScale: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(ColorFiltered), findsWidgets);
      expect(find.byType(CustomPaint), findsWidgets);
      expect(find.byType(Image), findsWidgets);
    },
  );

  testWidgets('select-area drag renders transient selection rectangle', (
    tester,
  ) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    controller.setImageSize(const Size(300, 200), 300, 200);

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_select_overlay',
          imageData: _loadSolidPng(300, 200, const Color(0xFFCCCCCC)),
          selectAreaMode: true,
          onRestorePositionAndScale: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final panDetector = tester
        .widgetList<GestureDetector>(find.byType(GestureDetector))
        .firstWhere((widget) => widget.onPanStart != null);

    panDetector.onPanStart!(DragStartDetails(globalPosition: Offset(30, 30)));
    await tester.pump();
    panDetector.onPanUpdate!(
      DragUpdateDetails(globalPosition: Offset(120, 90)),
    );
    await tester.pump();

    expect(find.byType(Container), findsWidgets);

    panDetector.onPanEnd!(DragEndDetails());
    await tester.pump();
  });

  testWidgets('strong-number selection paints highlighted strong labels', (
    tester,
  ) async {
    final controller = ImagePreviewController(20.0);
    addTearDown(controller.dispose);
    controller.setImageSize(const Size(300, 200), 300, 200);

    await tester.pumpWidget(
      _buildHost(
        child: _buildPreview(
          controller: controller,
          imageName: 'page_strong_highlight',
          imageData: _loadSolidPng(300, 200, const Color(0xFFFFFFFF)),
          words: [
            PageWord('w', [PageRect(0.1, 0.1, 0.2, 0.2)], sn: 55),
          ],
          showStrongNumbers: true,
          currentDescriptionType: DescriptionKind.strongNumber,
          currentDescriptionNumber: 55,
          onRestorePositionAndScale: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(CustomPaint), findsWidgets);
  });
}

Uint8List _loadPreviewBytes() {
  // 1x1 transparent PNG to avoid filesystem/asset dependency in widget tests.
  return Uint8List.fromList(<int>[
    0x89,
    0x50,
    0x4E,
    0x47,
    0x0D,
    0x0A,
    0x1A,
    0x0A,
    0x00,
    0x00,
    0x00,
    0x0D,
    0x49,
    0x48,
    0x44,
    0x52,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x01,
    0x08,
    0x06,
    0x00,
    0x00,
    0x00,
    0x1F,
    0x15,
    0xC4,
    0x89,
    0x00,
    0x00,
    0x00,
    0x0A,
    0x49,
    0x44,
    0x41,
    0x54,
    0x78,
    0x9C,
    0x63,
    0x00,
    0x01,
    0x00,
    0x00,
    0x05,
    0x00,
    0x01,
    0x0D,
    0x0A,
    0x2D,
    0xB4,
    0x00,
    0x00,
    0x00,
    0x00,
    0x49,
    0x45,
    0x4E,
    0x44,
    0xAE,
    0x42,
    0x60,
    0x82,
  ]);
}

Widget _buildHost({required Widget child}) {
  return MaterialApp(
    home: Scaffold(body: SizedBox(width: 800, height: 600, child: child)),
  );
}

Widget _buildPreview({
  required ImagePreviewController controller,
  required String imageName,
  required Uint8List imageData,
  required VoidCallback onRestorePositionAndScale,
  bool pipetteMode = false,
  bool selectAreaMode = false,
  bool isNegative = false,
  bool isMonochrome = false,
  bool showWordSeparators = false,
  bool showStrongNumbers = false,
  bool showVerseNumbers = false,
  Rect? replaceRegion,
  double tolerance = 0,
  List<PageWord> words = const [],
  List<Verse> verses = const [],
  DescriptionKind currentDescriptionType = DescriptionKind.info,
  int? currentDescriptionNumber,
  ValueChanged<Rect?>? onFinishSelectAreaMode,
  ValueChanged<Color?>? onFinishPipetteMode,
  ValueChanged<int>? onWordTap,
  ValueChanged<int>? onVerseTap,
  ValueChanged<int>? onStrongNumberTap,
}) {
  return ImagePreview(
    imageData: imageData,
    imageName: imageName,
    controller: controller,
    pipetteMode: pipetteMode,
    selectAreaMode: selectAreaMode,
    isNegative: isNegative,
    isMonochrome: isMonochrome,
    brightness: 0,
    contrast: 100,
    replaceRegion: replaceRegion,
    colorToReplace: const Color(0xFFFFFFFF),
    newColor: const Color(0xFFFFFFFF),
    tolerance: tolerance,
    showWordSeparators: showWordSeparators,
    showStrongNumbers: showStrongNumbers,
    showVerseNumbers: showVerseNumbers,
    words: words,
    verses: verses,
    currentDescriptionType: currentDescriptionType,
    currentDescriptionNumber: currentDescriptionNumber,
    selectedVerseIndex: null,
    onFinishSelectAreaMode: onFinishSelectAreaMode ?? (_) {},
    onFinishPipetteMode: onFinishPipetteMode ?? (_) {},
    onWordTap: onWordTap ?? (_) {},
    onVerseTap: onVerseTap ?? (_) {},
    onStrongNumberTap: onStrongNumberTap ?? (_) {},
    onRestorePositionAndScale: onRestorePositionAndScale,
  );
}

Uint8List _loadSolidPng(int width, int height, Color color) {
  final image = img.Image(width: width, height: height);
  final c = img.ColorRgba8(
    (color.r * 255).round(),
    (color.g * 255).round(),
    (color.b * 255).round(),
    (color.a * 255).round(),
  );
  img.fill(image, color: c);
  return Uint8List.fromList(img.encodePng(image));
}
