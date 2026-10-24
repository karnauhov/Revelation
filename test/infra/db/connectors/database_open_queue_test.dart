import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/database_open_queue.dart';

void main() {
  test('concurrent opens run in order without overlapping', () async {
    final queue = DatabaseOpenQueue();
    final release = Completer<void>();
    final events = <String>[];
    var active = 0;

    Future<int> open(int id) => queue.run(() async {
      expect(active++, 0);
      events.add('start $id');
      if (id == 0) await release.future;
      await Future<void>.delayed(Duration.zero);
      events.add('end $id');
      active--;
      return id;
    });

    final opens = [for (var i = 0; i < 3; i++) open(i)];
    await Future<void>.delayed(Duration.zero);
    expect(events, ['start 0']);
    release.complete();
    expect(await Future.wait(opens), [0, 1, 2]);
    expect(events, [
      'start 0',
      'end 0',
      'start 1',
      'end 1',
      'start 2',
      'end 2',
    ]);
    expect(active, 0);
  });

  for (final asynchronous in [false, true]) {
    test(
      'a ${asynchronous ? 'async' : 'sync'} failure releases the queue',
      () async {
        final queue = DatabaseOpenQueue();
        final failure = StateError('open failed');
        final stack = StackTrace.current;
        final failed = queue.run<int>(() {
          if (asynchronous) return Future<int>.error(failure, stack);
          Error.throwWithStackTrace(failure, stack);
        });
        final failedExpectation = expectLater(failed, throwsA(same(failure)));
        final next = queue.run(() async => 42);

        await failedExpectation;
        expect(await next, 42);
      },
    );
  }
}
