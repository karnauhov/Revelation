@Tags(['widget'])
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/shared/models/description_kind.dart';

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
}) {
  return ImagePreview(
    imageData: imageData,
    imageName: imageName,
    controller: controller,
    pipetteMode: false,
    selectAreaMode: false,
    isNegative: false,
    isMonochrome: false,
    brightness: 0,
    contrast: 100,
    replaceRegion: null,
    colorToReplace: const Color(0xFFFFFFFF),
    newColor: const Color(0xFFFFFFFF),
    tolerance: 0,
    showWordSeparators: false,
    showStrongNumbers: false,
    showVerseNumbers: false,
    words: const [],
    verses: const [],
    currentDescriptionType: DescriptionKind.info,
    currentDescriptionNumber: null,
    selectedVerseIndex: null,
    onFinishSelectAreaMode: (_) {},
    onFinishPipetteMode: (_) {},
    onWordTap: (_) {},
    onVerseTap: (_) {},
    onStrongNumberTap: (_) {},
    onRestorePositionAndScale: onRestorePositionAndScale,
  );
}
