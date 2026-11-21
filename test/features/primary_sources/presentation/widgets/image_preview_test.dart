@Tags(['widget'])
import 'dart:async';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/verse.dart';
import '../../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('restore waits for current decoded image and a usable layout', (
    tester,
  ) async {
    final controller = ImagePreviewController(20);
    addTearDown(controller.dispose);
    final bytes = _loadPreviewBytes();
    final calls = <String>[];
    Future<void> show(
      String page,
      Completer<ui.Image> decode, {
      double width = 800,
    }) async {
      await tester.pumpWidget(
        _buildHost(
          child: Align(
            child: SizedBox(
              width: width,
              height: 600,
              child: _buildPreview(
                controller: controller,
                imageName: page,
                imageData: bytes,
                decodeImage: (_) => decode.future,
                onRestorePositionAndScale: () {
                  calls.add(page);
                  controller.setTransformParams(-12, -18, 2);
                },
              ),
            ),
          ),
        ),
      );
    }

    final first = Completer<ui.Image>();
    final second = Completer<ui.Image>();
    await show('A', first);
    await tester.pump(const Duration(seconds: 2));
    expect(calls, isEmpty);
    expect(find.byType(InteractiveViewer), findsNothing);
    await show('B', second, width: 0);
    final stale = _decoded(640, 480);
    first.complete(stale);
    final ready = _decoded(1200, 800);
    second.complete(ready);
    await tester.pump();
    expect(calls, isEmpty);
    expect(controller.imageSize, isNull);
    await show('B', second);
    await tester.pump();
    expect(calls, ['B']);
    expect(controller.imageSize, const Size(1200, 800));
    expect(controller.transformationController.value.storage[12], -12);
    expect(find.byType(InteractiveViewer), findsOneWidget);
    expect(tester.widget<RawImage>(find.byType(RawImage)).image, same(ready));
    await show('B', second);
    await tester.pump(const Duration(seconds: 2));
    expect(calls, ['B']);
    final third = Completer<ui.Image>();
    await show('C', third);
    expect(find.byType(InteractiveViewer), findsNothing);
    await tester.pumpWidget(const SizedBox());
    final late = _decoded(400, 400);
    third.complete(late);
    await tester.pump();
    expect(calls, ['B']);
    expect(stale.debugDisposed, isTrue);
    expect(ready.debugDisposed, isTrue);
    expect(late.debugDisposed, isTrue);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'failed decode leaves the viewport and its saved position untouched',
    (tester) async {
      final controller = ImagePreviewController(2);
      addTearDown(controller.dispose);
      final decode = Completer<ui.Image>();
      var restored = false;
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: _buildPreview(
            controller: controller,
            imageName: 'missing',
            imageData: _loadPreviewBytes(),
            decodeImage: (_) => decode.future,
            onRestorePositionAndScale: () => restored = true,
          ),
        ),
      );
      decode.completeError(StateError('invalid image'));
      await tester.pump();
      expect(restored, isFalse);
      expect(controller.imageSize, isNull);
      expect(find.byType(InteractiveViewer), findsNothing);
      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );

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

  testWidgets('a word under the restored zoom and offset receives the tap', (
    tester,
  ) async {
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
          onRestorePositionAndScale: () =>
              controller.setTransformParams(-50, -30, 2),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // (135, 90) in manuscript pixels after the saved scale and translation.
    await tester.tapAt(const Offset(220, 150));
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
      expect(find.byType(RawImage), findsWidgets);
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

ui.Image _decoded(int width, int height) {
  final recorder = ui.PictureRecorder();
  ui.Canvas(recorder).drawColor(const Color(0xffdddddd), BlendMode.src);
  final picture = recorder.endRecording();
  final image = picture.toImageSync(width, height);
  picture.dispose();
  return image;
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
  Future<ui.Image> Function(Uint8List)? decodeImage,
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
    decodeImage:
        decodeImage ??
        (_) async => _decoded(
          controller.imageSize!.width.toInt(),
          controller.imageSize!.height.toInt(),
        ),
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
