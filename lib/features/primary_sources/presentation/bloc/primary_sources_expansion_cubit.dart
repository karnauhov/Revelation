import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_expansion_state.dart';

class PrimarySourcesExpansionCubit extends Cubit<PrimarySourcesExpansionState> {
  PrimarySourcesExpansionCubit()
    : super(PrimarySourcesExpansionState.initial());

  bool isExpanded(String sourceId) {
    return state.isExpanded(sourceId.trim());
  }

  void toggle(String sourceId) {
    final normalized = sourceId.trim();
    if (normalized.isEmpty) {
      return;
    }
    setExpanded(normalized, !state.isExpanded(normalized));
  }

  void setExpanded(String sourceId, bool expanded) {
    final normalized = sourceId.trim();
    if (normalized.isEmpty) {
      return;
    }

    final updated = Set<String>.from(state.expandedSourceIds);
    final changed = expanded
        ? updated.add(normalized)
        : updated.remove(normalized);
    if (!changed) {
      return;
    }
    emit(state.copyWith(expandedSourceIds: updated));
  }

  void retainKnownSourceIds(Iterable<String> sourceIds) {
    final allowed = sourceIds
        .map((id) => id.trim())
        .where((id) => id.isNotEmpty)
        .toSet();
    final retained = state.expandedSourceIds.where(allowed.contains).toSet();
    if (retained.length == state.expandedSourceIds.length) {
      return;
    }
    emit(state.copyWith(expandedSourceIds: retained));
  }
}
