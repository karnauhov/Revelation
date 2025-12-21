import 'package:flutter/material.dart';

class PageLine {
  final double startX;
  final double startY;
  final double endX;
  final double endY;
  final Color color;
  final double strokeWidth;

  PageLine(
    this.startX,
    this.startY,
    this.endX,
    this.endY, {
    this.color = Colors.red,
    this.strokeWidth = 6.0,
  });
}
