import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_expansion_cubit.dart';

void main() {
  test('toggle expands and collapses source id', () {
    final cubit = PrimarySourcesExpansionCubit();
    addTearDown(cubit.close);

    expect(cubit.state.expandedSourceIds, isEmpty);

    cubit.toggle('source-a');
    expect(cubit.state.expandedSourceIds, {'source-a'});
    expect(cubit.isExpanded('source-a'), isTrue);

    cubit.toggle('source-a');
    expect(cubit.state.expandedSourceIds, isEmpty);
    expect(cubit.isExpanded('source-a'), isFalse);
  });

  test('retainKnownSourceIds removes stale expanded ids', () {
    final cubit = PrimarySourcesExpansionCubit();
    addTearDown(cubit.close);

    cubit.setExpanded('source-a', true);
    cubit.setExpanded('source-b', true);
    cubit.retainKnownSourceIds(const <String>['source-a', 'source-c']);

    expect(cubit.state.expandedSourceIds, {'source-a'});
  });
}
