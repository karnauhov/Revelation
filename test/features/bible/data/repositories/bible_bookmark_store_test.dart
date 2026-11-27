import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_bookmark_store.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_bookmarks_cubit.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

const _source = (bookId: 66, chapter: 1, verse: 13);
const _target = (bookId: 54, chapter: 1, verse: 3);
const _first = BibleBookmark(
  id: 'first',
  location: _source,
  name: 'Утіха',
  color: BibleBookmarkColor.green,
);
const _second = BibleBookmark(
  id: 'second',
  location: _source,
  name: 'Bookmark 4',
  color: BibleBookmarkColor.violet,
);

void main() {
  late _ControlledPreferences preferences;
  late BibleBookmarkStore store;
  setUp(() {
    final previous = SharedPreferencesAsyncPlatform.instance;
    addTearDown(() => SharedPreferencesAsyncPlatform.instance = previous);
    preferences = _ControlledPreferences();
    SharedPreferencesAsyncPlatform.instance = preferences;
    store = BibleBookmarkStore();
  });

  test(
    'serialized changes survive reopening and retain order and identity',
    () async {
      expect(await store.load(), isEmpty);
      await Future.wait([
        store.save(_first),
        store.save(_second),
        store.move(_first.id, _target),
      ]);
      const moved = BibleBookmark(
        id: 'first',
        location: _target,
        name: 'Утіха',
        color: BibleBookmarkColor.green,
      );
      final reopened = BibleBookmarkStore();
      expect(await reopened.load(), [_second, moved]);
      await store.remove(moved.id);
      await store.move(moved.id, _source);
      expect(await reopened.load(), [_second]);
    },
  );

  test(
    'a failed write leaves stored data intact and permits a retry',
    () async {
      await store.save(_first);
      preferences.rejectNextWrite = true;
      await expectLater(store.remove(_first.id), throwsStateError);
      expect(await store.load(), [_first]);
      expect(await store.save(_second), [_second, _first]);
    },
  );

  test('unreadable data is preserved when a mutation is attempted', () async {
    const raw = '{"futureFormat":true}';
    final local = SharedPreferencesAsync();
    await local.setString(BibleBookmarkStore.storageKey, raw);
    await expectLater(store.load(), throwsFormatException);
    await expectLater(store.save(_first), throwsFormatException);
    expect(await local.getString(BibleBookmarkStore.storageKey), raw);
  });

  test('a failed or rapid save keeps the last committed snapshot', () async {
    final cubit = BibleBookmarksCubit(store);
    addTearDown(cubit.close);
    await store.save(_first);
    await cubit.load();
    preferences.rejectNextWrite = true;
    await cubit.remove(_first.id);
    expect(cubit.state.status, BibleBookmarksStatus.saveFailed);
    expect(cubit.state.bookmarks, [_first]);

    final gate = preferences.writeGate = Completer<void>();
    final move = cubit.move(_first, _target);
    await cubit.remove(_first.id);
    expect(cubit.state.status, BibleBookmarksStatus.saving);
    expect(cubit.state.bookmarks, [_first]);
    gate.complete();
    await move;
    expect(cubit.state.bookmarks.single.location, _target);
  });

  test('closing during a write still persists the change', () async {
    final cubit = BibleBookmarksCubit(store);
    await cubit.load();
    final gate = preferences.writeGate = Completer<void>();
    final save = cubit.save(
      location: _source,
      name: '  Read later  ',
      color: BibleBookmarkColor.amber,
    );
    await cubit.close();
    gate.complete();
    await save;
    final bookmark = (await BibleBookmarkStore().load()).single;
    expect(bookmark.location, _source);
    expect(bookmark.name, 'Read later');
  });
}

final class _ControlledPreferences extends InMemorySharedPreferencesAsync {
  _ControlledPreferences() : super.empty();

  bool rejectNextWrite = false;
  Completer<void>? writeGate;

  @override
  Future<bool> setString(
    String key,
    String value,
    SharedPreferencesOptions options,
  ) async {
    if (rejectNextWrite) {
      rejectNextWrite = false;
      throw StateError('Simulated write failure');
    }
    await writeGate?.future;
    return super.setString(key, value, options);
  }
}
