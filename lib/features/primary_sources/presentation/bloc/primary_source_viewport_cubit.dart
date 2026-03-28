import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_state.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceViewportCubit extends Cubit<PrimarySourceViewportState> {
  PrimarySourceViewportCubit() : super(PrimarySourceViewportState.initial);
  static const double _transformEpsilon = 0.0001;

  void markImageLoadingStarted() {
    _emitIfChanged(state.copyWith(scaleAndPositionRestored: false));
  }

  void applyViewportSettings(PageSettingsState settings) {
    _emitIfChanged(
      state.copyWith(
        dx: settings.posX,
        dy: settings.posY,
        scale: settings.scale,
        savedX: settings.posX,
        savedY: settings.posY,
        savedScale: settings.scale,
      ),
    );
  }

  void resetViewportWithNoPage() {
    _emitIfChanged(
      state.copyWith(
        dx: 0,
        dy: 0,
        scale: 0,
        savedX: 0,
        savedY: 0,
        savedScale: 0,
        scaleAndPositionRestored: true,
      ),
    );
  }

  void resetViewportAndRenderControls() {
    _emitIfChanged(
      state.copyWith(
        dx: 0,
        dy: 0,
        scale: 0,
        savedX: 0,
        savedY: 0,
        savedScale: 0,
        selectedArea: null,
        selectedAreaSet: true,
        colorToReplace: const Color(0xFFFFFFFF),
        newColor: const Color(0xFFFFFFFF),
        tolerance: 0,
      ),
    );
  }

  void setScaleAndPositionRestored(bool value) {
    _emitIfChanged(state.copyWith(scaleAndPositionRestored: value));
  }

  void updateTransform({
    required double dx,
    required double dy,
    required double scale,
    required ZoomStatus zoomStatus,
  }) {
    if (_areClose(state.dx, dx) &&
        _areClose(state.dy, dy) &&
        _areClose(state.scale, scale) &&
        state.zoomStatus == zoomStatus) {
      return;
    }
    _emitIfChanged(
      state.copyWith(dx: dx, dy: dy, scale: scale, zoomStatus: zoomStatus),
    );
  }

  void setZoomStatus(ZoomStatus status) {
    _emitIfChanged(state.copyWith(zoomStatus: status));
  }

  void startSelectAreaMode() {
    _emitIfChanged(state.copyWith(selectAreaMode: true));
  }

  void finishSelectAreaMode(Rect? selectedArea) {
    _emitIfChanged(
      state.copyWith(
        selectedArea: selectedArea,
        selectedAreaSet: true,
        selectAreaMode: false,
      ),
    );
  }

  void startPipetteMode({required bool isColorToReplace}) {
    _emitIfChanged(
      state.copyWith(pipetteMode: true, isColorToReplace: isColorToReplace),
    );
  }

  void finishPipetteMode(Color? color) {
    if (color == null) {
      _emitIfChanged(state.copyWith(pipetteMode: false));
      return;
    }

    _emitIfChanged(
      state.copyWith(
        pipetteMode: false,
        colorToReplace: state.isColorToReplace ? color : state.colorToReplace,
        newColor: state.isColorToReplace ? state.newColor : color,
      ),
    );
  }

  void applyColorReplacement({
    required Rect? selectedArea,
    required Color colorToReplace,
    required Color newColor,
    required double tolerance,
  }) {
    _emitIfChanged(
      state.copyWith(
        selectedArea: selectedArea,
        selectedAreaSet: true,
        colorToReplace: colorToReplace,
        newColor: newColor,
        tolerance: tolerance,
      ),
    );
  }

  void resetColorReplacement() {
    _emitIfChanged(
      state.copyWith(
        selectedArea: null,
        selectedAreaSet: true,
        colorToReplace: const Color(0xFFFFFFFF),
        newColor: const Color(0xFFFFFFFF),
        tolerance: 0,
      ),
    );
  }

  bool _areClose(double a, double b) {
    return (a - b).abs() <= _transformEpsilon;
  }

  void _emitIfChanged(PrimarySourceViewportState nextState) {
    if (nextState == state) {
      return;
    }
    emit(nextState);
  }
}
