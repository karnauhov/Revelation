class BibleVerseText {
  const BibleVerseText({required this.verseKey, required this.text});

  final String verseKey;
  final String text;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleVerseText &&
            other.verseKey == verseKey &&
            other.text == text;
  }

  @override
  int get hashCode => Object.hash(verseKey, text);
}
