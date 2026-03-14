import 'package:flutter/foundation.dart';

@immutable
class ZoomStatus {
  final bool canZoomIn;
  final bool canZoomOut;
  final bool canReset;
  const ZoomStatus({
    required this.canZoomIn,
    required this.canZoomOut,
    required this.canReset,
  });

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is ZoomStatus &&
            runtimeType == other.runtimeType &&
            canZoomIn == other.canZoomIn &&
            canZoomOut == other.canZoomOut &&
            canReset == other.canReset;
  }

  @override
  int get hashCode => Object.hash(canZoomIn, canZoomOut, canReset);
}
