class StrongNumberPolicy {
  const StrongNumberPolicy();

  static const int minNumber = 1;
  static const int maxNumber = 5624;
  static const int blockedSingleNumber = 2717;
  static const int blockedRangeStart = 3203;
  static const int blockedRangeEnd = 3302;

  bool isAllowed(int value) {
    if (isForbidden(value)) {
      return false;
    }
    return value >= minNumber && value <= maxNumber;
  }

  bool isForbidden(int value) {
    return value == blockedSingleNumber ||
        (value >= blockedRangeStart && value <= blockedRangeEnd);
  }

  int normalizeToAllowed(int value) {
    if (isAllowed(value)) {
      return value;
    }

    var normalized = value.clamp(minNumber, maxNumber);

    if (normalized == blockedSingleNumber) {
      normalized = blockedSingleNumber + 1;
    } else if (normalized >= blockedRangeStart &&
        normalized <= blockedRangeEnd) {
      normalized = blockedRangeEnd + 1;
    }

    return normalized.clamp(minNumber, maxNumber);
  }

  int closestAvailableNumber(int value, Iterable<int> availableNumbers) {
    final numbers =
        availableNumbers.where(isAllowed).toSet().toList(growable: false)
          ..sort();
    if (numbers.isEmpty) {
      return minNumber;
    }

    final normalized = normalizeToAllowed(value);
    if (numbers.contains(normalized)) {
      return normalized;
    }

    for (var offset = 1; offset <= maxNumber; offset++) {
      final up = normalized + offset;
      if (up <= maxNumber && numbers.contains(up)) {
        return up;
      }
      final down = normalized - offset;
      if (down >= minNumber && numbers.contains(down)) {
        return down;
      }
    }

    return numbers.first;
  }

  int neighbor(int current, {required bool forward}) {
    var candidate = normalizeToAllowed(current);
    do {
      candidate = forward ? candidate + 1 : candidate - 1;
      if (candidate > maxNumber) {
        candidate = minNumber;
      }
      if (candidate < minNumber) {
        candidate = maxNumber;
      }
    } while (!isAllowed(candidate));

    return candidate;
  }

  int neighborAvailable(
    int current,
    Iterable<int> availableNumbers, {
    required bool forward,
  }) {
    final numbers =
        availableNumbers.where(isAllowed).toSet().toList(growable: false)
          ..sort();
    if (numbers.isEmpty) {
      return neighbor(current, forward: forward);
    }

    final normalized = normalizeToAllowed(current);
    if (forward) {
      for (final number in numbers) {
        if (number > normalized) {
          return number;
        }
      }
      return numbers.first;
    }

    for (final number in numbers.reversed) {
      if (number < normalized) {
        return number;
      }
    }
    return numbers.last;
  }
}
