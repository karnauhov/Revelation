import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/bible/data/repositories/bible_bookmark_store.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';

enum BibleBookmarksStatus { loading, loadFailed, ready, saving, saveFailed }

class BibleBookmarksState {
  const BibleBookmarksState(this.status, [this.bookmarks = const []]);

  final BibleBookmarksStatus status;
  final List<BibleBookmark> bookmarks;

  bool get canChange =>
      status == BibleBookmarksStatus.ready ||
      status == BibleBookmarksStatus.saveFailed;

  @override
  bool operator ==(Object other) =>
      other is BibleBookmarksState &&
      status == other.status &&
      listEquals(bookmarks, other.bookmarks);

  @override
  int get hashCode => Object.hash(status, Object.hashAll(bookmarks));
}

class BibleBookmarksCubit extends Cubit<BibleBookmarksState> {
  BibleBookmarksCubit(this._store)
    : super(const BibleBookmarksState(BibleBookmarksStatus.loading));

  final BibleBookmarkStore _store;
  bool _readInProgress = false;

  Future<void> load() async {
    if (isClosed ||
        _readInProgress ||
        state.status == BibleBookmarksStatus.saving) {
      return;
    }
    _readInProgress = true;
    emit(const BibleBookmarksState(BibleBookmarksStatus.loading));
    try {
      final bookmarks = await _store.load();
      if (isClosed) return;
      emit(
        BibleBookmarksState(
          BibleBookmarksStatus.ready,
          List<BibleBookmark>.unmodifiable(bookmarks),
        ),
      );
    } catch (_) {
      if (isClosed) return;
      emit(const BibleBookmarksState(BibleBookmarksStatus.loadFailed));
    } finally {
      _readInProgress = false;
    }
  }

  Future<void> save({
    String? id,
    required BibleBookmarkLocation location,
    required String name,
    required BibleBookmarkColor color,
  }) {
    final label = name.trim();
    if (label.isEmpty) return Future<void>.value();
    return _mutate(() {
      final bookmark = BibleBookmark(
        id:
            id ??
            '${DateTime.now().microsecondsSinceEpoch}-${Random.secure().nextInt(1 << 30)}',
        location: location,
        name: label,
        color: color,
      );
      return _store.save(bookmark);
    });
  }

  Future<void> remove(String id) => _mutate(() => _store.remove(id));

  Future<void> move(BibleBookmark bookmark, BibleBookmarkLocation location) =>
      _mutate(() => _store.move(bookmark.id, location));

  Future<void> _mutate(Future<List<BibleBookmark>> Function() write) async {
    if (isClosed || !state.canChange) return;
    final previous = state.bookmarks;
    emit(BibleBookmarksState(BibleBookmarksStatus.saving, previous));
    try {
      final bookmarks = await write();
      if (isClosed) return;
      emit(BibleBookmarksState(BibleBookmarksStatus.ready, bookmarks));
    } catch (_) {
      if (isClosed) return;
      emit(BibleBookmarksState(BibleBookmarksStatus.saveFailed, previous));
    }
  }
}
