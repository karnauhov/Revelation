class BibleVerseText {
  const BibleVerseText({
    required this.verseKey,
    required this.text,
    this.comment = '',
  });

  final String verseKey;
  final String text;
  final String comment;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleVerseText &&
            other.verseKey == verseKey &&
            other.text == text &&
            other.comment == comment;
  }

  @override
  int get hashCode => Object.hash(verseKey, text, comment);
}
