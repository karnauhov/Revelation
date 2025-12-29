import 'package:flutter/material.dart';

class PageLabel {
  final String text;
  final double positionX;
  final double positionY;
  final double fontSizeFrac;
  final Color color;
  final Color strokeColor;
  final double strokeWidth;

  PageLabel(
    this.text,
    this.positionX,
    this.positionY, {
    this.fontSizeFrac = 0.004,
    this.color = Colors.indigoAccent,
    this.strokeColor = Colors.transparent,
    this.strokeWidth = 0.0,
  });
}
