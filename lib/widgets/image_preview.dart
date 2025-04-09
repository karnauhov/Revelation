import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:revelation/utils/image_preview_controller.dart';

class ImagePreview extends StatefulWidget {
  final Uint8List imageData;
  final ImagePreviewController controller;

  const ImagePreview({
    required this.imageData,
    required this.controller,
    super.key,
  });

  @override
  ImagePreviewState createState() => ImagePreviewState();
}

class ImagePreviewState extends State<ImagePreview> {
  @override
  void initState() {
    super.initState();
    _decodeImage();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (widget.controller.imageSize == null) {
          return const Center(child: CircularProgressIndicator());
        }
        widget.controller.setImageSize(widget.controller.imageSize!,
            constraints.maxWidth, constraints.maxHeight);

        return MouseRegion(
          cursor: SystemMouseCursors.grab,
          child: InteractiveViewer(
            transformationController:
                widget.controller.transformationController,
            minScale: widget.controller.minScale,
            maxScale: widget.controller.maxScale,
            constrained: false,
            child: Center(
              child: Image.memory(widget.imageData),
            ),
          ),
        );
      },
    );
  }

  Future<void> _decodeImage() async {
    ui.decodeImageFromList(widget.imageData, (ui.Image image) {
      if (mounted) {
        setState(() {
          widget.controller.setImageSize(
              Size(image.width.toDouble(), image.height.toDouble()),
              context.size!.width,
              context.size!.height);
        });
      }
    });
  }
}
