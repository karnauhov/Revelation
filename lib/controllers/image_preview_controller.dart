import 'dart:math';
import 'package:flutter/material.dart';

class ImagePreviewController {
  final TransformationController _transformationController =
      TransformationController();
  double minScale = 1.0;
  double maxScale = 10.0;
  Size? imageSize;

  ImagePreviewController(this.maxScale);

  TransformationController get transformationController =>
      _transformationController;

  void setImageSize(Size size, double availableWidth, double availableHeight,
      {recalc = false}) {
    if (imageSize == null || imageSize != size || recalc) {
      imageSize = size;
      minScale = availableWidth / size.width;
      if (minScale * size.height < availableHeight) {
        minScale = availableHeight / size.height;
      }
      _transformationController.value = Matrix4.identity()..scale(minScale);
    }
  }

  void setTransformParams(double dx, double dy, double scale) {
    final clampedScale = scale.clamp(minScale, maxScale);
    _transformationController.value = Matrix4.identity()
      ..translate(dx, dy)
      ..scale(clampedScale);
  }

  void zoomIn(Offset focalPoint) {
    // 1. Get the current matrix and calculate the coordinate of the focal point in image coordinates.
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);

    // 2. Calculate the new scale.
    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.25).clamp(minScale, maxScale);

    // 3. Calculate the initial offset so that the focal point remains on the screen.
    final newTranslation = focalPoint - focalImage * newScale;

    // 4. Form a new transformation matrix.
    _transformationController.value = Matrix4.identity()
      ..translate(newTranslation.dx, newTranslation.dy)
      ..scale(newScale);
  }

  void zoomOut(Offset focalPoint, Size viewportSize) {
    // 1. Get the current matrix and calculate the coordinate of the focal point in image coordinates.
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);

    // 2. Calculate the new scale.
    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.25).clamp(minScale, maxScale);

    // 3. Calculate the initial offset so that the focal point remains on the screen.
    Offset newTranslation = focalPoint - focalImage * newScale;

    // 4. Form a new transformation matrix.
    Matrix4 newMatrix = Matrix4.identity()
      ..translate(newTranslation.dx, newTranslation.dy)
      ..scale(newScale);

    // 5. Find the positions of the image corners after transformation.
    final corners = <Offset>[
      const Offset(0, 0),
      Offset(imageSize!.width, 0),
      Offset(0, imageSize!.height),
      Offset(imageSize!.width, imageSize!.height),
    ];

    final transformedCorners = corners
        .map((corner) => MatrixUtils.transformPoint(newMatrix, corner))
        .toList();

    // Calculate the image boundaries after transformation.
    final xValues = transformedCorners.map((p) => p.dx).toList();
    final yValues = transformedCorners.map((p) => p.dy).toList();
    final double xMin = xValues.reduce(min);
    final double xMax = xValues.reduce(max);
    final double yMin = yValues.reduce(min);
    final double yMax = yValues.reduce(max);
    bool initialScale = false;

    // 6. Correct the horizontal offset.
    if (imageSize!.width * newScale >= viewportSize.width) {
      if (xMin > 0) {
        newTranslation = Offset(newTranslation.dx - xMin, newTranslation.dy);
      }
      if (xMax < viewportSize.width) {
        newTranslation = Offset(
            newTranslation.dx + (viewportSize.width - xMax), newTranslation.dy);
      }
    } else {
      initialScale = true;
    }

    // 7. Correct the vertical offset.
    if (imageSize!.height * newScale >= viewportSize.height) {
      if (yMin > 0) {
        newTranslation = Offset(newTranslation.dx, newTranslation.dy - yMin);
      }
      if (yMax < viewportSize.height) {
        newTranslation = Offset(newTranslation.dx,
            newTranslation.dy + (viewportSize.height - yMax));
      }
    } else {
      initialScale = true;
    }

    // 8. Apply the updated matrix with corrected offsets.
    if (initialScale) {
      backToMinScale();
    } else {
      _transformationController.value = Matrix4.identity()
        ..translate(newTranslation.dx, newTranslation.dy)
        ..scale(newScale);
    }
  }

  void backToMinScale() {
    if (imageSize != null) {
      _transformationController.value = Matrix4.identity()..scale(minScale);
    }
  }
}
