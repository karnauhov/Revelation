import 'package:revelation/shared/config/app_constants.dart';

class BibleWorkspaceState {
  const BibleWorkspaceState({
    required this.paneIds,
    this.linkedNavigation = true,
  });

  const BibleWorkspaceState.initial()
    : paneIds = const <String>[],
      linkedNavigation = true;

  final List<String> paneIds;
  final bool linkedNavigation;

  bool get hasMultiplePanes => paneIds.length > 1;
  bool get canOpenParallelReader =>
      paneIds.isNotEmpty &&
      paneIds.length < AppConstants.maxParallelBibleReaders;

  BibleWorkspaceState copyWith({
    List<String>? paneIds,
    bool? linkedNavigation,
  }) {
    return BibleWorkspaceState(
      paneIds: paneIds ?? this.paneIds,
      linkedNavigation: linkedNavigation ?? this.linkedNavigation,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleWorkspaceState &&
            _listEquals(other.paneIds, paneIds) &&
            other.linkedNavigation == linkedNavigation;
  }

  @override
  int get hashCode => Object.hash(Object.hashAll(paneIds), linkedNavigation);
}

bool _listEquals<T>(List<T> left, List<T> right) {
  if (identical(left, right)) {
    return true;
  }
  if (left.length != right.length) {
    return false;
  }
  for (var index = 0; index < left.length; index++) {
    if (left[index] != right[index]) {
      return false;
    }
  }
  return true;
}
