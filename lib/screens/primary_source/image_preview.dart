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

const grayscaleMatrix = <double>[
  0.2126, 0.7152, 0.0722, 0, 0, // R
  0.2126, 0.7152, 0.0722, 0, 0, // G
  0.2126, 0.7152, 0.0722, 0, 0, // B
  0, 0, 0, 1, 0, // A
];

class ImagePreview extends StatefulWidget {
  final Uint8List imageData;
  final ImagePreviewController controller;
  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;

  const ImagePreview({
    required this.imageData,
    required this.controller,
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
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

        // Calculate brightness and contrast adjustments
        double contrastFactor = widget.contrast / 100.0;
        double brightnessOffset = widget.brightness * 2.55;
        double offset = 128 - contrastFactor * 128 + brightnessOffset;
        List<double> brightnessContrastMatrix = [
          contrastFactor, 0, 0, 0, offset, //R
          0, contrastFactor, 0, 0, offset, //G
          0, 0, contrastFactor, 0, offset, //B
          0, 0, 0, 1, 0 //A
        ];

        Widget imageWidget = Image.memory(widget.imageData);

        // Apply brightness and contrast filter
        imageWidget = ColorFiltered(
          colorFilter: ColorFilter.matrix(brightnessContrastMatrix),
          child: imageWidget,
        );

        // Apply invert filter if enabled
        if (widget.isNegative) {
          imageWidget = ColorFiltered(
            colorFilter: const ColorFilter.matrix(invertMatrix),
            child: imageWidget,
          );
        }

        // Apply monochrome filter if enabled
        if (widget.isMonochrome) {
          imageWidget = ColorFiltered(
            colorFilter: const ColorFilter.matrix(grayscaleMatrix),
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
