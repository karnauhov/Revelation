import 'package:flutter/material.dart';

class ImagePreviewController {
  final TransformationController _transformationController =
      TransformationController();
  double minScale = 1.0;
  double maxScale = 20.0;
  Size? imageSize;

  TransformationController get transformationController =>
      _transformationController;

  void setImageSize(Size size, double availableWidth, double availableHeight) {
    imageSize = size;
    minScale = availableWidth / size.width;
    if (minScale * size.height < availableHeight) {
      minScale = availableHeight / size.height;
    }
    _transformationController.value = Matrix4.identity()..scale(minScale);
  }

  void zoomIn(Offset focalPoint) {
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);
    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.25).clamp(minScale, maxScale);
    final newTranslation = focalPoint - focalImage * newScale;
    _transformationController.value = Matrix4.identity()
      ..translate(newTranslation.dx, newTranslation.dy)
      ..scale(newScale);
  }

  void zoomOut(Offset focalPoint) {
    final matrix = _transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final focalImage = MatrixUtils.transformPoint(inverseMatrix, focalPoint);
    final currentScale = matrix.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.25).clamp(minScale, maxScale);
    final newTranslation = focalPoint - focalImage * newScale;
    _transformationController.value = Matrix4.identity()
      ..translate(newTranslation.dx, newTranslation.dy)
      ..scale(newScale);
  }

  void backToMinScale() {
    if (imageSize != null) {
      _transformationController.value = Matrix4.identity()..scale(minScale);
    }
  }
}
