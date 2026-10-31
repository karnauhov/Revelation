import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';

/// Shared UI regression, also run against installed SQLite modules locally.
Future<void> exerciseBibleStrongAvailability(
  WidgetTester tester,
  BibleRepository repository,
  double width,
) async {
  await tester.binding.setSurfaceSize(Size(width, 900));
  addTearDown(() => tester.binding.setSurfaceSize(null));
  await tester.pumpWidget(
    MaterialApp(
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: BibleScreen(initialBookId: 1, bibleRepository: repository),
    ),
  );
  final primaryPane = find.byKey(const Key('bible_reader_pane_primary'));
  await _waitFor(
    tester,
    () => find.byKey(const Key('bible_verse_1')).evaluate().isNotEmpty,
  );
  final workspace = tester.element(primaryPane).read<BibleWorkspaceCubit>();
  final reader = workspace.readerCubitFor('primary');
  expect(workspace.state.paneIds, ['primary']);
  expect(reader.state.selectedModule!.hasStrongNumbers, isTrue);

  Future<void> select(BibleReaderCubit cubit, String file) async {
    await tester.runAsync(
      () => cubit.selectModule(
        cubit.state.modules.firstWhere((m) => m.fileName == file),
      ),
    );
    await tester.pumpAndSettle();
    expect(cubit.state.status, BibleReaderStatus.ready);
  }

  Future<void> checkControl(
    Finder pane,
    bool available, {
    bool tap = false,
  }) async {
    final inline = find.descendant(
      of: pane,
      matching: find.byKey(const Key('bible_strong_toggle_button')),
    );
    final overflow = find.descendant(
      of: pane,
      matching: find.byIcon(Icons.more_vert),
    );
    if (inline.evaluate().isNotEmpty) {
      expect(available, isTrue);
      if (tap) await tester.tap(inline);
    } else {
      if (!available && overflow.evaluate().isEmpty) {
        return;
      }
      expect(overflow, findsOneWidget);
      await tester.tap(overflow);
      await tester.pumpAndSettle();
      final action = find.byKey(const Key('bible_toolbar_menu_strong_numbers'));
      expect(action, available ? findsOneWidget : findsNothing);
      if (tap) {
        await tester.tap(action);
      } else {
        Navigator.of(tester.element(pane)).pop();
      }
    }
    await tester.pumpAndSettle();
  }

  await checkControl(primaryPane, true, tap: true);
  expect(reader.state.showStrongNumbers, isFalse);
  await select(reader, 'bible_ohienko_1988.sqlite');
  expect(reader.state.selectedModule!.hasStrongNumbers, isFalse);
  await checkControl(primaryPane, false);
  expect(
    find.descendant(
      of: primaryPane,
      matching: find.byKey(const Key('bible_verse_1')),
    ),
    findsOneWidget,
  );

  await select(reader, 'bible_kjv.sqlite');
  await checkControl(primaryPane, true);
  expect(reader.state.showStrongNumbers, isFalse);
  await checkControl(primaryPane, true, tap: true);
  expect(reader.state.showStrongNumbers, isTrue);

  // An unannotated pane must not affect the independent original pane.
  await select(reader, 'bible_ohienko_1988.sqlite');
  workspace.openParallelReader();
  await _waitFor(
    tester,
    () =>
        workspace.state.paneIds.length == 2 &&
        workspace.readerCubitFor(workspace.state.paneIds.last).state.status ==
            BibleReaderStatus.ready,
  );
  final secondaryId = workspace.state.paneIds.last;
  final secondary = workspace.readerCubitFor(secondaryId);
  await select(secondary, 'bible_lxx_tr.sqlite');
  final secondaryPane = find.byKey(Key('bible_reader_pane_$secondaryId'));
  await checkControl(primaryPane, false);
  await checkControl(secondaryPane, true, tap: true);
  expect(secondary.state.showStrongNumbers, isFalse);
  expect(reader.state.showStrongNumbers, isTrue);
  expect(tester.takeException(), isNull);
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpAndSettle();
}

Future<void> _waitFor(WidgetTester tester, bool Function() ready) async {
  for (var i = 0; i < 200 && !ready(); i++) {
    await tester.pump(const Duration(milliseconds: 50));
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 20)),
    );
  }
  expect(ready(), isTrue);
  await tester.pumpAndSettle();
}
