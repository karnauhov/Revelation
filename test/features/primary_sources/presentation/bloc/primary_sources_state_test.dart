import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_state.dart';
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  test('constructor stores immutable copies of source groups', () {
    final full = <PrimarySource>[_buildSource('full')];
    final significant = <PrimarySource>[_buildSource('significant')];
    final fragments = <PrimarySource>[_buildSource('fragment')];

    final state = PrimarySourcesState(
      full: full,
      significant: significant,
      fragments: fragments,
      isLoading: false,
    );

    full.clear();
    significant.clear();
    fragments.clear();

    expect(state.full.map((source) => source.id), <String>['full']);
    expect(state.significant.map((source) => source.id), <String>[
      'significant',
    ]);
    expect(state.fragments.map((source) => source.id), <String>['fragment']);
    expect(() => state.full.add(_buildSource('new')), throwsUnsupportedError);
  });

  test('copyWith keeps collections immutable', () {
    final initial = PrimarySourcesState.initial();
    final nextFull = <PrimarySource>[_buildSource('next')];

    final updated = initial.copyWith(full: nextFull);
    nextFull.add(_buildSource('next-2'));

    expect(updated.full.map((source) => source.id), <String>['next']);
    expect(
      () => updated.full.add(_buildSource('next-3')),
      throwsUnsupportedError,
    );
  });
}

PrimarySource _buildSource(String id) {
  return PrimarySource(
    id: id,
    title: id,
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    attributes: const [],
    permissionsReceived: false,
  );
}
