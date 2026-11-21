import 'dart:math' as math;
import 'dart:typed_data';

import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_postings.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

typedef AllusionSourceWord = ({
  String? form,
  int? occurrences,
  double baseWeight,
  double searchWeight,
});
typedef AllusionSourceVocabulary = ({
  Map<int, AllusionSourceWord> words,
  double totalWeight,
});

/// Immutable, corpus-specific posting index. Frequencies count each G-ID once per verse.
class AllusionIndex {
  AllusionIndex.fromPostings(this.verseMap, this._postings)
    : _weights = Float64List(_postings.baseWeights.length),
      _verseTotals = Float64List(verseMap.totalVerses + 1) {
    for (var n = 1; n < _weights.length; n++) {
      final df = _postings.termOffsets[n + 1] - _postings.termOffsets[n];
      if (df > 0) {
        _weights[n] =
            _postings.baseWeights[n] *
            math.min(4.0, 1 + math.log((_postings.documents + 1) / (df + 1)));
      }
    }
    for (var ordinal = 1; ordinal < _verseTotals.length; ordinal++) {
      var total = 0.0;
      final end = _postings.verseOffsets[ordinal + 1];
      for (var i = _postings.verseOffsets[ordinal]; i < end; i++) {
        total += _weights[_postings.terms[i]];
      }
      _verseTotals[ordinal] = total;
    }
  }

  static const maxLength = 77;
  final BibleVerseMap verseMap;
  final AllusionPostings _postings;
  final Float64List _weights;
  final Float64List _verseTotals;

  factory AllusionIndex.build({
    required BibleVerseMap verseMap,
    required Iterable<BibleVerseText> verses,
    required Map<int, double> baseWeights,
  }) {
    final builder = AllusionIndexBuilder(verseMap, baseWeights);
    builder.add(verses);
    return AllusionIndex.fromPostings(verseMap, builder.finish());
  }

  double? baseWeight(int number) =>
      number > 0 && number < _postings.baseWeights.length
      ? _postings.baseWeights[number]
      : null;

  Set<int> _sourceNumbers(int first, int last) => {
    for (var ordinal = first; ordinal <= last; ordinal++)
      ..._postings.numbersFor(ordinal),
  };

  /// The search index stores presence per verse; the original text retains
  /// repeated occurrences. Never infer a frequency from the translation.
  AllusionSourceVocabulary sourceVocabulary(
    List<BibleVerseReference> passage,
    Map<String, String>? originals,
  ) {
    final numbers = _sourceNumbers(
      int.parse(passage.first.verseKey, radix: 36),
      int.parse(passage.last.verseKey, radix: 36),
    );
    final counts = <int, int>{};
    final forms = <int, String>{};
    final unavailable = <int>{};
    for (final ref in passage) {
      final original = originals?[ref.verseKey];
      if (original == null) {
        unavailable.addAll(
          _postings.numbersFor(int.parse(ref.verseKey, radix: 36)),
        );
        continue;
      }
      for (final word in bibleMarkedWords(original)) {
        for (final code in word.codes) {
          if (!code.startsWith('G')) continue;
          final number = int.parse(code.substring(1));
          if (!numbers.contains(number)) continue;
          counts.update(number, (count) => count + 1, ifAbsent: () => 1);
          forms.putIfAbsent(number, () => word.text);
        }
      }
    }
    return (
      words: {
        for (final n in numbers.toList()..sort())
          n: (
            form: forms[n],
            occurrences: unavailable.contains(n) ? null : counts[n],
            baseWeight: _postings.baseWeights[n],
            searchWeight: _weights[n],
          ),
      },
      totalWeight: _total(numbers),
    );
  }

  Set<int> matchedInVerse(BibleVerseReference ref, Iterable<int> candidates) {
    final present = _postings
        .numbersFor(int.parse(ref.verseKey, radix: 36))
        .toSet();
    return candidates.where(present.contains).toSet();
  }

  AllusionResults search(AllusionQuery query) => _search(query).last!;

