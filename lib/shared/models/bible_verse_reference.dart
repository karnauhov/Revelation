class BibleVerseReference {
  final String verseKey;
  final int bookId;
  final int chapter;
  final int verse;

  const BibleVerseReference({
    required this.verseKey,
    required this.bookId,
    required this.chapter,
    required this.verse,
  });

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleVerseReference &&
            other.verseKey == verseKey &&
            other.bookId == bookId &&
            other.chapter == chapter &&
            other.verse == verse;
  }

  @override
  int get hashCode => Object.hash(verseKey, bookId, chapter, verse);

  @override
  String toString() {
    return 'BibleVerseReference('
        'verseKey: $verseKey, '
        'bookId: $bookId, '
        'chapter: $chapter, '
        'verse: $verse'
        ')';
  }
}
