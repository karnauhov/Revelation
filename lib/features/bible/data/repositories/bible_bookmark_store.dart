import 'dart:async';
import 'dart:convert';

import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';
import 'package:shared_preferences/shared_preferences.dart';

class BibleBookmarkStore {
  BibleBookmarkStore({SharedPreferencesAsync? preferences})
    : _preferencesOverride = preferences;

  static const storageKey = 'bible.bookmarks.v1';
  final SharedPreferencesAsync? _preferencesOverride;
  Future<void>? _pendingWrite;

  SharedPreferencesAsync get _preferences =>
      _preferencesOverride ?? SharedPreferencesAsync();

  Future<List<BibleBookmark>> load() async {
    await _pendingWrite;
    return _read();
  }

  Future<List<BibleBookmark>> save(BibleBookmark bookmark) =>
      _write((bookmarks) {
        final index = bookmarks.indexWhere((item) => item.id == bookmark.id);
        if (index == -1) {
          bookmarks.insert(0, bookmark);
        } else {
          bookmarks[index] = bookmark;
        }
      });

  Future<List<BibleBookmark>> remove(String id) =>
      _write((bookmarks) => bookmarks.removeWhere((item) => item.id == id));

  Future<List<BibleBookmark>> move(String id, BibleBookmarkLocation location) =>
      _write((bookmarks) {
        final index = bookmarks.indexWhere((item) => item.id == id);
        if (index == -1) return;
        final old = bookmarks[index];
        bookmarks[index] = BibleBookmark(
          id: old.id,
          location: location,
          name: old.name,
          color: old.color,
        );
      });

  Future<List<BibleBookmark>> _read() async {
    final value = await _preferences.getString(storageKey);
    if (value == null) return [];
    final decoded = jsonDecode(value);
    if (decoded is! List) {
      throw const FormatException('Invalid Bible bookmark list');
    }
    return [for (final item in decoded) _decode(item)];
  }

  Future<List<BibleBookmark>> _write(
    void Function(List<BibleBookmark>) update,
  ) {
    final previous = _pendingWrite;
    Future<List<BibleBookmark>> apply() async {
      if (previous != null) await previous;
      final bookmarks = await _read();
      update(bookmarks);
      await _preferences.setString(
        storageKey,
        jsonEncode([
          for (final bookmark in bookmarks)
            {
              'id': bookmark.id,
              'bookId': bookmark.location.bookId,
              'chapter': bookmark.location.chapter,
              'verse': bookmark.location.verse,
              'name': bookmark.name,
              'color': bookmark.color.name,
            },
        ]),
      );
      return List<BibleBookmark>.unmodifiable(bookmarks);
    }

    final write = apply();
    final settled = write.then<void>(
      (_) {},
      onError: (Object _, StackTrace _) {},
    );
    _pendingWrite = settled;
    unawaited(
      settled.then((_) {
        if (identical(_pendingWrite, settled)) _pendingWrite = null;
      }),
    );
    return write;
  }

  BibleBookmark _decode(Object? value) {
    if (value
        case {
          'id': final String id,
          'bookId': final int bookId,
          'chapter': final int chapter,
          'verse': final int verse,
          'name': final String name,
          'color': final String color,
        }
        when id.isNotEmpty &&
            bookId > 0 &&
            bookId <= 66 &&
            chapter > 0 &&
            verse > 0 &&
            name.trim().isNotEmpty) {
      return BibleBookmark(
        id: id,
        location: (bookId: bookId, chapter: chapter, verse: verse),
        name: name,
        color: BibleBookmarkColor.values.byName(color),
      );
    }
    throw const FormatException('Invalid Bible bookmark');
  }
}
