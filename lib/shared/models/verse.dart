import 'dart:ui';

class Verse {
  final int chapterNumber;
  final int verseNumber;
  final Offset labelPosition;
  final List<int> wordIndexes;
  final List<List<Offset>> contours;

  const Verse({
    required this.chapterNumber,
    required this.verseNumber,
    required this.labelPosition,
    this.wordIndexes = const [],
    this.contours = const [],
  });
}
