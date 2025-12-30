import 'package:flutter/material.dart';

class PageRect {
  final double startX;
  final double startY;
  final double endX;
  final double endY;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;

  PageRect(
    this.startX,
    this.startY,
    this.endX,
    this.endY, {
    this.color = Colors.transparent,
    this.strokeColor = Colors.green,
    this.strokeWidth = 2.0,
  });
}
