import 'package:flutter/material.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';

class BibleVerseCommentButton extends StatelessWidget {
  const BibleVerseCommentButton({super.key, required this.verse});

  final BibleChapterVerse verse;

  @override
  Widget build(BuildContext context) {
    if (verse.comment.trim().isEmpty) {
      return const SizedBox.shrink();
    }
    final localizations = AppLocalizations.of(context)!;
    return IconButton(
      key: Key('bible_verse_comment_${verse.reference.verse}'),
      tooltip: localizations.bible_show_footnotes(verse.reference.verse),
      icon: const Icon(Icons.notes_outlined),
      onPressed: () => showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          key: const Key('bible_verse_comment_dialog'),
          title: Text(
            localizations.bible_verse_footnotes(
              '${verse.reference.chapter}:${verse.reference.verse}',
            ),
          ),
          content: SingleChildScrollView(child: SelectableText(verse.comment)),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(localizations.close),
            ),
          ],
        ),
      ),
    );
  }
}
