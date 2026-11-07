@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../integration_test/smoke/smoke_test_harness.dart';

void main() {
  testWidgets(
    'home readiness does not wait for independent loading animation',
    (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Column(
              children: [Text('Home shell'), CircularProgressIndicator()],
            ),
          ),
        ),
      );
      try {
        await expectLater(
          () => pumpAndSettleSmoke(
            tester,
            timeout: const Duration(milliseconds: 64),
          ),
          throwsA(isA<FlutterError>()),
        );
        await pumpUntilSmoke(
          tester,
          isReady: () => find.text('Home shell').evaluate().length == 1,
          reason: 'the home shell',
        );
        expect(find.text('Home shell'), findsOneWidget);
        expect(tester.binding.hasScheduledFrame, isTrue);
      } finally {
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      }
    },
  );

  testWidgets('readiness waits for the requested asynchronous result', (
    tester,
  ) async {
    var ready = false;
    final timer = Timer(const Duration(milliseconds: 48), () => ready = true);
    addTearDown(timer.cancel);
    await pumpUntilSmoke(
      tester,
      isReady: () => ready,
      reason: 'the delayed shell',
    );
    expect(ready, isTrue);
  });

  testWidgets('drawer can finish opening and closing while content loads', (
    tester,
  ) async {
    final scaffoldKey = GlobalKey<ScaffoldState>();
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          key: scaffoldKey,
          body: const CircularProgressIndicator(),
          drawer: const Drawer(child: Text('Navigation')),
        ),
      ),
    );
    final drawer = find.byType(Drawer);
    try {
      scaffoldKey.currentState!.openDrawer();
      await pumpUntilSmoke(
        tester,
        isReady: () =>
            drawer.evaluate().length == 1 &&
            tester.getTopLeft(drawer).dx.abs() < 0.1,
        reason: 'the drawer to finish opening',
      );
      expect(scaffoldKey.currentState!.isDrawerOpen, isTrue);
      expect(tester.getTopLeft(drawer).dx, closeTo(0, 0.1));
      expect(tester.binding.hasScheduledFrame, isTrue);
      scaffoldKey.currentState!.closeDrawer();
      await pumpUntilSmoke(
        tester,
        isReady: () =>
            !scaffoldKey.currentState!.isDrawerOpen &&
            drawer.evaluate().isEmpty,
        reason: 'the drawer to finish closing',
      );
      expect(drawer, findsNothing);
      expect(tester.binding.hasScheduledFrame, isTrue);
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
    }
  });

  testWidgets('missing readiness fails within the deadline with its reason', (
    tester,
  ) async {
    final started = tester.binding.clock.now();
    await expectLater(
      () => pumpUntilSmoke(
        tester,
        isReady: () => false,
        reason: 'the missing home shell',
        timeout: const Duration(milliseconds: 64),
      ),
      throwsA(
        isA<FlutterError>().having(
          (error) => error.toString(),
          'message',
          contains('the missing home shell'),
        ),
      ),
    );
    expect(
      tester.binding.clock.now().difference(started),
      lessThanOrEqualTo(const Duration(milliseconds: 80)),
    );
  });

  testWidgets('nonpositive deadlines and frame steps are rejected', (
    tester,
  ) async {
    for (final durations in [
      (step: Duration.zero, timeout: const Duration(seconds: 1)),
      (step: const Duration(milliseconds: 16), timeout: Duration.zero),
    ]) {
      expect(
        () => pumpUntilSmoke(
          tester,
          isReady: () => true,
          reason: 'invalid wait',
          step: durations.step,
          timeout: durations.timeout,
        ),
        throwsArgumentError,
      );
    }
  });
}
