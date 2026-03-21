import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';

void main() {
  test('setImageSize computes minScale and applies initial transform', () {
    final controller = ImagePreviewController(4);

    controller.setImageSize(const Size(200, 100), 100, 100);

    expect(controller.minScale, closeTo(1.0, 0.00001));
    expect(_matrixScale(controller), closeTo(1.0, 0.00001));
    expect(_matrixOffset(controller).dx, closeTo(0, 0.00001));
    expect(_matrixOffset(controller).dy, closeTo(0, 0.00001));
  });

  test(
    'setImageSize does not reset transform for same size without recalc',
    () {
      final controller = ImagePreviewController(4);
      controller.setImageSize(const Size(200, 100), 100, 100);
      controller.setTransformParams(12, -8, 2.5);

      controller.setImageSize(const Size(200, 100), 100, 100);

      expect(_matrixScale(controller), closeTo(2.5, 0.00001));
      expect(_matrixOffset(controller).dx, closeTo(12, 0.00001));
      expect(_matrixOffset(controller).dy, closeTo(-8, 0.00001));
    },
  );

  test('setImageSize with recalc resets transform to minScale', () {
    final controller = ImagePreviewController(4);
    controller.setImageSize(const Size(200, 100), 100, 100);
    controller.setTransformParams(10, 15, 3);

    controller.setImageSize(const Size(200, 100), 100, 100, recalc: true);

    expect(_matrixScale(controller), closeTo(1.0, 0.00001));
    expect(_matrixOffset(controller).dx, closeTo(0, 0.00001));
    expect(_matrixOffset(controller).dy, closeTo(0, 0.00001));
  });

  test('setTransformParams clamps scale to [minScale, maxScale]', () {
    final controller = ImagePreviewController(3);
    controller.setImageSize(const Size(200, 100), 100, 100);

    controller.setTransformParams(0, 0, 0.1);
    expect(_matrixScale(controller), closeTo(1.0, 0.00001));

    controller.setTransformParams(0, 0, 99);
    expect(_matrixScale(controller), closeTo(3.0, 0.00001));
  });

  test('zoomIn increases scale by factor and respects maxScale', () {
    final controller = ImagePreviewController(1.6);
    controller.setImageSize(const Size(200, 200), 100, 100);

    controller.zoomIn(const Offset(20, 20));
    expect(_matrixScale(controller), closeTo(0.625, 0.00001));

    controller.setTransformParams(0, 0, 1.6);
    controller.zoomIn(const Offset(20, 20));
    expect(_matrixScale(controller), closeTo(1.6, 0.00001));
  });

  test('zoomOut returns early when image size is unknown', () {
    final controller = ImagePreviewController(4);
    controller.setTransformParams(5, 6, 2);

    controller.zoomOut(const Offset(10, 10), const Size(100, 100));

    expect(_matrixScale(controller), closeTo(2, 0.00001));
    expect(_matrixOffset(controller).dx, closeTo(5, 0.00001));
    expect(_matrixOffset(controller).dy, closeTo(6, 0.00001));
  });

  test('zoomOut falls back to backToMinScale when viewport is larger', () {
    final controller = ImagePreviewController(4);
    controller.setImageSize(const Size(100, 100), 50, 50);
    controller.setTransformParams(8, 12, 1);

    controller.zoomOut(const Offset(25, 25), const Size(300, 300));

    expect(controller.minScale, closeTo(0.5, 0.00001));
    expect(_matrixScale(controller), closeTo(0.5, 0.00001));
    expect(_matrixOffset(controller).dx, closeTo(0, 0.00001));
    expect(_matrixOffset(controller).dy, closeTo(0, 0.00001));
  });

  test(
    'backToMinScale and resetImageSize restore baseline transform state',
    () {
      final controller = ImagePreviewController(4);
      controller.setImageSize(const Size(200, 100), 100, 100);
      controller.setTransformParams(30, -10, 2);

      controller.backToMinScale();
      expect(_matrixScale(controller), closeTo(1.0, 0.00001));
      expect(_matrixOffset(controller).dx, closeTo(0, 0.00001));
      expect(_matrixOffset(controller).dy, closeTo(0, 0.00001));

      controller.resetImageSize();
      expect(controller.imageSize, isNull);
      expect(_matrixScale(controller), closeTo(1.0, 0.00001));
      expect(_matrixOffset(controller).dx, closeTo(0, 0.00001));
      expect(_matrixOffset(controller).dy, closeTo(0, 0.00001));
    },
  );

  test('public methods become safe no-ops after dispose', () {
    final controller = ImagePreviewController(4);
    controller.setImageSize(const Size(200, 100), 100, 100);
    controller.dispose();

    expect(
      () => controller.setImageSize(const Size(300, 300), 100, 100),
      returnsNormally,
    );
    expect(() => controller.setTransformParams(1, 2, 3), returnsNormally);
    expect(() => controller.zoomIn(const Offset(1, 1)), returnsNormally);
    expect(
      () => controller.zoomOut(const Offset(1, 1), const Size(100, 100)),
      returnsNormally,
    );
    expect(() => controller.backToMinScale(), returnsNormally);
    expect(() => controller.resetImageSize(), returnsNormally);
  });
}

double _matrixScale(ImagePreviewController controller) {
  return controller.transformationController.value.storage[0];
}

Offset _matrixOffset(ImagePreviewController controller) {
  final storage = controller.transformationController.value.storage;
  return Offset(storage[12], storage[13]);
}
