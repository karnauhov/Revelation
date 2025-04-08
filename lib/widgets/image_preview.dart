import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';

class ImagePreview extends StatefulWidget {
  final Uint8List imageData;

  const ImagePreview({
    required this.imageData,
    super.key,
  });

  @override
  ImagePreviewState createState() => ImagePreviewState();
}

class ImagePreviewState extends State<ImagePreview> {
  final TransformationController _transformationController =
      TransformationController();
  Size? imageSize;
  double minScale = 1.0;

  @override
  void initState() {
    super.initState();
    _decodeImage();
  }

  @override
  Widget build(BuildContext context) {
    if (imageSize == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return LayoutBuilder(
      builder: (context, constraints) {
        final availableWidth = constraints.maxWidth;
        final imageWidth = imageSize!.width;
        minScale = availableWidth / imageWidth;
        _transformationController.value = Matrix4.identity()..scale(minScale);
        return InteractiveViewer(
          transformationController: _transformationController,
          minScale: minScale,
          maxScale: 20.0,
          constrained: false,
          child: Center(
            child: Image.memory(widget.imageData),
          ),
        );
      },
    );
  }

  void fitToWidth() {
    if (imageSize != null) {
      final availableWidth = context.size!.width;
      final imageWidth = imageSize!.width;
      minScale = availableWidth / imageWidth;
      _transformationController.value = Matrix4.identity()..scale(minScale);
    }
  }

  void zoomIn() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale * 1.25).clamp(minScale, 20.0);
    _transformationController.value = Matrix4.identity()..scale(newScale);
  }

  void zoomOut() {
    final currentScale = _transformationController.value.getMaxScaleOnAxis();
    final newScale = (currentScale / 1.25).clamp(minScale, 20.0);
    _transformationController.value = Matrix4.identity()..scale(newScale);
  }

  Future<void> _decodeImage() async {
    ui.decodeImageFromList(widget.imageData, _getImage);
  }

  void _getImage(ui.Image image) {
    if (mounted) {
      setState(() {
        imageSize = Size(image.width.toDouble(), image.height.toDouble());
      });
    }
  }
}
