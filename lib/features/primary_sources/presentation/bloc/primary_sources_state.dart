import 'package:flutter/foundation.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/shared/models/primary_source.dart';

class PrimarySourcesState {
  PrimarySourcesState({
    required List<PrimarySource> full,
    required List<PrimarySource> significant,
    required List<PrimarySource> fragments,
    required this.isLoading,
    this.failure,
  }) : full = List<PrimarySource>.unmodifiable(full),
       significant = List<PrimarySource>.unmodifiable(significant),
       fragments = List<PrimarySource>.unmodifiable(fragments);

  factory PrimarySourcesState.initial() {
    return PrimarySourcesState(
      full: <PrimarySource>[],
      significant: <PrimarySource>[],
      fragments: <PrimarySource>[],
      isLoading: false,
    );
  }

  final List<PrimarySource> full;
  final List<PrimarySource> significant;
  final List<PrimarySource> fragments;
  final bool isLoading;
  final AppFailure? failure;

  bool get hasError => failure != null;

  PrimarySourcesState copyWith({
    List<PrimarySource>? full,
    List<PrimarySource>? significant,
    List<PrimarySource>? fragments,
    bool? isLoading,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return PrimarySourcesState(
      full: full ?? this.full,
      significant: significant ?? this.significant,
      fragments: fragments ?? this.fragments,
      isLoading: isLoading ?? this.isLoading,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourcesState &&
            runtimeType == other.runtimeType &&
            listEquals(full, other.full) &&
            listEquals(significant, other.significant) &&
            listEquals(fragments, other.fragments) &&
            isLoading == other.isLoading &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    Object.hashAll(full),
    Object.hashAll(significant),
    Object.hashAll(fragments),
    isLoading,
    failure,
  );
}
