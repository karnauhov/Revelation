import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_expansion_state.dart';

void main() {
  test('initial has no expanded ids', () {
    final state = PrimarySourcesExpansionState.initial();
    expect(state.expandedSourceIds, isEmpty);
    expect(state.isExpanded('any'), isFalse);
  });

  test('constructor and copyWith keep expanded ids immutable', () {
    final mutable = <String>{'s1'};
    final state = PrimarySourcesExpansionState(expandedSourceIds: mutable);
    mutable.add('s2');

    expect(state.expandedSourceIds, {'s1'});
    expect(() => state.expandedSourceIds.add('x'), throwsUnsupportedError);

    final next = <String>{'s3'};
    final updated = state.copyWith(expandedSourceIds: next);
    next.add('s4');
    expect(updated.expandedSourceIds, {'s3'});
  });

  test(
    'value equality compares set contents regardless of insertion order',
    () {
      final a = PrimarySourcesExpansionState(expandedSourceIds: {'a', 'b'});
      final b = PrimarySourcesExpansionState(expandedSourceIds: {'b', 'a'});
      final c = PrimarySourcesExpansionState(expandedSourceIds: {'a'});

      expect(a, b);
      expect(a.hashCode, b.hashCode);
      expect(a, isNot(c));
    },
  );
}
