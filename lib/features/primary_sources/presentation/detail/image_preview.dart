import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:image/image.dart' as img;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/image_preview_controller.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/verse.dart';
import 'package:revelation/shared/utils/common.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_source_view_model.dart';
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
  final bool showWordSeparators;
  final bool showStrongNumbers;
  final bool showVerseNumbers;
  final List<PageWord> words;
  final List<Verse> verses;
  final int? selectedVerseIndex;

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
    required this.showWordSeparators,
    required this.showStrongNumbers,
    required this.showVerseNumbers,
    required this.words,
    required this.verses,
    this.selectedVerseIndex,
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
  Size? _lastContainerSize;
  List<SingleLine>? _lines;
  List<TextLabel>? _strongLabels;

  @override
  void initState() {
    super.initState();
    _decodeImage();
    _original = null;
    _imageName = null;
    _lines = _prepareWordSeparators(widget.words);
    _strongLabels = _preparStrongNumbers(widget.words);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        if (widget.controller.imageSize == null) {
          return Container(
            color: colorScheme.surface,
            child: const Center(child: CircularProgressIndicator()),
          );
        }

        final currentSize = Size(constraints.maxWidth, constraints.maxHeight);
        bool recalcAnyway = false;
        if (_lastContainerSize == null ||
            _lastContainerSize!.width != currentSize.width ||
            (_lastContainerSize!.height - currentSize.height).abs() > 40) {
          _lastContainerSize = currentSize;
          recalcAnyway = true;
        }

        widget.controller.setImageSize(
          widget.controller.imageSize!,
          constraints.maxWidth,
          constraints.maxHeight,
          recalc: recalcAnyway,
        );

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
                final rect = createNonZeroRect(_start!, _end!);
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
                        border: Border.all(
                          color: colorScheme.primary,
                          width: 2,
                        ),
                        color: colorScheme.onSurface.withValues(alpha: 0.1),
                      ),
                    ),
                  ),
              ],
            ),
          );
          wrapped = imageWidget;
        } else if (vm.pipetteMode) {
          imageWidget = Image.memory(widget.imageData);
          wrapped = imageWidget;
        } else {
          // Color replacement and filters
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
            0, 0, 0, 1, 0, // A
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

          final imgSize = widget.controller.imageSize!;
          final Widget contentStack = Center(
            child: SizedBox(
              width: imgSize.width,
              height: imgSize.height,
              child: Stack(
                children: [
                  // Base image
                  Positioned.fill(child: imageWidget),

                  if (widget.verses.isNotEmpty && widget.showVerseNumbers)
                    Positioned.fill(
                      child: CustomPaint(
                        painter: RelativeVersesPainter(
                          verses: widget.verses,
                          selectedVerseIndex: widget.selectedVerseIndex,
                        ),
                      ),
                    ),

                  // Draw multiple word separators (lines)
                  if (widget.showWordSeparators && _lines != null)
                    Positioned.fill(
                      child: CustomPaint(
                        painter: RelativeLinesPainter(lines: _lines!),
                      ),
                    ),

                  // Draw multiple Strong's numbers (texts)
                  if (widget.showStrongNumbers && _strongLabels != null)
                    Positioned.fill(
                      child: CustomPaint(
                        painter: RelativeTextsPainter(
                          texts: _strongLabels!,
                          selectedNumber:
                              (vm.currentDescriptionType ==
                                      DescriptionKind.strongNumber &&
                                  vm.currentDescriptionNumber != null)
                              ? vm.currentDescriptionNumber
                              : null,
                        ),
                      ),
                    ),

                  // Draw rectangles for selected word
                  _buildSelectedWordRects(vm),
                ],
              ),
            ),
          );

          wrapped = contentStack;
        }

        vm.restorePositionAndScale();

        // Single GestureDetector
        final Widget gestureWrapped = GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: (TapDownDetails details) async {
            if (await _handlePipetteModeTap(details.globalPosition, vm)) {
              return;
            }
            if (_handleSelectArea(vm)) {
              return;
            }
            if (_handleTapOnVerseLabels(details.globalPosition, vm)) {
              return;
            }
            if (_handleTapOnStrongNumbers(details.globalPosition, vm)) {
              return;
            }
            if (_handleTapOnWords(details.globalPosition, vm)) {
              return;
            }
          },
          child: Center(
            child: Container(color: colorScheme.surface, child: wrapped),
          ),
        );

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
            child: gestureWrapped,
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
    final transformed = inverseMatrix.transform3(
      math.Vector3(localPoint.dx, localPoint.dy, 0),
    );
    final px = transformed.x
        .clamp(0, widget.controller.imageSize!.width - 1)
        .round();
    final py = transformed.y
        .clamp(0, widget.controller.imageSize!.height - 1)
        .round();
    return LocalCoord(px, py);
  }

  void _decodeImage() {
    ui.decodeImageFromList(widget.imageData, (ui.Image image) {
      if (mounted) {
        setState(() {
          widget.controller.setImageSize(
            Size(image.width.toDouble(), image.height.toDouble()),
            context.size!.width,
            context.size!.height,
          );
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
      _original = img.decodeImage(data);
      _imageName = widget.imageName;
    }

    final int startX = region.left.toInt().clamp(0, _original!.width - 1);
    final int startY = region.top.toInt().clamp(0, _original!.height - 1);
    final int width = (region.width.toInt()).clamp(
      0,
      _original!.width - startX,
    );
    final int height = (region.height.toInt()).clamp(
      0,
      _original!.height - startY,
    );

    if (width <= 0 || height <= 0) return Uint8List(0);

    final img.Image regionImage = img.copyCrop(
      _original!,
      x: startX,
      y: startY,
      width: width,
      height: height,
    );

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
            x,
            y,
            replacementR,
            replacementG,
            replacementB,
            px.a,
          );
        }
      }
    }

    final result = Uint8List.fromList(img.encodePng(regionImage));
    return result;
  }

  Widget _buildSelectedWordRects(PrimarySourceViewModel vm) {
    if (vm.currentDescriptionType != DescriptionKind.word ||
        vm.currentDescriptionNumber == null ||
        widget.words.isEmpty) {
      return const SizedBox.shrink();
    }

    final int idx = vm.currentDescriptionNumber!;
    if (idx < 0 || idx >= widget.words.length) {
      return const SizedBox.shrink();
    }

    final selectedWord = widget.words[idx];
    final List<Widget> layers = [];

    if (selectedWord.sn != null) {
      final snRects = widget.words
          .where((w) => w.sn != null && w.sn == selectedWord.sn)
          .expand((w) => w.rectangles)
          .toList();
      if (snRects.isNotEmpty) {
        layers.add(
          Positioned.fill(
            child: CustomPaint(
              painter: RelativeRectsDashedPainter(
                rects: snRects,
                color: Colors.blue.withAlpha(45),
              ),
            ),
          ),
        );
      }
    }

    if (selectedWord.rectangles.isNotEmpty) {
      layers.add(
        Positioned.fill(
          child: CustomPaint(
            painter: RelativeRectsPainter(
              rects: selectedWord.rectangles,
              color: Colors.blue.withAlpha(25),
            ),
          ),
        ),
      );
    }

    if (layers.isEmpty) {
      return const SizedBox.shrink();
    }
    return Stack(children: layers);
  }

  Future<bool> _handlePipetteModeTap(
    Offset globalPosition,
    PrimarySourceViewModel vm,
  ) async {
    if (vm.pipetteMode) {
      final coord = _getCursorCoord(globalPosition);
      final ui.Image decoded = await decodeImageFromList(widget.imageData);
      final byteData = await decoded.toByteData(
        format: ui.ImageByteFormat.rawRgba,
      );
      if (byteData == null) {
        return false;
      }
      final offset = (coord.y * decoded.width + coord.x) * 4;
      if (offset < 0 || offset + 3 >= byteData.lengthInBytes) {
        return false;
      }
      final r = byteData.getUint8(offset);
      final g = byteData.getUint8(offset + 1);
      final b = byteData.getUint8(offset + 2);
      final a = byteData.getUint8(offset + 3);
      final picked = Color.fromARGB(a, r, g, b);
      vm.finishPipetteMode(picked);
      return true;
    }
    return false;
  }

  bool _handleSelectArea(PrimarySourceViewModel vm) {
    if (vm.selectAreaMode) {
      return true;
    }
    return false;
  }

  bool _handleTapOnVerseLabels(
    Offset globalPosition,
    PrimarySourceViewModel vm,
  ) {
    if (!widget.showVerseNumbers ||
        widget.controller.imageSize == null ||
        widget.verses.isEmpty) {
      return false;
    }

    final LocalCoord coord = _getCursorCoord(globalPosition);
    final imgSize = widget.controller.imageSize!;
    final tapPoint = Offset(coord.x.toDouble(), coord.y.toDouble());

    for (int i = 0; i < widget.verses.length; i++) {
      final verse = widget.verses[i];
      final labelRect = RelativeVersesPainter.getLabelRect(verse, imgSize);
      if (labelRect.contains(tapPoint)) {
        vm.showInfoForVerse(i, context);
        return true;
      }
    }

    return false;
  }

  bool _handleTapOnWords(Offset globalPosition, PrimarySourceViewModel vm) {
    if (widget.controller.imageSize == null) {
      return false;
    }
    if (widget.words.isEmpty) {
      return false;
    }

    final LocalCoord coord = _getCursorCoord(globalPosition);
    final imgWidth = widget.controller.imageSize!.width;
    final imgHeight = widget.controller.imageSize!.height;
    final Size imgSize = Size(imgWidth, imgHeight);
    const double extra = 4.0;

    for (int wi = 0; wi < widget.words.length; wi++) {
      final pw = widget.words[wi];
      for (final r in pw.rectangles) {
        double left, top, right, bottom;
        left = imgSize.width * r.startX;
        top = imgSize.height * r.startY;
        right = imgSize.width * r.endX;
        bottom = imgSize.height * r.endY;

        final double hitLeft = (left < right ? left : right) - extra;
        final double hitTop = (top < bottom ? top : bottom) - extra;
        final double hitRight = (left < right ? right : left) + extra;
        final double hitBottom = (top < bottom ? bottom : top) + extra;

        if (coord.x >= hitLeft &&
            coord.x <= hitRight &&
            coord.y >= hitTop &&
            coord.y <= hitBottom) {
          vm.showInfoForWord(wi, context);
          return true;
        }
      }
    }
    return false;
  }

  bool _handleTapOnStrongNumbers(
    Offset globalPosition,
    PrimarySourceViewModel vm,
  ) {
    if (widget.controller.imageSize == null) {
      return false;
    }
    if (_strongLabels == null) {
      return false;
    }
    if (!vm.showStrongNumbers) {
      return false;
    }

    final LocalCoord coord = _getCursorCoord(globalPosition);
    final imgWidth = widget.controller.imageSize!.width;
    final imgHeight = widget.controller.imageSize!.height;
    final Size imgSize = Size(imgWidth, imgHeight);

    for (final t in _strongLabels!) {
      final double fontSize = imgSize.height * t.fontSizeFrac;
      final double dx = imgSize.width * t.positionX + (fontSize * 0.2);
      final double dy = imgSize.height * t.positionY - (fontSize * 1.2);
      final TextPainter tp = TextPainter(
        text: TextSpan(
          text: t.text,
          style: TextStyle(fontSize: fontSize, fontWeight: FontWeight.w700),
        ),
        textDirection: TextDirection.ltr,
      );
      tp.layout();
      final double left = dx;
      final double top = dy;
      final double right = left + tp.width;
      final double bottom = top + tp.height;
      const double extra = 4.0;
      final hitLeft = left - extra;
      final hitTop = top - extra;
      final hitRight = right + extra;
      final hitBottom = bottom + extra;

      if (coord.x >= hitLeft &&
          coord.x <= hitRight &&
          coord.y >= hitTop &&
          coord.y <= hitBottom) {
        final int? number = int.tryParse(t.text);
        if (number != null) {
          vm.showInfoForStrongNumber(number, context);
          return true;
        }
      }
    }
    return false;
  }

  List<SingleLine> _prepareWordSeparators(List<PageWord> words) {
    List<SingleLine> result = [];
    for (var word in words) {
      if (word.rectangles.isNotEmpty) {
        SingleLine firstLine = SingleLine(
          word.rectangles[0].startX,
          word.rectangles[0].startY,
          word.rectangles[0].startX,
          word.rectangles[0].endY,
        );
        SingleLine lastLine = SingleLine(
          word.rectangles[word.rectangles.length - 1].endX,
          word.rectangles[word.rectangles.length - 1].startY,
          word.rectangles[word.rectangles.length - 1].endX,
          word.rectangles[word.rectangles.length - 1].endY,
        );
        result.add(firstLine);
        result.add(lastLine);
      }
    }
    return result;
  }

  List<TextLabel> _preparStrongNumbers(List<PageWord> words) {
    List<TextLabel> result = [];
    for (var word in words) {
      if (word.sn != null && word.rectangles.isNotEmpty) {
        TextLabel strongLabel = TextLabel(
          word.sn.toString(),
          word.rectangles[0].startX + word.snXshift,
          word.rectangles[0].startY,
        );
        result.add(strongLabel);
      }
    }
    return result;
  }
}

