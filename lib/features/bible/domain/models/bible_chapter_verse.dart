import 'package:revelation/shared/models/bible_verse_reference.dart';

class BibleChapterVerse {
  const BibleChapterVerse({required this.reference, required this.text});

  final BibleVerseReference reference;
  final String text;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleChapterVerse &&
            other.reference == reference &&
            other.text == text;
  }

  @override
  int get hashCode => Object.hash(reference, text);
}
