import 'dart:async';

/// Keeps storage discovery and database initialization from overlapping.
class DatabaseOpenQueue {
  Future<void> _tail = Future.value();

  Future<T> run<T>(Future<T> Function() open) {
    final previous = _tail;
    final finished = Completer<void>();
    _tail = finished.future;

    return () async {
      await previous;
      try {
        return await open();
      } finally {
        finished.complete();
      }
    }();
  }
}