class LocalCoord {
  late final int x;
  late final int y;

  LocalCoord(this.x, this.y);
}

class SingleLine {
  final double startX;
  final double startY;
  final double endX;
  final double endY;
  final Color color;
  final double strokeWidth;

  SingleLine(
    this.startX,
    this.startY,
    this.endX,
    this.endY, {
    this.color = Colors.red,
    this.strokeWidth = 6.0,
  });
}

class TextLabel {
  final String text;
  final double positionX;
  final double positionY;
  final double fontSizeFrac;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;

  TextLabel(
    this.text,
    this.positionX,
    this.positionY, {
    this.fontSizeFrac = 0.004,
    this.color = Colors.indigoAccent,
    this.strokeColor = Colors.transparent,
    this.strokeWidth = 0.0,
  });
}

class RelativeLinesPainter extends CustomPainter {
  final List<SingleLine> lines;

  RelativeLinesPainter({required this.lines});

  @override
  void paint(Canvas canvas, Size size) {
    for (final l in lines) {
      final Offset start = Offset(
        size.width * l.startX,
        size.height * l.startY,
      );
      final Offset end = Offset(size.width * l.endX, size.height * l.endY);

      final paint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = l.strokeWidth
        ..strokeCap = StrokeCap.round
        ..color = l.color;

      canvas.drawLine(start, end, paint);
    }
  }

