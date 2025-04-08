import 'package:flutter/material.dart';

class ImagePreviewController {
  final TransformationController _transformationController =
      TransformationController();
  double minScale = 1.0;
  double maxScale = 20.0;
  Size? imageSize;

  TransformationController get transformationController =>
      _transformationController;

  void setImageSize(Size size, double availableWidth) {
    imageSize = size;
    minScale = availableWidth / size.width;
    _transformationController.value = Matrix4.identity()..scale(minScale);
  }

  void zoomIn() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.25).clamp(minScale, maxScale);
    _transformationController.value = Matrix4.identity()..scale(newScale);
  }

  void zoomOut() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.25).clamp(minScale, maxScale);
    _transformationController.value = Matrix4.identity()..scale(newScale);
  }

  void fitToWidth() {
    if (imageSize != null) {
      _transformationController.value = Matrix4.identity()..scale(minScale);
    }
  }
}
