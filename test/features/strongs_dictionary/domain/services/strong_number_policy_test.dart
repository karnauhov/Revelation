import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_number_policy.dart';

void main() {
  const policy = StrongNumberPolicy();

  test('enables attested extended navigation after dictionary rollout', () {
    expect(StrongNumberPolicy.classicMaxNumber, 5624);
    expect(StrongNumberPolicy.extendedMinNumber, 6000);
    expect(StrongNumberPolicy.extendedMaxNumber, 20833);
    expect(StrongNumberPolicy.attestedExtendedCount, 88);
    expect(StrongNumberPolicy.attestedExtendedNumbers, hasLength(88));
    expect(StrongNumberPolicy.attestedExtendedNumbers.toSet(), hasLength(88));
    expect(StrongNumberPolicy.isAttestedExtended(6000), isTrue);
    expect(StrongNumberPolicy.isAttestedExtended(6087), isTrue);
    expect(StrongNumberPolicy.isAttestedExtended(20833), isTrue);
    expect(StrongNumberPolicy.isAttestedExtended(21502), isFalse);
    expect(StrongNumberPolicy.extendedNavigationEnabled, isTrue);
    expect(StrongNumberPolicy.maxNumber, StrongNumberPolicy.extendedMaxNumber);
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
    expect(policy.isAllowed(6000), isTrue);
    expect(policy.isAllowed(6096), isFalse);
    expect(policy.isAllowed(20833), isTrue);
    expect(policy.isAllowed(21502), isFalse);
    expect(policy.isAllowed(21503), isFalse);
  });

  test('normalizeToAllowed clamps values and skips forbidden values', () {
    expect(policy.normalizeToAllowed(-10), 1);
    expect(policy.normalizeToAllowed(2717), 2718);
    expect(policy.normalizeToAllowed(3203), 3303);
    expect(policy.normalizeToAllowed(3302), 3303);
    expect(policy.normalizeToAllowed(5625), 5624);
    expect(policy.normalizeToAllowed(6000), 6000);
    expect(policy.normalizeToAllowed(6096), 6095);
    expect(policy.normalizeToAllowed(20833), 20833);
    expect(policy.normalizeToAllowed(21502), 20833);
    expect(policy.normalizeToAllowed(30000), 20833);
  });

  test('neighbor skips forbidden values and wraps around', () {
    expect(policy.neighbor(2716, forward: true), 2718);
    expect(policy.neighbor(3202, forward: true), 3303);
    expect(policy.neighbor(3303, forward: false), 3202);
    expect(policy.neighbor(5624, forward: true), 6000);
    expect(policy.neighbor(6095, forward: true), 6632);
    expect(policy.neighbor(1, forward: false), 20833);
  });

  test('neighborAvailable moves through real dictionary entries', () {
    const available = <int>[1, 2718, 3303, 5624, 6000, 20833];

    expect(policy.neighborAvailable(2716, available, forward: true), 2718);
    expect(policy.neighborAvailable(5624, available, forward: true), 6000);
    expect(policy.neighborAvailable(1, available, forward: false), 20833);
  });

  test('closestAvailableNumber prefers nearest valid picker number', () {
    const available = <int>[1, 2718, 3303, 5000];

    expect(policy.closestAvailableNumber(2717, available), 2718);
    expect(policy.closestAvailableNumber(3203, available), 3303);
    expect(policy.closestAvailableNumber(4999, available), 5000);
    expect(policy.closestAvailableNumber(6000, available), 5000);
    expect(
      policy.closestAvailableNumber(21502, const <int>[1, 5000, 6000, 20833]),
      20833,
    );
    expect(policy.closestAvailableNumber(10, const <int>[]), 1);
  });
}
