import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:revelation/controllers/image_preview_controller.dart';

const invertMatrix = <double>[
  -1, 0, 0, 0, 255, // R = 255 - R
  0, -1, 0, 0, 255, // G = 255 - G
  0, 0, -1, 0, 255, // B = 255 - B
  0, 0, 0, 1, 0, // A = A
];

class ImagePreview extends StatefulWidget {
  final Uint8List imageData;
  final ImagePreviewController controller;
  final bool isNegative;

  const ImagePreview({
    required this.imageData,
    required this.controller,
    required this.isNegative,
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

        Widget imageWidget = Image.memory(widget.imageData);
        if (widget.isNegative) {
          imageWidget = ColorFiltered(
            colorFilter: const ColorFilter.matrix(invertMatrix),
            child: imageWidget,
          );
        }

        return MouseRegion(
          cursor: SystemMouseCursors.grab,
          child: InteractiveViewer(
            transformationController:
                widget.controller.transformationController,
            minScale: widget.controller.minScale,
            maxScale: widget.controller.maxScale,
            constrained: false,
            child: Center(
              child: imageWidget,
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
