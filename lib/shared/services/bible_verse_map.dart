import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

class BibleVerseMap {
  static const String assetPath = 'assets/data/bible_verse_map.json';

  final int totalBooks;
  final int totalVerses;
  final String firstVerseKey;
  final String lastVerseKey;
  final List<String> _bookCodesById;
  final List<List<int>> _chapterVerseCountsByBookId;
  final List<BibleVerseReference?> _referencesByOrdinal;
  final Map<int, String> _verseKeysByReference;

  const BibleVerseMap._({
    required this.totalBooks,
    required this.totalVerses,
    required this.firstVerseKey,
    required this.lastVerseKey,
    required List<String> bookCodesById,
    required List<List<int>> chapterVerseCountsByBookId,
    required List<BibleVerseReference?> referencesByOrdinal,
    required Map<int, String> verseKeysByReference,
  }) : _bookCodesById = bookCodesById,
       _chapterVerseCountsByBookId = chapterVerseCountsByBookId,
       _referencesByOrdinal = referencesByOrdinal,
       _verseKeysByReference = verseKeysByReference;

  static Future<BibleVerseMap> loadFromAssets({AssetBundle? bundle}) async {
    final assetBundle = bundle ?? rootBundle;
    final jsonText = await assetBundle.loadString(assetPath);
    return BibleVerseMap.fromJson(
      json.decode(jsonText) as Map<String, Object?>,
    );
  }

  factory BibleVerseMap.fromJson(Map<String, Object?> json) {
    final verseKeyFormat = _requiredMap(json, 'verse_key_format');
    final base = _requiredInt(verseKeyFormat, 'base');
    final width = _requiredInt(verseKeyFormat, 'width');
    if (base != 36) {
      throw const FormatException('Bible verse map supports only base36 keys');
    }
    if (width != 3) {
      throw const FormatException(
        'Bible verse map supports only 3-character keys',
      );
    }

    final booksJson = _requiredList(json, 'books');
    final totalVerses = _requiredInt(json, 'verses_count');
    final maxBookId = booksJson
        .map((bookJson) => _requiredInt(_asMap(bookJson), 'id'))
        .fold<int>(
          0,
          (maxValue, bookId) => bookId > maxValue ? bookId : maxValue,
        );

    final bookCodesById = List<String>.filled(maxBookId + 1, '');
    final chapterVerseCountsByBookId = List<List<int>>.generate(
      maxBookId + 1,
      (_) => const <int>[],
    );
    final referencesByOrdinal = List<BibleVerseReference?>.filled(
      totalVerses + 1,
      null,
    );
    final verseKeysByReference = <int, String>{};

    var ordinal = 0;
    for (final bookJson in booksJson) {
      final book = _asMap(bookJson);
      final bookId = _requiredInt(book, 'id');
      if (bookId <= 0 || bookId > maxBookId) {
        throw FormatException('Invalid canonical book id: $bookId');
      }
      if (bookCodesById[bookId].isNotEmpty) {
        throw FormatException('Duplicate canonical book id: $bookId');
      }

      final code = _requiredString(book, 'code');
      final chapters = _requiredList(book, 'chapters')
          .map((value) => _asPositiveInt(value, 'chapter verse count'))
          .toList(growable: false);
      if (chapters.isEmpty) {
        throw FormatException('Book $bookId has no chapters');
      }

      bookCodesById[bookId] = code;
      chapterVerseCountsByBookId[bookId] = List<int>.unmodifiable(chapters);

      for (
        var chapterIndex = 0;
        chapterIndex < chapters.length;
        chapterIndex++
      ) {
        final chapter = chapterIndex + 1;
        for (var verse = 1; verse <= chapters[chapterIndex]; verse++) {
          ordinal++;
          final verseKey = _base36(ordinal).padLeft(width, '0');
          final reference = BibleVerseReference(
            verseKey: verseKey,
            bookId: bookId,
            chapter: chapter,
            verse: verse,
          );
          referencesByOrdinal[ordinal] = reference;
          verseKeysByReference[_referenceKey(bookId, chapter, verse)] =
              verseKey;
        }
      }
    }

    if (ordinal != totalVerses) {
      throw FormatException(
        'Bible verse map count mismatch: expected $totalVerses, got $ordinal',
      );
    }

    final firstVerseKey = _requiredString(verseKeyFormat, 'first');
    final lastVerseKey = _requiredString(verseKeyFormat, 'last');
    if (referencesByOrdinal[1]?.verseKey != firstVerseKey ||
        referencesByOrdinal[totalVerses]?.verseKey != lastVerseKey) {
      throw const FormatException('Bible verse map key bounds mismatch');
    }

    return BibleVerseMap._(
      totalBooks: booksJson.length,
      totalVerses: totalVerses,
      firstVerseKey: firstVerseKey,
      lastVerseKey: lastVerseKey,
      bookCodesById: List<String>.unmodifiable(bookCodesById),
      chapterVerseCountsByBookId: List<List<int>>.unmodifiable(
        chapterVerseCountsByBookId,
      ),
      referencesByOrdinal: List<BibleVerseReference?>.unmodifiable(
        referencesByOrdinal,
      ),
      verseKeysByReference: Map<int, String>.unmodifiable(verseKeysByReference),
    );
  }

