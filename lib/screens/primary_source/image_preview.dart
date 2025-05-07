import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:vector_math/vector_math_64.dart';

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

        final vm = context.watch<PrimarySourceViewModel>();
        Widget imageWidget = Image.memory(widget.imageData);
        Widget wrapped;

        if (vm.pipetteMode) {
          wrapped = GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapDown: (TapDownDetails details) async {
              final renderBox = context.findRenderObject() as RenderBox;
              final local = renderBox.globalToLocal(details.globalPosition);
              final matrix = widget.controller.transformationController.value;
              final inverseMatrix = Matrix4.inverted(matrix);

              final localPoint = Offset(local.dx, local.dy);
              final transformed = inverseMatrix
                  .transform3(Vector3(localPoint.dx, localPoint.dy, 0));
              final px = transformed.x
                  .clamp(0, widget.controller.imageSize!.width - 1)
                  .round();
              final py = transformed.y
                  .clamp(0, widget.controller.imageSize!.height - 1)
                  .round();

              final ui.Image decoded =
                  await decodeImageFromList(widget.imageData);
              final byteData =
                  await decoded.toByteData(format: ui.ImageByteFormat.rawRgba);
              final offset = (py * decoded.width + px) * 4;
              final r = byteData!.getUint8(offset);
              final g = byteData.getUint8(offset + 1);
              final b = byteData.getUint8(offset + 2);
              final a = byteData.getUint8(offset + 3);
              final picked = Color.fromARGB(a, r, g, b);

              vm.finishPipetteMode(picked);
            },
            child: imageWidget,
          );
        } else {
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
          wrapped = imageWidget;
        }

        return MouseRegion(
          cursor: vm.pipetteMode
              ? SystemMouseCursors.precise
              : SystemMouseCursors.grab,
          child: InteractiveViewer(
            transformationController:
                widget.controller.transformationController,
            minScale: widget.controller.minScale,
            maxScale: widget.controller.maxScale,
            constrained: false,
            child: Center(
              child: wrapped,
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
