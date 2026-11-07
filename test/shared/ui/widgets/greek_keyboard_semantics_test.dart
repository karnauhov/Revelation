@Tags(['widget'])
import 'dart:ui' show SemanticsAction;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/shared/ui/widgets/greek_keyboard.dart';

void main() {
  testWidgets(
    'Greek search suffix keeps valid semantics through route slides',
    (tester) async {
      tester.view.physicalSize = const Size(784, 611);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final semantics = tester.ensureSemantics();
      try {
        await _exerciseRouteSlides(tester);
      } finally {
        semantics.dispose();
      }
    },
  );
}

Future<void> _exerciseRouteSlides(WidgetTester tester) async {
  final controller = TextEditingController();
  final focusNode = FocusNode();
  addTearDown(controller.dispose);
  addTearDown(focusNode.dispose);
  final router = GoRouter(
    routes: [
      GoRoute(
        path: '/',
        pageBuilder: (context, state) => buildPageWithDefaultTransition<void>(
          context: context,
          state: state,
          child: const Scaffold(body: Text('Home')),
        ),
      ),
      GoRoute(
        path: '/search',
        pageBuilder: (context, state) => buildPageWithDefaultTransition<void>(
          context: context,
          state: state,
          child: Scaffold(
            appBar: AppBar(title: const Text('Greek search')),
            body: Align(
              alignment: Alignment.topLeft,
              child: SizedBox(
                width: 300,
                child: TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: InputDecoration(
                    labelText: 'Search',
                    suffixIcon: GreekKeyboardButton(
                      controller: controller,
                      focusNode: focusNode,
                      tooltip: 'Greek keyboard',
                    ),
                    suffixIconConstraints: const BoxConstraints.tightFor(
                      width: 48,
                      height: 42,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    ],
  );
  addTearDown(router.dispose);
  await tester.pumpWidget(MaterialApp.router(routerConfig: router));
  await tester.pumpAndSettle();
  for (var cycle = 0; cycle < 3; cycle++) {
    router.push<void>('/search');
    await _pumpTransition(tester);
    expect(find.byKey(const Key('greek_keyboard_button')), findsOneWidget);
    final buttonSemantics = tester
        .getSemantics(find.byKey(const Key('greek_keyboard_button')))
        .getSemanticsData();
    expect(buttonSemantics.tooltip, 'Greek keyboard');
    expect(buttonSemantics.hasAction(SemanticsAction.tap), isTrue);
    await tester.tap(find.byTooltip('Greek keyboard'));
    await tester.pumpAndSettle();
    final keySemantics = tester
        .getSemantics(find.byKey(const Key('greek_keyboard_key_α')))
        .getSemanticsData();
    expect(keySemantics.label, 'α');
    expect(keySemantics.hasAction(SemanticsAction.tap), isTrue);
    await tester.tap(find.byKey(const Key('greek_keyboard_key_α')));
    await tester.pump();
    expect(controller.text, 'α' * (cycle + 1));
    router.pop();
    await _pumpTransition(tester);
  }
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpAndSettle();
  expect(tester.takeException(), isNull);
}

Future<void> _pumpTransition(WidgetTester tester) async {
  await tester.pump();
  for (var frame = 0; frame < 22; frame++) {
    await tester.pump(const Duration(milliseconds: 16));
    expect(tester.takeException(), isNull, reason: 'transition frame $frame');
  }
  await tester.pumpAndSettle();
}
