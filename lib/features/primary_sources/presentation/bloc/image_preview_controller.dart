import 'dart:math';
import 'package:flutter/material.dart';

class ImagePreviewController {
  final TransformationController _transformationController =
      TransformationController();
  double minScale = 1.0;
  double maxScale = 10.0;
  Size? imageSize;
  bool _isDisposed = false;

  ImagePreviewController(this.maxScale);

  TransformationController get transformationController =>
      _transformationController;

  void setImageSize(
    Size size,
    double availableWidth,
    double availableHeight, {
    recalc = false,
  }) {
    if (_isDisposed) {
      return;
    }
    if (imageSize == null || imageSize != size || recalc) {
      imageSize = size;
      minScale = availableWidth / size.width;
      if (minScale * size.height < availableHeight) {
        minScale = availableHeight / size.height;
      }
      _transformationController.value = Matrix4.identity()
        ..scaleByDouble(minScale, minScale, minScale, 1.0);
    }
  }

  void setTransformParams(double dx, double dy, double scale) {
    if (_isDisposed) {
      return;
    }
    final clampedScale = scale.clamp(minScale, maxScale);
    _transformationController.value = Matrix4.identity()
      ..translateByDouble(dx, dy, 0.0, 1.0)
      ..scaleByDouble(clampedScale, clampedScale, clampedScale, 1.0);
  }

  void zoomIn(Offset focalPoint) {
    if (_isDisposed) {
      return;
    }
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);

    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.25).clamp(minScale, maxScale);
    final newTranslation = focalPoint - focalImage * newScale;

    _transformationController.value = Matrix4.identity()
      ..translateByDouble(newTranslation.dx, newTranslation.dy, 0.0, 1.0)
      ..scaleByDouble(newScale, newScale, newScale, 1.0);
  }

  void zoomOut(Offset focalPoint, Size viewportSize) {
    if (_isDisposed || imageSize == null) {
      return;
    }
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);

    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.25).clamp(minScale, maxScale);

    Offset newTranslation = focalPoint - focalImage * newScale;
    Matrix4 newMatrix = Matrix4.identity()
      ..translateByDouble(newTranslation.dx, newTranslation.dy, 0.0, 1.0)
      ..scaleByDouble(newScale, newScale, newScale, 1.0);

    final corners = <Offset>[
      const Offset(0, 0),
      Offset(imageSize!.width, 0),
      Offset(0, imageSize!.height),
      Offset(imageSize!.width, imageSize!.height),
    ];

    final transformedCorners = corners
        .map((corner) => MatrixUtils.transformPoint(newMatrix, corner))
        .toList();

    final xValues = transformedCorners.map((p) => p.dx).toList();
    final yValues = transformedCorners.map((p) => p.dy).toList();
    final double xMin = xValues.reduce(min);
    final double xMax = xValues.reduce(max);
    final double yMin = yValues.reduce(min);
    final double yMax = yValues.reduce(max);
    bool initialScale = false;

    if (imageSize!.width * newScale >= viewportSize.width) {
      if (xMin > 0) {
        newTranslation = Offset(newTranslation.dx - xMin, newTranslation.dy);
      }
      if (xMax < viewportSize.width) {
        newTranslation = Offset(
          newTranslation.dx + (viewportSize.width - xMax),
          newTranslation.dy,
        );
      }
    } else {
      initialScale = true;
    }

    if (imageSize!.height * newScale >= viewportSize.height) {
      if (yMin > 0) {
        newTranslation = Offset(newTranslation.dx, newTranslation.dy - yMin);
      }
      if (yMax < viewportSize.height) {
        newTranslation = Offset(
          newTranslation.dx,
          newTranslation.dy + (viewportSize.height - yMax),
        );
      }
    } else {
      initialScale = true;
    }

    if (initialScale) {
      backToMinScale();
    } else {
      _transformationController.value = Matrix4.identity()
        ..translateByDouble(newTranslation.dx, newTranslation.dy, 0.0, 1.0)
        ..scaleByDouble(newScale, newScale, newScale, 1.0);
    }
  }

  void backToMinScale() {
    if (_isDisposed) {
      return;
    }
    if (imageSize != null) {
      _transformationController.value = Matrix4.identity()
        ..scaleByDouble(minScale, minScale, minScale, 1.0);
    }
  }

  void resetImageSize() {
    if (_isDisposed) {
      return;
    }
    imageSize = null;
    _transformationController.value = Matrix4.identity();
  }

  void dispose() {
    _isDisposed = true;
    _transformationController.dispose();
  }
}