  BibleVerseReference? referenceForKey(String verseKey) {
    final ordinal = _base36Ordinal(verseKey);
    if (ordinal == null ||
        ordinal <= 0 ||
        ordinal >= _referencesByOrdinal.length) {
      return null;
    }
    return _referencesByOrdinal[ordinal];
  }

  String? verseKeyFor({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    if (!_containsReference(bookId: bookId, chapter: chapter, verse: verse)) {
      return null;
    }
    return _verseKeysByReference[_referenceKey(bookId, chapter, verse)];
  }

  List<int> get bookIds {
    return List<int>.unmodifiable(
      List<int>.generate(
        _bookCodesById.length,
        (index) => index,
      ).where((bookId) => bookId > 0 && _bookCodesById[bookId].isNotEmpty),
    );
  }

  bool containsReference({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    return _containsReference(bookId: bookId, chapter: chapter, verse: verse);
  }

  BibleVerseReference referenceFor({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    final verseKey = verseKeyFor(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    if (verseKey == null) {
      throw RangeError(
        'Unknown Bible reference: book $bookId, chapter $chapter, verse $verse',
      );
    }
    return BibleVerseReference(
      verseKey: verseKey,
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
  }

  BibleVerseReference normalizedReference({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    final normalizedBookId =
        bookId >= 1 &&
            bookId < _chapterVerseCountsByBookId.length &&
            _chapterVerseCountsByBookId[bookId].isNotEmpty
        ? bookId
        : 1;
    final chapterCount = _chapterVerseCountsByBookId[normalizedBookId].length;
    final normalizedChapter = chapter.clamp(1, chapterCount).toInt();
    final verseCount =
        _chapterVerseCountsByBookId[normalizedBookId][normalizedChapter - 1];
    final normalizedVerse = verse.clamp(1, verseCount).toInt();
    return referenceFor(
      bookId: normalizedBookId,
      chapter: normalizedChapter,
      verse: normalizedVerse,
    );
  }

  BibleVerseReference firstReferenceInChapter({
    required int bookId,
    required int chapter,
  }) {
    return normalizedReference(bookId: bookId, chapter: chapter, verse: 1);
  }

  BibleVerseReference? adjacentChapterReference({
    required int bookId,
    required int chapter,
    required bool forward,
  }) {
    _checkBookId(bookId);
    final currentBookChapterCount = chapterCount(bookId);
    if (chapter < 1 || chapter > currentBookChapterCount) {
      throw RangeError.value(chapter, 'chapter');
    }

    if (forward) {
      if (chapter < currentBookChapterCount) {
        return firstReferenceInChapter(bookId: bookId, chapter: chapter + 1);
      }
      final nextBookId = bookId + 1;
      if (nextBookId < _bookCodesById.length &&
          _bookCodesById[nextBookId].isNotEmpty) {
        return firstReferenceInChapter(bookId: nextBookId, chapter: 1);
      }
      return null;
    }

    if (chapter > 1) {
      return firstReferenceInChapter(bookId: bookId, chapter: chapter - 1);
    }
    final previousBookId = bookId - 1;
    if (previousBookId >= 1 && _bookCodesById[previousBookId].isNotEmpty) {
      return firstReferenceInChapter(
        bookId: previousBookId,
        chapter: chapterCount(previousBookId),
      );
    }
    return null;
  }

  List<String> verseKeysForChapter({
    required int bookId,
    required int chapter,
  }) {
    final verseTotal = verseCount(bookId: bookId, chapter: chapter);
    return List<String>.unmodifiable(
      List<String>.generate(verseTotal, (index) {
        return verseKeyFor(bookId: bookId, chapter: chapter, verse: index + 1)!;
      }),
    );
  }

  String bookCode(int bookId) {
    _checkBookId(bookId);
    return _bookCodesById[bookId];
  }

  int chapterCount(int bookId) {
    _checkBookId(bookId);
    return _chapterVerseCountsByBookId[bookId].length;
  }

  int verseCount({required int bookId, required int chapter}) {
    _checkBookId(bookId);
    final chapters = _chapterVerseCountsByBookId[bookId];
    if (chapter < 1 || chapter > chapters.length) {
      throw RangeError.value(chapter, 'chapter');
    }
    return chapters[chapter - 1];
  }

  bool _containsReference({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    if (bookId < 1 || bookId >= _chapterVerseCountsByBookId.length) {
      return false;
    }
    final chapters = _chapterVerseCountsByBookId[bookId];
    if (chapters.isEmpty || chapter < 1 || chapter > chapters.length) {
      return false;
    }
    return verse >= 1 && verse <= chapters[chapter - 1];
  }

  void _checkBookId(int bookId) {
    if (bookId < 1 ||
        bookId >= _bookCodesById.length ||
        _bookCodesById[bookId].isEmpty) {
      throw RangeError.value(bookId, 'bookId');
    }
  }
}

Map<String, Object?> _requiredMap(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return value.cast<String, Object?>();
  }
  throw FormatException('Missing map field: $key');
}

List<Object?> _requiredList(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is List<Object?>) {
    return value;
  }
  if (value is List) {
    return value.cast<Object?>();
  }
  throw FormatException('Missing list field: $key');
}

int _requiredInt(Map<String, Object?> json, String key) {
  return _asPositiveInt(json[key], key);
}

int _asPositiveInt(Object? value, String label) {
  if (value is! int || value <= 0) {
    throw FormatException('Invalid positive integer field: $label');
  }
  return value;
}

String _requiredString(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw FormatException('Missing string field: $key');
}

Map<String, Object?> _asMap(Object? value) {
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return value.cast<String, Object?>();
  }
  throw const FormatException('Expected object in Bible verse map');
}

int _referenceKey(int bookId, int chapter, int verse) {
  return bookId * 1000000 + chapter * 1000 + verse;
}

int? _base36Ordinal(String verseKey) {
  if (verseKey.length != 3) {
    return null;
  }
  var value = 0;
  for (final codeUnit in verseKey.toUpperCase().codeUnits) {
    final digit = _base36Digit(codeUnit);
    if (digit == null) {
      return null;
    }
    value = value * 36 + digit;
  }
  return value;
}

int? _base36Digit(int codeUnit) {
  if (codeUnit >= 48 && codeUnit <= 57) {
    return codeUnit - 48;
  }
  if (codeUnit >= 65 && codeUnit <= 90) {
    return codeUnit - 55;
  }
  return null;
}

String _base36(int number) {
  if (number <= 0) {
    throw RangeError.value(number, 'number');
  }
  const alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  var value = number;
  final characters = <String>[];
  while (value > 0) {
    final remainder = value % 36;
    characters.add(alphabet[remainder]);
    value ~/= 36;
  }
  return characters.reversed.join();
}
