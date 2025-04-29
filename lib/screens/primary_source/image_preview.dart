import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:revelation/utils/common.dart';

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
  ui.Image? _decodedImage;
  late bool _isMobileWeb;
  late int _maxTextureSize;
  bool _flagsLoaded = false;
  bool _startedDecoding = false;

  @override
  void initState() {
    super.initState();
    _initFlags();
  }

  Future<void> _initFlags() async {
    _isMobileWeb = isWeb() && isMobileBrowser();
    if (_isMobileWeb) {
      _maxTextureSize = await fetchMaxTextureSize();
      log.i(
          "A mobile browser with max texture size of $_maxTextureSize was detected.");
    } else {
      _maxTextureSize = 0;
    }
    setState(() => _flagsLoaded = true);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      if (!_flagsLoaded) {
        return const Center(child: CircularProgressIndicator());
      }
      if (_isMobileWeb) {
        if (_decodedImage == null) {
          if (!_startedDecoding) {
            _startedDecoding = true;
            _decodeForMobileBrowser(constraints);
          }
          return const Center(child: CircularProgressIndicator());
        }
      } else {
        if (widget.controller.imageSize == null) {
          if (!_startedDecoding) {
            _startedDecoding = true;
            _decodeForRestCases(constraints);
          }
          return const Center(child: CircularProgressIndicator());
        }
      }

      final child = _isMobileWeb
          ? RawImage(image: _decodedImage!)
          : Image.memory(widget.imageData);

      return MouseRegion(
        cursor: SystemMouseCursors.grab,
        child: InteractiveViewer(
          transformationController: widget.controller.transformationController,
          minScale: widget.controller.minScale,
          maxScale: widget.controller.maxScale,
          constrained: false,
          child: Center(child: child),
        ),
      );
    });
  }

  void _decodeForMobileBrowser(BoxConstraints c) {
    final maxSize = _maxTextureSize;
    final w = c.maxWidth.toInt().clamp(1, maxSize);
    final h = c.maxHeight.toInt().clamp(1, maxSize);

    ui
        .instantiateImageCodec(
          widget.imageData,
          targetWidth: w,
          targetHeight: h,
        )
        .then((codec) => codec.getNextFrame())
        .then((frame) {
      if (!mounted) return;
      setState(() {
        _decodedImage = frame.image;
        widget.controller.setImageSize(
          Size(frame.image.width.toDouble(), frame.image.height.toDouble()),
          w.toDouble(),
          h.toDouble(),
        );
      });
    });
  }

  void _decodeForRestCases(BoxConstraints c) {
    ui.decodeImageFromList(widget.imageData, (img) {
      if (!mounted) return;
      setState(() {
        widget.controller.setImageSize(
          Size(img.width.toDouble(), img.height.toDouble()),
          c.maxWidth,
          c.maxHeight,
        );
      });
    });
  }
}
