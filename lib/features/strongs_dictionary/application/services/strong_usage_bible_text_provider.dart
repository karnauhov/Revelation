import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';

abstract interface class StrongUsageBibleTextProvider {
  Future<String?> loadVerseText(String verseKey);
}

class DefaultStrongUsageBibleTextProvider
    implements StrongUsageBibleTextProvider {
  const DefaultStrongUsageBibleTextProvider(this._library);

  final BibleLibraryRepository Function() _library;

  @override
  Future<String?> loadVerseText(String verseKey) async {
    final normalizedVerseKey = verseKey.trim().toUpperCase();
    if (normalizedVerseKey.isEmpty) return null;
    final preview = await _library().loadPreview([normalizedVerseKey]);
    final verse = preview.verses.firstOrNull;
    return verse == null ? null : plainBibleText(verse.text);
  }
}
