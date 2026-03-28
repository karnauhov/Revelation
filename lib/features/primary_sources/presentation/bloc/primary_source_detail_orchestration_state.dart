import 'package:flutter/foundation.dart';

@immutable
class PrimarySourceDetailOrchestrationState {
  const PrimarySourceDetailOrchestrationState();

  static const initial = PrimarySourceDetailOrchestrationState();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceDetailOrchestrationState;
  }

  @override
  int get hashCode => 0;
}
