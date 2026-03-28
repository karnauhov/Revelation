import 'package:flutter/foundation.dart';

class PrimarySourcesExpansionState {
  PrimarySourcesExpansionState({required Set<String> expandedSourceIds})
    : expandedSourceIds = Set<String>.unmodifiable(expandedSourceIds);

  factory PrimarySourcesExpansionState.initial() {
    return PrimarySourcesExpansionState(expandedSourceIds: <String>{});
  }

  final Set<String> expandedSourceIds;

  bool isExpanded(String sourceId) {
    return expandedSourceIds.contains(sourceId);
  }

  PrimarySourcesExpansionState copyWith({Set<String>? expandedSourceIds}) {
    return PrimarySourcesExpansionState(
      expandedSourceIds: expandedSourceIds ?? this.expandedSourceIds,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourcesExpansionState &&
            runtimeType == other.runtimeType &&
            setEquals(expandedSourceIds, other.expandedSourceIds);
  }

  @override
  int get hashCode => Object.hashAllUnordered(expandedSourceIds);
}
