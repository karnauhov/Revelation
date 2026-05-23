class StrongNumberPolicy {
  const StrongNumberPolicy();

  static const int minNumber = 1;
  static const int classicMaxNumber = 5624;
  static const int extendedMinNumber = 6000;
  static const int extendedMaxNumber = 20833;
  static const List<int> attestedExtendedNumbers = <int>[
    6000,
    6001,
    6002,
    6003,
    6005,
    6006,
    6007,
    6008,
    6011,
    6013,
    6015,
    6016,
    6017,
    6018,
    6019,
    6020,
    6022,
    6027,
    6028,
    6029,
    6030,
    6031,
    6032,
    6033,
    6034,
    6035,
    6036,
    6037,
    6041,
    6043,
    6044,
    6045,
    6046,
    6048,
    6049,
    6050,
    6051,
    6052,
    6053,
    6055,
    6058,
    6059,
    6060,
    6061,
    6063,
    6064,
    6065,
    6066,
    6068,
    6069,
    6070,
    6071,
    6072,
    6073,
    6074,
    6075,
    6076,
    6077,
    6078,
    6079,
    6080,
    6081,
    6083,
    6085,
    6087,
    6088,
    6090,
    6091,
    6092,
    6093,
    6094,
    6095,
    6632,
    6897,
    7013,
    7530,
    9315,
    9402,
    9577,
    9990,
    9991,
    9992,
    9993,
    9994,
    9995,
    9996,
    20447,
    20833,
  ];
  static const int attestedExtendedCount = 88;

  /// Extended navigation is enabled only for the 88 attested NA28_LXX keys.
  /// Do not treat G6000..G20833 as a continuous range.
  static const bool extendedNavigationEnabled = true;

  static const int maxNumber = extendedNavigationEnabled
      ? extendedMaxNumber
      : classicMaxNumber;
  static const int blockedSingleNumber = 2717;
  static const int blockedRangeStart = 3203;
  static const int blockedRangeEnd = 3302;

  bool isAllowed(int value) {
    if (isForbidden(value)) {
      return false;
    }
    if (value >= minNumber && value <= classicMaxNumber) {
      return true;
    }
    return extendedNavigationEnabled && isAttestedExtended(value);
  }

  static bool isAttestedExtended(int value) =>
      attestedExtendedNumbers.contains(value);

  bool isForbidden(int value) {
    return value == blockedSingleNumber ||
        (value >= blockedRangeStart && value <= blockedRangeEnd);
  }

  int normalizeToAllowed(int value) {
    if (isAllowed(value)) {
      return value;
    }

    if (extendedNavigationEnabled && value > classicMaxNumber) {
      return _closestExtendedRolloutNumber(value);
    }

    var normalized = value.clamp(minNumber, classicMaxNumber);

    if (normalized == blockedSingleNumber) {
      normalized = blockedSingleNumber + 1;
    } else if (normalized >= blockedRangeStart &&
        normalized <= blockedRangeEnd) {
      normalized = blockedRangeEnd + 1;
    }

    return normalized.clamp(minNumber, classicMaxNumber);
  }

  int _closestExtendedRolloutNumber(int value) {
    var best = classicMaxNumber;
    var bestDistance = (value - best).abs();

    for (final candidate in attestedExtendedNumbers) {
      final distance = (value - candidate).abs();
      if (distance < bestDistance ||
          (distance == bestDistance && candidate < best)) {
        best = candidate;
        bestDistance = distance;
      }
    }

    return best;
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
