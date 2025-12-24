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
    this.color = Colors.grey,
    this.strokeColor = const Color.fromARGB(103, 239, 232, 9),
    this.strokeWidth = 6.0,
  });
}
