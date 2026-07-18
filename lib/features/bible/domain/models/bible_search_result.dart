import 'package:revelation/shared/models/bible_verse_reference.dart';

class BibleTextMatch {
  const BibleTextMatch({required this.start, required this.end});

  final int start;
  final int end;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleTextMatch && start == other.start && end == other.end;
  }

  @override
  int get hashCode => Object.hash(start, end);
}

class BibleSearchResult {
  const BibleSearchResult({
    required this.reference,
    required this.text,
    required this.matches,
  });

  final BibleVerseReference reference;
  final String text;
  final List<BibleTextMatch> matches;

  int get matchCount => matches.length;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleSearchResult &&
            reference == other.reference &&
            text == other.text &&
            _listEquals(matches, other.matches);
  }

  @override
  int get hashCode => Object.hash(reference, text, Object.hashAll(matches));
}

bool _listEquals<T>(List<T> left, List<T> right) {
  if (identical(left, right)) {
    return true;
  }
  if (left.length != right.length) {
    return false;
  }
  for (var index = 0; index < left.length; index++) {
    if (left[index] != right[index]) {
      return false;
    }
  }
  return true;
}
