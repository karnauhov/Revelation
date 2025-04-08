import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';

class ImagePreview extends StatefulWidget {
  final Uint8List imageData;
  final TransformationController controller;

  const ImagePreview({
    required this.imageData,
    required this.controller,
    super.key,
  });

  @override
  ImagePreviewState createState() => ImagePreviewState();
}

class ImagePreviewState extends State<ImagePreview> {
  Size? imageSize;

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
        final scale = availableWidth / imageWidth;
        widget.controller.value = Matrix4.identity()..scale(scale);
        return InteractiveViewer(
          transformationController: widget.controller,
          minScale: scale,
          maxScale: 20.0,
          constrained: false,
          child: Center(
            child: Image.memory(widget.imageData),
          ),
        );
      },
    );
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
