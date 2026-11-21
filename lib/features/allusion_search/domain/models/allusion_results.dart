import 'package:flutter/foundation.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

enum AllusionScope { wholeBible, oldTestament, newTestament }

enum AllusionLevel { verse, chapter, book }

typedef AllusionQuery = ({
  int bookId,
  int chapter,
  int verse,
  int length,
  AllusionScope scope,
});

class AllusionMatch {
  AllusionMatch({
    required this.reference,
    Iterable<BibleVerseReference>? references,
    required Iterable<int> numbers,
    required this.score,
    required this.sharedWeight,
  }) : references = List.unmodifiable(references ?? [reference]),
       numbers = List.unmodifiable(numbers.toList()..sort());
  final BibleVerseReference reference;
  final List<BibleVerseReference> references;
  final List<int> numbers;
  final double score;
  final double sharedWeight;

  @override
  bool operator ==(Object other) =>
      other is AllusionMatch &&
      reference == other.reference &&
      listEquals(references, other.references) &&
      listEquals(numbers, other.numbers) &&
      score == other.score &&
      sharedWeight == other.sharedWeight;
  @override
  int get hashCode => Object.hash(
    reference,
    Object.hashAll(references),
    Object.hashAll(numbers),
    score,
    sharedWeight,
  );
}

class AllusionResults {
  AllusionResults({
    required this.start,
    required this.end,
    required Iterable<int> sourceNumbers,
    required Map<AllusionLevel, List<AllusionMatch>> matches,
  }) : sourceNumbers = List.unmodifiable(sourceNumbers.toList()..sort()),
       _matches = Map.unmodifiable(
         matches.map(
           (key, value) =>
               MapEntry(key, List<AllusionMatch>.unmodifiable(value)),
         ),
       );

  final BibleVerseReference start;
  final BibleVerseReference end;
  final List<int> sourceNumbers;
  final Map<AllusionLevel, List<AllusionMatch>> _matches;
  List<AllusionMatch> forLevel(AllusionLevel level) =>
      _matches[level] ?? const [];

  @override
  bool operator ==(Object other) =>
      other is AllusionResults &&
      start == other.start &&
      end == other.end &&
      listEquals(sourceNumbers, other.sourceNumbers) &&
      AllusionLevel.values.every(
        (level) => listEquals(forLevel(level), other.forLevel(level)),
      );
  @override
  int get hashCode => Object.hash(
    start,
    end,
    Object.hashAll(sourceNumbers),
    Object.hashAll(
      AllusionLevel.values.map((level) => Object.hashAll(forLevel(level))),
    ),
  );
}
