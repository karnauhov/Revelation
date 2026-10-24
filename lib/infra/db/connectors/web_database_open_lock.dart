import 'dart:async';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:revelation/infra/db/connectors/database_open_queue.dart';
import 'package:web/web.dart' as web;

const webDatabaseOpenLockName = 'revelation-drift-database-open';

final _openQueue = DatabaseOpenQueue();

/// Drift 2.30's workers share an OPFS feature-detection file. Serialize the
/// complete probe/open sequence, including across tabs when Web Locks exist.
/// See https://github.com/simolus3/drift/issues/3856.
Future<T> withWebDatabaseOpenLock<T>(Future<T> Function() open) {
  return _openQueue.run(() async {
    final navigator = web.window.navigator;
    if (!navigator.has('locks')) {
      return open();
    }

    late T result;
    Object? failure;
    StackTrace? failureStack;

    final callback = Zone.current.bindUnaryCallback((web.Lock? _) {
      return () async {
        try {
          result = await open();
        } catch (error, stackTrace) {
          failure = error;
          failureStack = stackTrace;
        }
        return null;
      }().toJS;
    });

    // The browser holds the lock until this callback's promise settles. Keep
    // Dart errors in Dart so their type and original stack survive JS interop.
    await navigator.locks
        .request(webDatabaseOpenLockName, callback.toJS)
        .toDart;
    if (failure != null) {
      Error.throwWithStackTrace(failure!, failureStack!);
    }
    return result;
  });
}
