import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:image/image.dart' as img;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:vector_math/vector_math_64.dart' as math;

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
  final String imageName;
  final ImagePreviewController controller;
  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;
  final Rect? replaceRegion;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;

  const ImagePreview({
    required this.imageData,
    required this.imageName,
    required this.controller,
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
    required this.replaceRegion,
    required this.colorToReplace,
    required this.newColor,
    required this.tolerance,
    super.key,
  });

  @override
  ImagePreviewState createState() => ImagePreviewState();
}

class ImagePreviewState extends State<ImagePreview> {
  String? _imageName;
  img.Image? _original;
  Offset? _start;
  Offset? _end;

  @override
  void initState() {
    super.initState();
    _decodeImage();
    _original = null;
    _imageName = null;
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

        final vm = context.watch<PrimarySourceViewModel>();
        Widget imageWidget;
        Widget wrapped;

        if (vm.selectAreaMode) {
          imageWidget = GestureDetector(
            onPanStart: (details) {
              final coord = _getCursorCoord(details.globalPosition);
              setState(() {
                _start = Offset(coord.x.toDouble(), coord.y.toDouble());
                _end = _start;
              });
            },
            onPanUpdate: (details) {
              final coord = _getCursorCoord(details.globalPosition);
              setState(() {
                _end = Offset(coord.x.toDouble(), coord.y.toDouble());
              });
            },
            onPanEnd: (details) {
              if (_start != null && _end != null) {
                final rect = Rect.fromPoints(_start!, _end!);
                vm.finishSelectAreaMode(rect);
                setState(() {
                  _start = null;
                  _end = null;
                });
              }
            },
            child: Stack(
              children: [
                Image.memory(widget.imageData),
                if (_start != null && _end != null)
                  Positioned(
                    left: _start!.dx < _end!.dx ? _start!.dx : _end!.dx,
                    top: _start!.dy < _end!.dy ? _start!.dy : _end!.dy,
                    width: (_start!.dx - _end!.dx).abs(),
                    height: (_start!.dy - _end!.dy).abs(),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.blue, width: 2),
                      ),
                    ),
                  ),
              ],
            ),
          );
          wrapped = imageWidget;
        } else if (vm.pipetteMode) {
          imageWidget = Image.memory(widget.imageData);
          wrapped = GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapDown: (TapDownDetails details) async {
              final coord = _getCursorCoord(details.globalPosition);
              final ui.Image decoded =
                  await decodeImageFromList(widget.imageData);
              final byteData =
                  await decoded.toByteData(format: ui.ImageByteFormat.rawRgba);
              final offset = (coord.y * decoded.width + coord.x) * 4;
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
          // Color replacement
          imageWidget = Stack(
            children: [
              Image.memory(widget.imageData),
              if (widget.tolerance > 0 && widget.replaceRegion != null)
                FutureBuilder<Uint8List>(
                  future: _createModifiedRegionImage(
                    region: widget.replaceRegion!,
                    data: widget.imageData,
                    target: widget.colorToReplace,
                    replacement: widget.newColor,
                    tolerance: widget.tolerance,
                  ),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState != ConnectionState.done ||
                        snapshot.data == null) {
                      return const SizedBox.shrink();
                    }
                    return Positioned(
                      left: widget.replaceRegion!.left,
                      top: widget.replaceRegion!.top,
                      child: Image.memory(snapshot.data!),
                    );
                  },
                ),
            ],
          );

          // Apply brightness and contrast filter
          double contrastFactor = widget.contrast / 100.0;
          double brightnessOffset = widget.brightness * 2.55;
          double offset = 128 - contrastFactor * 128 + brightnessOffset;
          List<double> brightnessContrastMatrix = [
            contrastFactor, 0, 0, 0, offset, // R
            0, contrastFactor, 0, 0, offset, // G
            0, 0, contrastFactor, 0, offset, // B
            0, 0, 0, 1, 0 // A
          ];
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
          cursor: vm.selectAreaMode
              ? SystemMouseCursors.precise
              : vm.pipetteMode
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

  LocalCoord _getCursorCoord(Offset globalPosition) {
    final renderBox = context.findRenderObject() as RenderBox;
    final local = renderBox.globalToLocal(globalPosition);
    final matrix = widget.controller.transformationController.value;
    final inverseMatrix = Matrix4.inverted(matrix);
    final localPoint = Offset(local.dx, local.dy);
    final transformed =
        inverseMatrix.transform3(math.Vector3(localPoint.dx, localPoint.dy, 0));
    final px =
        transformed.x.clamp(0, widget.controller.imageSize!.width - 1).round();
    final py =
        transformed.y.clamp(0, widget.controller.imageSize!.height - 1).round();
    return LocalCoord(px, py);
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

  Future<Uint8List> _createModifiedRegionImage({
    required Rect region,
    required Uint8List data,
    required Color target,
    required Color replacement,
    required double tolerance,
  }) async {
    if (tolerance == 0) return Uint8List(0);
    if (_imageName == null ||
        _original == null ||
        _imageName != widget.imageName) {
      _original = img.decodeImage(widget.imageData);
      _imageName = widget.imageName;
    }

    final int startX = region.left.toInt().clamp(0, _original!.width - 1);
    final int startY = region.top.toInt().clamp(0, _original!.height - 1);
    final int width =
        (region.width.toInt()).clamp(0, _original!.width - startX);
    final int height =
        (region.height.toInt()).clamp(0, _original!.height - startY);

    if (width <= 0 || height <= 0) return Uint8List(0);

    final img.Image regionImage = img.copyCrop(_original!,
        x: startX, y: startY, width: width, height: height);

    final int r0 = (target.r * 255).round();
    final int g0 = (target.g * 255).round();
    final int b0 = (target.b * 255).round();
    final int replacementR = (replacement.r * 255).round();
    final int replacementG = (replacement.g * 255).round();
    final int replacementB = (replacement.b * 255).round();
    final double tolSq = tolerance * tolerance;

    for (int y = 0; y < regionImage.height; y++) {
      for (int x = 0; x < regionImage.width; x++) {
        final img.Pixel px = regionImage.getPixel(x, y);
        final int r = px.r.toInt(), g = px.g.toInt(), b = px.b.toInt();
        final int dr = r - r0, dg = g - g0, db = b - b0;
        if (dr * dr + dg * dg + db * db <= tolSq) {
          regionImage.setPixelRgba(
              x, y, replacementR, replacementG, replacementB, px.a);
        }
      }
    }

    return Uint8List.fromList(img.encodePng(regionImage));
  }
}

class LocalCoord {
  late final int x;
  late final int y;

  LocalCoord(this.x, this.y);
}
