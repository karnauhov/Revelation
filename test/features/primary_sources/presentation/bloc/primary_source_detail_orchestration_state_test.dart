import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_state.dart';

void main() {
  test('all instances are equal and have stable hashCode', () {
    const stateA = PrimarySourceDetailOrchestrationState();
    const stateB = PrimarySourceDetailOrchestrationState();

    expect(stateA, stateB);
    expect(stateA, PrimarySourceDetailOrchestrationState.initial);
    expect(stateA.hashCode, stateB.hashCode);
    expect(stateA.hashCode, 0);
  });

  test('state is not equal to objects of other types', () {
    const state = PrimarySourceDetailOrchestrationState();

    expect(state == Object(), isFalse);
    expect(state == 'state', isFalse);
  });
}
