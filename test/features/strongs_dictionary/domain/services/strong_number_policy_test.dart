import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_number_policy.dart';

void main() {
  const policy = StrongNumberPolicy();

  test('uses classic Greek Strong boundaries', () {
    expect(StrongNumberPolicy.minNumber, 1);
    expect(StrongNumberPolicy.maxNumber, 5624);
  });

  test('isAllowed validates boundaries and forbidden values', () {
    expect(policy.isAllowed(0), isFalse);
    expect(policy.isAllowed(1), isTrue);
    expect(policy.isAllowed(2717), isFalse);
    expect(policy.isAllowed(3203), isFalse);
    expect(policy.isAllowed(3302), isFalse);
    expect(policy.isAllowed(3303), isTrue);
    expect(policy.isAllowed(5624), isTrue);
    expect(policy.isAllowed(5625), isFalse);
  });

  test('normalizeToAllowed clamps values and skips forbidden values', () {
    expect(policy.normalizeToAllowed(-10), 1);
    expect(policy.normalizeToAllowed(2717), 2718);
    expect(policy.normalizeToAllowed(3203), 3303);
    expect(policy.normalizeToAllowed(3302), 3303);
    expect(policy.normalizeToAllowed(5625), 5624);
    expect(policy.normalizeToAllowed(99999), 5624);
  });

  test('neighbor skips forbidden values and wraps around', () {
    expect(policy.neighbor(2716, forward: true), 2718);
    expect(policy.neighbor(3202, forward: true), 3303);
    expect(policy.neighbor(3303, forward: false), 3202);
    expect(policy.neighbor(5624, forward: true), 1);
    expect(policy.neighbor(1, forward: false), 5624);
  });

  test('neighborAvailable moves through real dictionary entries', () {
    const available = <int>[1, 2718, 3303, 5624, 5625];

    expect(policy.neighborAvailable(2716, available, forward: true), 2718);
    expect(policy.neighborAvailable(5624, available, forward: true), 1);
    expect(policy.neighborAvailable(1, available, forward: false), 5624);
  });

  test('closestAvailableNumber prefers nearest valid picker number', () {
    const available = <int>[1, 2718, 3303, 5000];

    expect(policy.closestAvailableNumber(2717, available), 2718);
    expect(policy.closestAvailableNumber(3203, available), 3303);
    expect(policy.closestAvailableNumber(4999, available), 5000);
    expect(policy.closestAvailableNumber(99999, available), 5000);
    expect(policy.closestAvailableNumber(10, const <int>[]), 1);
  });
}