  @override
  bool shouldRepaint(covariant RelativeLinesPainter old) {
    return old.lines != lines;
  }
}

class RelativeVersesPainter extends CustomPainter {
  final List<Verse> verses;
  final int? selectedVerseIndex;
  static const Color _strokeColor = Color(0xFF0B8A5A);
  static const double _strokeWidth = 3.0;
  static const double _labelFontSize = 26.0;
  static const double _labelPadX = 4.0;
  static const double _labelPadY = 2.0;

  RelativeVersesPainter({required this.verses, this.selectedVerseIndex});

  static String verseLabel(Verse verse) {
    return '${verse.chapterNumber}:${verse.verseNumber}';
  }

  static TextPainter _buildLabelPainter(
    Verse verse, {
    Color color = _strokeColor,
  }) {
    final tp = TextPainter(
      text: TextSpan(
        text: verseLabel(verse),
        style: TextStyle(
          color: color,
          fontSize: _labelFontSize,
          fontWeight: FontWeight.w700,
          height: 1.0,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    tp.layout();
    return tp;
  }

  static Rect getLabelRect(Verse verse, Size size) {
    final textPainter = _buildLabelPainter(verse);
    final rawX = verse.labelPosition.dx * size.width;
    final rawY = verse.labelPosition.dy * size.height;
    final textX = rawX.clamp(
      0.0,
      size.width - textPainter.width - (_labelPadX * 2),
    );
    final textY = rawY.clamp(
      0.0,
      size.height - textPainter.height - (_labelPadY * 2),
    );
    return Rect.fromLTWH(
      textX - _labelPadX,
      textY - _labelPadY,
      textPainter.width + (_labelPadX * 2),
      textPainter.height + (_labelPadY * 2),
    );
  }

  @override
  void paint(Canvas canvas, Size size) {
    final strokePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _strokeWidth
      ..strokeJoin = StrokeJoin.miter
      ..strokeCap = StrokeCap.square
      ..color = _strokeColor;
    final haloPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _strokeWidth + 1.8
      ..strokeJoin = StrokeJoin.miter
      ..strokeCap = StrokeCap.square
      ..color = _strokeColor.withValues(alpha: 0.28);
    final fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = _strokeColor.withValues(alpha: 0.12);

    for (int i = 0; i < verses.length; i++) {
      final verse = verses[i];
      final bool isSelected =
          selectedVerseIndex != null && selectedVerseIndex == i;

      if (isSelected) {
        for (final contour in verse.contours) {
          if (contour.length < 2) {
            continue;
          }
          final path = Path();
          path.moveTo(
            contour.first.dx * size.width,
            contour.first.dy * size.height,
          );
          for (var j = 1; j < contour.length; j++) {
            path.lineTo(
              contour[j].dx * size.width,
              contour[j].dy * size.height,
            );
          }
          path.close();
          canvas.drawPath(path, fillPaint);
          canvas.drawPath(path, haloPaint);
          canvas.drawPath(path, strokePaint);
        }
      }

      _paintVerseLabel(canvas, size, verse, selected: isSelected);
    }
  }

  void _paintVerseLabel(
    Canvas canvas,
    Size size,
    Verse verse, {
    required bool selected,
  }) {
    final textPainter = _buildLabelPainter(
      verse,
      color: selected ? Colors.white : _strokeColor,
    );
    final rect = getLabelRect(verse, size);
    final bgRect = RRect.fromRectAndRadius(rect, const Radius.circular(3));

    final bgPaint = Paint()
      ..color = selected
          ? _strokeColor.withValues(alpha: 0.95)
          : Colors.white.withValues(alpha: 0.82);
    final borderPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = selected ? 1.3 : 1
      ..color = _strokeColor.withValues(alpha: 0.95);

    canvas.drawRRect(bgRect, bgPaint);
    canvas.drawRRect(bgRect, borderPaint);
    textPainter.paint(
      canvas,
      Offset(rect.left + _labelPadX, rect.top + _labelPadY),
    );
  }

  @override
  bool shouldRepaint(covariant RelativeVersesPainter oldDelegate) {
    return oldDelegate.verses != verses ||
        oldDelegate.selectedVerseIndex != selectedVerseIndex;
  }
}

class RelativeTextsPainter extends CustomPainter {
  final List<TextLabel> texts;
  final int? selectedNumber;

  RelativeTextsPainter({required this.texts, this.selectedNumber});

  @override
  void paint(Canvas canvas, Size size) {
    for (final t in texts) {
      final double fontSize = size.height * t.fontSizeFrac;
      final double dx = size.width * t.positionX + (fontSize * 0.2);
      final double dy = size.height * t.positionY - (fontSize * 1.2);

      final Offset offset = Offset(dx, dy);

      final int? number = int.tryParse(t.text);
      final bool isSelected =
          selectedNumber != null && number != null && number == selectedNumber;

      if (t.strokeWidth > 0 && t.strokeColor.a > 0) {
        final TextPainter strokePainter = TextPainter(
          text: TextSpan(
            text: t.text,
            style: TextStyle(
              fontSize: fontSize,
              foreground: Paint()
                ..style = PaintingStyle.stroke
                ..strokeWidth = t.strokeWidth
                ..color = isSelected ? Colors.red : t.strokeColor,
              fontWeight: FontWeight.w700,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        strokePainter.layout();
        final Offset centered = Offset(offset.dx, offset.dy);
        strokePainter.paint(canvas, centered);
      }

      final TextPainter fillPainter = TextPainter(
        text: TextSpan(
          text: t.text,
          style: TextStyle(
            fontSize: fontSize,
            color: isSelected ? Colors.red : t.color,
            fontWeight: FontWeight.w700,
            shadows: const [
              Shadow(
                blurRadius: 1.0,
                offset: Offset(0.5, 0.5),
                color: Color(0x44000000),
              ),
            ],
          ),
        ),
        textDirection: TextDirection.ltr,
      );
      fillPainter.layout();
      final Offset centeredFill = Offset(offset.dx, offset.dy);
      fillPainter.paint(canvas, centeredFill);
    }
  }

  @override
  bool shouldRepaint(covariant RelativeTextsPainter old) {
    return old.texts != texts || old.selectedNumber != selectedNumber;
  }
}

class RelativeRectsDashedPainter extends CustomPainter {
  final List<PageRect> rects;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;
  final double dashWidth;
  final double gapWidth;

  RelativeRectsDashedPainter({
    required this.rects,
    this.color = Colors.transparent,
    this.strokeColor = Colors.green,
    this.strokeWidth = 2.0,
    this.dashWidth = 6.0,
    this.gapWidth = 3.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final Paint strokePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..color = strokeColor;

    for (final r in rects) {
      final double left = size.width * r.startX;
      final double top = size.height * r.startY;
      final double right = size.width * r.endX;
      final double bottom = size.height * r.endY;

      final Rect rect = Rect.fromLTRB(
        left < right ? left : right,
        top < bottom ? top : bottom,
        left < right ? right : left,
        top < bottom ? bottom : top,
      );

      if (color.a > 0) {
        final Paint fillPaint = Paint()
          ..style = PaintingStyle.fill
          ..color = color;
        canvas.drawRect(rect, fillPaint);
      }

      _drawDashedRect(canvas, rect, strokePaint, dashWidth, gapWidth);
    }
  }

  void _drawDashedRect(
    Canvas canvas,
    Rect rect,
    Paint paint,
    double dashW,
    double gapW,
  ) {
    _drawDashedLine(
      canvas,
      Offset(rect.left, rect.top),
      Offset(rect.right, rect.top),
      paint,
      dashW,
      gapW,
    );
    _drawDashedLine(
      canvas,
      Offset(rect.right, rect.top),
      Offset(rect.right, rect.bottom),
      paint,
      dashW,
      gapW,
    );
    _drawDashedLine(
      canvas,
      Offset(rect.right, rect.bottom),
      Offset(rect.left, rect.bottom),
      paint,
      dashW,
      gapW,
    );
    _drawDashedLine(
      canvas,
      Offset(rect.left, rect.bottom),
      Offset(rect.left, rect.top),
      paint,
      dashW,
      gapW,
    );
  }

  void _drawDashedLine(
    Canvas canvas,
    Offset p1,
    Offset p2,
    Paint paint,
    double dashW,
    double gapW,
  ) {
    final double totalLength = (p2 - p1).distance;
    if (totalLength <= 0) return;
    final Offset direction = (p2 - p1) / totalLength;
    double drawn = 0.0;
    while (drawn < totalLength) {
      final double remaining = totalLength - drawn;
      final double len = remaining < dashW ? remaining : dashW;
      final Offset start = p1 + direction * drawn;
      final Offset end = p1 + direction * (drawn + len);
      canvas.drawLine(start, end, paint);
      drawn += dashW + gapW;
    }
  }

  @override
  bool shouldRepaint(covariant RelativeRectsDashedPainter old) {
    return old.rects != rects ||
        old.strokeColor != strokeColor ||
        old.strokeWidth != strokeWidth ||
        old.dashWidth != dashWidth ||
        old.gapWidth != gapWidth;
  }
}

class RelativeRectsPainter extends CustomPainter {
  final List<PageRect> rects;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;

  RelativeRectsPainter({
    required this.rects,
    this.color = Colors.transparent,
    this.strokeColor = Colors.green,
    this.strokeWidth = 2.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final r in rects) {
      final double left = size.width * r.startX;
      final double top = size.height * r.startY;
      final double right = size.width * r.endX;
      final double bottom = size.height * r.endY;

      final Rect rect = Rect.fromLTRB(
        left < right ? left : right,
        top < bottom ? top : bottom,
        left < right ? right : left,
        top < bottom ? bottom : top,
      );

      // Fill
      if (color.a > 0) {
        final Paint fillPaint = Paint()
          ..style = PaintingStyle.fill
          ..color = color;
        canvas.drawRect(rect, fillPaint);
      }

      // Stroke
      if (strokeWidth > 0 && strokeColor.a > 0) {
        final Paint strokePaint = Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = strokeWidth
          ..color = strokeColor;
        canvas.drawRect(rect, strokePaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant RelativeRectsPainter old) {
    return old.rects != rects;
  }
}
