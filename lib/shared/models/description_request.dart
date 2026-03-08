import 'package:revelation/shared/models/description_kind.dart';

sealed class DescriptionRequest {
  const DescriptionRequest();

  DescriptionKind get kind;
}

final class StrongDescriptionRequest extends DescriptionRequest {
  final int strongNumber;

  const StrongDescriptionRequest({required this.strongNumber});

  @override
  DescriptionKind get kind => DescriptionKind.strongNumber;
}

final class WordDescriptionRequest extends DescriptionRequest {
  final String? sourceId;
  final String? pageName;
  final int wordIndex;

  const WordDescriptionRequest({
    required this.wordIndex,
    this.sourceId,
    this.pageName,
  });

  @override
  DescriptionKind get kind => DescriptionKind.word;
}

final class VerseDescriptionRequest extends DescriptionRequest {
  final String? sourceId;
  final int chapterNumber;
  final int verseNumber;
  final String? pageName;
  final bool combineAcrossPages;

  const VerseDescriptionRequest({
    required this.chapterNumber,
    required this.verseNumber,
    this.sourceId,
    this.pageName,
    this.combineAcrossPages = true,
  });

  @override
  DescriptionKind get kind => DescriptionKind.verse;
}