  Future<AllusionResults> searchInBatches(AllusionQuery query) async {
    for (final result in _search(query)) {
      if (result != null) return result;
      await Future<void>.delayed(Duration.zero);
    }
    throw StateError('Incomplete allusion search');
  }

  Iterable<AllusionResults?> _search(AllusionQuery query) sync* {
    RangeError.checkValueInInterval(query.length, 1, maxLength, 'length');
    final start = verseMap.referenceFor(
      bookId: query.bookId,
      chapter: query.chapter,
      verse: query.verse,
    );
    final first = int.parse(start.verseKey, radix: 36);
    final last = math.min(first + query.length - 1, verseMap.totalVerses);
    final source = _sourceNumbers(first, last);
    final sourceTotal = _total(source);
    final sourceLexicalCount = _lexicalCount(source);
    final candidates = <int, Set<int>>{};
    final ntStart = verseMap.totalBooks >= 40
        ? int.parse(
            verseMap.referenceFor(bookId: 40, chapter: 1, verse: 1).verseKey,
            radix: 36,
          )
        : verseMap.totalVerses + 1;
    var visited = 0;
    for (final number in source) {
      for (final ordinal in _postings.versesFor(number)) {
        if (++visited % 4096 == 0) yield null;
        if (ordinal >= first && ordinal <= last) continue;
        final inScope = switch (query.scope) {
          AllusionScope.wholeBible => true,
          AllusionScope.oldTestament => ordinal < ntStart,
          AllusionScope.newTestament => ordinal >= ntStart,
        };
        if (inScope) (candidates[ordinal] ??= {}).add(number);
      }
    }
    final verseMatches = <AllusionMatch>[];
    final chapters = <(int, int), Set<int>>{};
    final books = <int, Set<int>>{};
    final chapterOrdinals = <(int, int), List<int>>{};
    final bookOrdinals = <int, List<int>>{};
    final versePriority = <int, ({bool qualifies, double score})>{};
    int compareVerses(int a, int b) {
      final left = versePriority[a]!;
      final right = versePriority[b]!;
      if (left.qualifies != right.qualifies) return left.qualifies ? -1 : 1;
      final byScore = right.score.compareTo(left.score);
      return byScore != 0 ? byScore : a.compareTo(b);
    }

    for (final MapEntry(key: ordinal, value: common) in candidates.entries) {
      if (++visited % 256 == 0) yield null;
      final reference = _reference(ordinal);
      (chapters[(reference.bookId, reference.chapter)] ??= {}).addAll(common);
      (books[reference.bookId] ??= {}).addAll(common);
      final lexicalCount = _lexicalCount(common);
      if (lexicalCount > 0) {
        final sharedWeight = _total(common);
        final score = 2 * sharedWeight / (sourceTotal + _verseTotals[ordinal]);
        final qualifies = lexicalCount >= 3;
        versePriority[ordinal] = (qualifies: qualifies, score: score);
        if (qualifies) {
          verseMatches.add(
            AllusionMatch(
              reference: reference,
              numbers: common,
              score: score,
              sharedWeight: sharedWeight,
            ),
          );
        }
        final chapterKey = (reference.bookId, reference.chapter);
        (chapterOrdinals[chapterKey] ??= []).add(ordinal);
        (bookOrdinals[reference.bookId] ??= []).add(ordinal);
      }
    }
    yield AllusionResults(
      start: start,
      end: _reference(last),
      sourceNumbers: source,
      matches: {
        AllusionLevel.verse: _rank(verseMatches),
        AllusionLevel.chapter: _rank([
          for (final MapEntry(key: (book, chapter), value: common)
              in chapters.entries)
            if (_lexicalCount(common) > (sourceLexicalCount / 3).ceil())
              _groupMatch(
                chapterOrdinals[(book, chapter)]!,
                common,
                sourceTotal,
                compareVerses,
              ),
        ]),
        AllusionLevel.book: _rank([
          for (final MapEntry(key: book, value: common) in books.entries)
            if (_lexicalCount(common) > (sourceLexicalCount / 2).ceil())
              _groupMatch(
                bookOrdinals[book]!,
                common,
                sourceTotal,
                compareVerses,
              ),
        ]),
      },
    );
  }

