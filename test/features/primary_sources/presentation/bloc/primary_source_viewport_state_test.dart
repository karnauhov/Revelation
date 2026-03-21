import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_state.dart';
import 'package:revelation/shared/models/zoom_status.dart';

void main() {
  test('initial exposes baseline viewport contract', () {
    const state = PrimarySourceViewportState.initial;

    expect(state.dx, 0);
    expect(state.dy, 0);
    expect(state.scale, 1);
    expect(state.savedX, 0);
    expect(state.savedY, 0);
    expect(state.savedScale, 0);
    expect(state.scaleAndPositionRestored, isFalse);
    expect(
      state.zoomStatus,
      const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
    );
    expect(state.selectedArea, isNull);
    expect(state.colorToReplace, const Color(0xFFFFFFFF));
    expect(state.newColor, const Color(0xFFFFFFFF));
    expect(state.tolerance, 0);
    expect(state.pipetteMode, isFalse);
    expect(state.selectAreaMode, isFalse);
    expect(state.isColorToReplace, isTrue);
  });

  test(
    'copyWith supports explicit selectedArea reset through selectedAreaSet',
    () {
      final withArea = PrimarySourceViewportState.initial.copyWith(
        selectedArea: const Rect.fromLTWH(1, 2, 3, 4),
        selectedAreaSet: true,
      );
      final cleared = withArea.copyWith(
        selectedArea: null,
        selectedAreaSet: true,
      );
      final untouched = withArea.copyWith(selectedArea: null);

      expect(withArea.selectedArea, const Rect.fromLTWH(1, 2, 3, 4));
      expect(cleared.selectedArea, isNull);
      expect(untouched.selectedArea, const Rect.fromLTWH(1, 2, 3, 4));
    },
  );

  test('value equality includes transform and render controls', () {
    const zoom = ZoomStatus(canZoomIn: true, canZoomOut: true, canReset: true);
    final a = PrimarySourceViewportState.initial.copyWith(
      dx: 1,
      dy: 2,
      scale: 3,
      savedX: 4,
      savedY: 5,
      savedScale: 6,
      scaleAndPositionRestored: true,
      zoomStatus: zoom,
      selectedArea: const Rect.fromLTWH(1, 1, 2, 2),
      selectedAreaSet: true,
      colorToReplace: const Color(0xFF010203),
      newColor: const Color(0xFF040506),
      tolerance: 7,
      pipetteMode: true,
      selectAreaMode: true,
      isColorToReplace: false,
    );
    final b = PrimarySourceViewportState.initial.copyWith(
      dx: 1,
      dy: 2,
      scale: 3,
      savedX: 4,
      savedY: 5,
      savedScale: 6,
      scaleAndPositionRestored: true,
      zoomStatus: zoom,
      selectedArea: const Rect.fromLTWH(1, 1, 2, 2),
      selectedAreaSet: true,
      colorToReplace: const Color(0xFF010203),
      newColor: const Color(0xFF040506),
      tolerance: 7,
      pipetteMode: true,
      selectAreaMode: true,
      isColorToReplace: false,
    );

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(b.copyWith(scale: 4)));
  });
}
