import 'package:flutter/material.dart';

class PageText {
  final String text;
  final double positionX;
  final double positionY;
  final double fontSizeFrac;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;

  PageText(
    this.text,
    this.positionX,
    this.positionY, {
    this.fontSizeFrac = 0.008,
    this.color = Colors.red,
    this.strokeColor = Colors.transparent,
    this.strokeWidth = 0.0,
  });
}