  AllusionMatch _groupMatch(
    List<int> ordinals,
    Set<int> common,
    double sourceTotal,
    Comparator<int> compareVerses,
  ) {
    ordinals.sort(compareVerses);
    final sharedWeight = _total(common);
    return AllusionMatch(
      reference: _reference(ordinals.first),
      references: ordinals.map(_reference),
      numbers: common,
      score: sharedWeight / sourceTotal,
      sharedWeight: sharedWeight,
    );
  }

  int _lexicalCount(Iterable<int> numbers) =>
      numbers.where((number) => _postings.baseWeights[number] >= 0.5).length;
  double _total(Iterable<int> numbers) =>
      numbers.fold(0.0, (total, number) => total + _weights[number]);
  BibleVerseReference _reference(int ordinal) =>
      verseMap.referenceForOrdinal(ordinal);
  static List<AllusionMatch> _rank(List<AllusionMatch> matches) =>
      matches..sort((a, b) {
        final scoreOrder = b.score.compareTo(a.score);
        return scoreOrder != 0
            ? scoreOrder
            : a.reference.verseKey.compareTo(b.reference.verseKey);
      });
}

/// Incremental fallback for an older corpus without a compatible prepared index.
class AllusionIndexBuilder {
  AllusionIndexBuilder(this.verseMap, this.baseWeights)
    : byVerse = List.filled(verseMap.totalVerses + 1, null),
      byTerm = List.filled(baseWeights.keys.reduce(math.max) + 1, null);

  final BibleVerseMap verseMap;
  final Map<int, double> baseWeights;
  final List<List<int>?> byVerse, byTerm;
  int documents = 0;
  static final whitespace = RegExp(r'\s+');

  void add(Iterable<BibleVerseText> rows) {
    for (final row in rows) {
      final reference = verseMap.referenceForKey(row.verseKey);
      final ordinal = reference == null
          ? null
          : int.parse(reference.verseKey, radix: 36);
      if (ordinal == null || byVerse[ordinal] != null) {
        throw FormatException(
          'Invalid or duplicate Greek verse ${row.verseKey}',
        );
      }
      final numbers = <int>{};
      for (final token in row.text.split(whitespace)) {
        if (!bibleStrongTokenPattern.hasMatch(token) ||
            token[0].toUpperCase() != 'G')
          continue;
        final number = int.parse(token.substring(1));
        final weight = baseWeights[number];
        if (weight == null)
          throw FormatException('Missing semantic weight G$number');
        if (weight > 0) numbers.add(number);
      }
      byVerse[ordinal] = numbers.toList(growable: false);
      for (final n in numbers) {
        (byTerm[n] ??= []).add(ordinal);
      }
      documents++;
    }
  }

  AllusionPostings finish() {
    Uint32List offsets(List<List<int>?> rows) {
      final values = Uint32List(rows.length + 1);
      for (var i = 0; i < rows.length; i++) {
        values[i + 1] = values[i] + (rows[i]?.length ?? 0);
      }
      return values;
    }

    Uint16List flatten(List<List<int>?> rows, Uint32List starts) {
      final values = Uint16List(starts.last);
      for (var i = 0; i < rows.length; i++) {
        final row = rows[i];
        if (row != null) values.setAll(starts[i], row);
      }
      return values;
    }

    final termOffsets = offsets(byTerm);
    if (termOffsets.last == 0)
      throw const FormatException('No Greek Strong tokens in corpus');
    final verseOffsets = offsets(byVerse);
    final weights = Float64List(byTerm.length);
    baseWeights.forEach((n, w) => weights[n] = w);
    return AllusionPostings(
      documents: documents,
      baseWeights: weights,
      verseOffsets: verseOffsets,
      termOffsets: termOffsets,
      terms: flatten(byVerse, verseOffsets),
      verses: flatten(byTerm, termOffsets),
    );
  }
}
