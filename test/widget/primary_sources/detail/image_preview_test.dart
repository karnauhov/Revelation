@Tags(['widget'])
import 'dart:io';
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
          ),
        ),
      );
      await tester.pump();

      expect(controller.imageSize, isNull);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    },
  );
}

Uint8List _loadPreviewBytes() {
  final directory = Directory('assets/images/PrimarySources');
  final file = directory.listSync().whereType<File>().firstWhere(
    (entry) => entry.path.endsWith('.png'),
  );
  return file.readAsBytesSync();
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
    onRestorePositionAndScale: () {},
  );
}
