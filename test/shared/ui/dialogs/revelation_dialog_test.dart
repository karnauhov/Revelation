@Tags(['widget'])
import 'dart:async';
import 'dart:ui' show PointerDeviceKind;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';

void main() {
  testWidgets('the filled action follows text actions when they wrap', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(320, 560));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final colors = ColorScheme.fromSeed(
      seedColor: Colors.teal,
      brightness: Brightness.dark,
    );
    var selected = false;
    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData(colorScheme: colors),
        home: RevelationDialog(
          title: const Text('Select a passage'),
          content: const Text('Choose a reference'),
          secondaryActions: [
            RevelationDialogAction(
              label: 'Close this window',
              onPressed: () {},
            ),
            RevelationDialogAction(label: 'Refresh the list', onPressed: () {}),
          ],
          primaryAction: RevelationDialogAction(
            label: 'Confirm selection',
            onPressed: () => selected = true,
          ),
        ),
      ),
    );

    expect(find.byType(TextButton), findsNWidgets(2));
    final primary = find.byType(FilledButton);
    final style = tester.widget<FilledButton>(primary).style!;
    expect(style.backgroundColor!.resolve({}), colors.primary);
    expect(style.foregroundColor!.resolve({}), colors.onPrimary);
    expect(style.shape!.resolve({}), isA<StadiumBorder>());
    expect(
      tester.getTopLeft(primary).dy,
      greaterThan(tester.getTopLeft(find.byType(TextButton).last).dy),
    );
    await tester.tap(primary);
    expect(selected, isTrue);
  });

  testWidgets('mouse and touch move the header within the available bounds', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(900, 680);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetViewInsets);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);

    await tester.pumpWidget(
      MaterialApp(
        home: RevelationDialog(
          title: const Text('Adjust document'),
          scrollContent: true,
          content: Column(
            children: [
              for (var index = 0; index < 14; index++) Text('Line \$index'),
              const TextField(),
            ],
          ),
          secondaryActions: [
            RevelationDialogAction(label: 'Close', onPressed: () {}),
          ],
        ),
      ),
    );

    final title = find.text('Adjust document');
    final surface = _dialogSurface;
    final original = tester.getRect(surface);
    await tester.drag(
      title,
      const Offset(140, 85),
      kind: PointerDeviceKind.mouse,
    );
    await tester.pumpAndSettle();
    final moved = tester.getRect(surface);
    expect(moved.left, greaterThan(original.left));
    expect(moved.top, greaterThan(original.top));

    await tester.drag(title, const Offset(-700, -500));
    await tester.pumpAndSettle();
    final atEdge = tester.getRect(surface);
    expect(atEdge.left, closeTo(10, 1));
    expect(atEdge.top, closeTo(10, 1));

    tester.view.physicalSize = const Size(320, 600);
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    tester.view.viewInsets = const FakeViewPadding(bottom: 280);
    await tester.pumpAndSettle();
    final compact = tester.getRect(surface);
    expect(compact.left, greaterThanOrEqualTo(10));
    expect(compact.right, lessThanOrEqualTo(310));
    expect(compact.top, greaterThanOrEqualTo(10));
    expect(compact.bottom, lessThanOrEqualTo(310));
    expect(
      find.widgetWithText(TextButton, 'Close').hitTestable(),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'nested dialog gets its own position and restores focus on Escape',
    (tester) async {
      final launcherFocus = FocusNode();
      addTearDown(launcherFocus.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                autofocus: true,
                focusNode: launcherFocus,
                onPressed: () => unawaited(
                  showDialog<void>(
                    context: context,
                    builder: (parentContext) => RevelationDialog(
                      title: const Text('Parent window'),
                      content: const Text('Parent content'),
                      primaryAction: RevelationDialogAction(
                        label: 'Open child',
                        onPressed: () => unawaited(
                          showDialog<void>(
                            context: parentContext,
                            builder: (_) => const RevelationDialog(
                              title: Text('Child window'),
                              content: Text('Child content'),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                child: const Text('Open parent'),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(launcherFocus.hasPrimaryFocus, isTrue);

      await tester.tap(find.text('Open parent'));
      await tester.pumpAndSettle();
      await tester.drag(find.text('Parent window'), const Offset(120, 55));
      await tester.pumpAndSettle();
      final parent = tester.getRect(_dialogSurface);

      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pump();
      await tester.sendKeyEvent(LogicalKeyboardKey.enter);
      await tester.pumpAndSettle();
      expect(find.text('Child window'), findsOneWidget);
      expect(tester.getCenter(_dialogSurface.last), const Offset(400, 300));

      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pumpAndSettle();
      expect(find.text('Child window'), findsNothing);
      expect(tester.getRect(_dialogSurface), parent);

      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pumpAndSettle();
      expect(find.text('Parent window'), findsNothing);
      expect(launcherFocus.hasPrimaryFocus, isTrue);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('deletion uses theme error colors only in its final action', (
    tester,
  ) async {
    final colors = ColorScheme.fromSeed(seedColor: Colors.indigo);
    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData(colorScheme: colors),
        home: RevelationDialog(
          title: const Text('Delete bookmark'),
          content: const Text('Bookmark name'),
          secondaryActions: [
            RevelationDialogAction(label: 'Cancel', onPressed: () {}),
          ],
          primaryAction: RevelationDialogAction.destructive(
            label: 'Delete',
            onPressed: () {},
          ),
        ),
      ),
    );

    final primary = find.widgetWithText(FilledButton, 'Delete');
    final style = tester.widget<FilledButton>(primary).style!;
    expect(style.backgroundColor!.resolve({}), colors.error);
    expect(style.foregroundColor!.resolve({}), colors.onError);
    expect(style.shape!.resolve({}), isA<StadiumBorder>());
    expect(find.widgetWithText(TextButton, 'Cancel'), findsOneWidget);
  });
}

final _dialogSurface = find.descendant(
  of: find.byType(AlertDialog),
  matching: find.byWidgetPredicate(
    (widget) => widget is Material && widget.type == MaterialType.card,
  ),
);
