import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/shared/config/app_constants.dart';

abstract interface class StrongUsageBibleTextProvider {
  Future<String?> loadVerseText(String verseKey);
}

class DefaultStrongUsageBibleTextProvider
    implements StrongUsageBibleTextProvider {
  DefaultStrongUsageBibleTextProvider({
    BibleModuleDataSource moduleDataSource = const LocalBibleModuleDataSource(),
    this.moduleFile = AppConstants.defaultBibleModuleDB,
  }) : _moduleDataSource = moduleDataSource;

  final BibleModuleDataSource _moduleDataSource;
  final String moduleFile;
  final Map<String, String?> _cache = <String, String?>{};
  final Map<String, Future<String?>> _inFlight = <String, Future<String?>>{};

  @override
  Future<String?> loadVerseText(String verseKey) {
    final normalizedVerseKey = verseKey.trim().toUpperCase();
    if (normalizedVerseKey.isEmpty) {
      return Future<String?>.value(null);
    }
    if (_cache.containsKey(normalizedVerseKey)) {
      return Future<String?>.value(_cache[normalizedVerseKey]);
    }

    return _inFlight[normalizedVerseKey] ??= _loadVerseText(normalizedVerseKey)
        .whenComplete(() {
          _inFlight.remove(normalizedVerseKey);
        });
  }

  Future<String?> _loadVerseText(String verseKey) async {
    final database = _moduleDataSource.openModule(moduleFile);
    try {
      final verses = await database.readVersesByKeys(<String>[verseKey]);
      if (verses.isEmpty) {
        _cache[verseKey] = null;
        return null;
      }
      final text = plainBibleText(verses.first.text);
      final normalizedText = text.isEmpty ? null : text;
      _cache[verseKey] = normalizedText;
      return normalizedText;
    } finally {
      await database.close();
    }
  }
}
