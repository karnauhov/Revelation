import 'package:flutter/material.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceViewportState {
  const PrimarySourceViewportState({
    required this.dx,
    required this.dy,
    required this.scale,
    required this.savedX,
    required this.savedY,
    required this.savedScale,
    required this.scaleAndPositionRestored,
    required this.zoomStatus,
    required this.selectedArea,
    required this.colorToReplace,
    required this.newColor,
    required this.tolerance,
    required this.pipetteMode,
    required this.selectAreaMode,
    required this.isColorToReplace,
  });

  static const PrimarySourceViewportState initial = PrimarySourceViewportState(
    dx: 0,
    dy: 0,
    scale: 1,
    savedX: 0,
    savedY: 0,
    savedScale: 0,
    scaleAndPositionRestored: false,
    zoomStatus: ZoomStatus(
      canZoomIn: false,
      canZoomOut: false,
      canReset: false,
    ),
    selectedArea: null,
    colorToReplace: Color(0xFFFFFFFF),
    newColor: Color(0xFFFFFFFF),
    tolerance: 0,
    pipetteMode: false,
    selectAreaMode: false,
    isColorToReplace: true,
  );

  final double dx;
  final double dy;
  final double scale;
  final double savedX;
  final double savedY;
  final double savedScale;
  final bool scaleAndPositionRestored;
  final ZoomStatus zoomStatus;
  final Rect? selectedArea;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;
  final bool pipetteMode;
  final bool selectAreaMode;
  final bool isColorToReplace;

  PrimarySourceViewportState copyWith({
    double? dx,
    double? dy,
    double? scale,
    double? savedX,
    double? savedY,
    double? savedScale,
    bool? scaleAndPositionRestored,
    ZoomStatus? zoomStatus,
    Rect? selectedArea,
    bool selectedAreaSet = false,
    Color? colorToReplace,
    Color? newColor,
    double? tolerance,
    bool? pipetteMode,
    bool? selectAreaMode,
    bool? isColorToReplace,
  }) {
    return PrimarySourceViewportState(
      dx: dx ?? this.dx,
      dy: dy ?? this.dy,
      scale: scale ?? this.scale,
      savedX: savedX ?? this.savedX,
      savedY: savedY ?? this.savedY,
      savedScale: savedScale ?? this.savedScale,
      scaleAndPositionRestored:
          scaleAndPositionRestored ?? this.scaleAndPositionRestored,
      zoomStatus: zoomStatus ?? this.zoomStatus,
      selectedArea: selectedAreaSet ? selectedArea : this.selectedArea,
      colorToReplace: colorToReplace ?? this.colorToReplace,
      newColor: newColor ?? this.newColor,
      tolerance: tolerance ?? this.tolerance,
      pipetteMode: pipetteMode ?? this.pipetteMode,
      selectAreaMode: selectAreaMode ?? this.selectAreaMode,
      isColorToReplace: isColorToReplace ?? this.isColorToReplace,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceViewportState &&
            runtimeType == other.runtimeType &&
            dx == other.dx &&
            dy == other.dy &&
            scale == other.scale &&
            savedX == other.savedX &&
            savedY == other.savedY &&
            savedScale == other.savedScale &&
            scaleAndPositionRestored == other.scaleAndPositionRestored &&
            zoomStatus == other.zoomStatus &&
            selectedArea == other.selectedArea &&
            colorToReplace == other.colorToReplace &&
            newColor == other.newColor &&
            tolerance == other.tolerance &&
            pipetteMode == other.pipetteMode &&
            selectAreaMode == other.selectAreaMode &&
            isColorToReplace == other.isColorToReplace;
  }

  @override
  int get hashCode => Object.hash(
    dx,
    dy,
    scale,
    savedX,
    savedY,
    savedScale,
    scaleAndPositionRestored,
    zoomStatus,
    selectedArea,
    colorToReplace,
    newColor,
    tolerance,
    pipetteMode,
    selectAreaMode,
    isColorToReplace,
  );
}
