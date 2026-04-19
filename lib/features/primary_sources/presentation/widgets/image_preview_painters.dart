import 'package:flutter/material.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/verse.dart';

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
    this.strokeColor = Colors.red,
    this.strokeWidth = 3.0,
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

      if (color.a > 0) {
        final Paint fillPaint = Paint()
          ..style = PaintingStyle.fill
          ..color = color;
        canvas.drawRect(rect, fillPaint);
      }

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
