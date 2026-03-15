import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/shared/models/zoom_status.dart';

void main() {
  test('initial state contains default viewport and render controls', () {
    final cubit = PrimarySourceViewportCubit();
    addTearDown(cubit.close);

    expect(cubit.state.dx, 0);
    expect(cubit.state.dy, 0);
    expect(cubit.state.scale, 1);
    expect(cubit.state.savedScale, 0);
    expect(cubit.state.scaleAndPositionRestored, isFalse);
    expect(cubit.state.selectedArea, isNull);
    expect(cubit.state.pipetteMode, isFalse);
    expect(cubit.state.selectAreaMode, isFalse);
    expect(cubit.state.tolerance, 0);
  });

  test('applyViewportSettings and updateTransform update viewport metrics', () {
    final cubit = PrimarySourceViewportCubit();
    addTearDown(cubit.close);

    cubit.applyViewportSettings(
      const PageSettingsState(
        rawSettings: 'raw',
        posX: 10,
        posY: 20,
        scale: 1.5,
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      ),
    );
    cubit.setScaleAndPositionRestored(true);
    cubit.updateTransform(
      dx: 12,
      dy: 24,
      scale: 2,
      zoomStatus: const ZoomStatus(
        canZoomIn: true,
        canZoomOut: true,
        canReset: true,
      ),
    );

    expect(cubit.state.savedX, 10);
    expect(cubit.state.savedY, 20);
    expect(cubit.state.savedScale, 1.5);
    expect(cubit.state.dx, 12);
    expect(cubit.state.dy, 24);
    expect(cubit.state.scale, 2);
    expect(cubit.state.scaleAndPositionRestored, isTrue);
    expect(cubit.state.zoomStatus.canZoomIn, isTrue);
  });

  test('selection and pipette modes update render controls', () {
    final cubit = PrimarySourceViewportCubit();
    addTearDown(cubit.close);

    final area = Rect.fromLTWH(1, 2, 3, 4);
    cubit.startSelectAreaMode();
    cubit.finishSelectAreaMode(area);
    expect(cubit.state.selectAreaMode, isFalse);
    expect(cubit.state.selectedArea, area);

    cubit.startPipetteMode(isColorToReplace: true);
    cubit.finishPipetteMode(const Color(0xFF000000));
    expect(cubit.state.pipetteMode, isFalse);
    expect(cubit.state.colorToReplace, const Color(0xFF000000));

    cubit.startPipetteMode(isColorToReplace: false);
    cubit.finishPipetteMode(const Color(0xFF00FF00));
    expect(cubit.state.newColor, const Color(0xFF00FF00));

    cubit.applyColorReplacement(
      selectedArea: area,
      colorToReplace: const Color(0xFF112233),
      newColor: const Color(0xFF445566),
      tolerance: 32,
    );
    expect(cubit.state.tolerance, 32);

    cubit.resetColorReplacement();
    expect(cubit.state.selectedArea, isNull);
    expect(cubit.state.colorToReplace, const Color(0xFFFFFFFF));
    expect(cubit.state.newColor, const Color(0xFFFFFFFF));
    expect(cubit.state.tolerance, 0);
  });

  test('updateTransform ignores unchanged transform values', () {
    final cubit = PrimarySourceViewportCubit();
    addTearDown(cubit.close);

    const status = ZoomStatus(
      canZoomIn: true,
      canZoomOut: true,
      canReset: true,
    );
    final initialState = cubit.state;
    cubit.updateTransform(dx: 12, dy: 24, scale: 2, zoomStatus: status);
    final stateAfterFirstUpdate = cubit.state;
    expect(stateAfterFirstUpdate, isNot(initialState));
    expect(stateAfterFirstUpdate.dx, 12);
    expect(stateAfterFirstUpdate.dy, 24);
    expect(stateAfterFirstUpdate.scale, 2);

    cubit.updateTransform(dx: 12, dy: 24, scale: 2, zoomStatus: status);
    expect(cubit.state, same(stateAfterFirstUpdate));

    cubit.setZoomStatus(
      const ZoomStatus(canZoomIn: true, canZoomOut: true, canReset: true),
    );
    expect(cubit.state, same(stateAfterFirstUpdate));
  });

  test('dedups repeated non-transform updates', () {
    final cubit = PrimarySourceViewportCubit();
    addTearDown(cubit.close);

    final initialState = cubit.state;

    cubit.setScaleAndPositionRestored(false);
    expect(cubit.state, same(initialState));

    cubit.startSelectAreaMode();
    final stateAfterSelectStart = cubit.state;
    expect(stateAfterSelectStart.selectAreaMode, isTrue);

    cubit.startSelectAreaMode();
    expect(cubit.state, same(stateAfterSelectStart));

    cubit.startPipetteMode(isColorToReplace: true);
    final stateAfterPipetteStart = cubit.state;
    expect(stateAfterPipetteStart.pipetteMode, isTrue);

    cubit.startPipetteMode(isColorToReplace: true);
    expect(cubit.state, same(stateAfterPipetteStart));

    cubit.resetColorReplacement();
    expect(cubit.state, same(stateAfterPipetteStart));
  });
}
