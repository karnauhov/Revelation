import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_attributes_footer.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/source_item.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/main.dart' as app;
import 'package:revelation/shared/models/page.dart' as model;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

import 'smoke/smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets(
    'manuscript leaves restore their own zoom and pan and keep their credits through tool use',
    (tester) async {
      final dispatcher = tester.binding.platformDispatcher;
      dispatcher.defaultRouteNameTestValue = '/primary_sources';
      addTearDown(dispatcher.clearDefaultRouteNameTestValue);
      await GetIt.I.reset();
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      AppDi.registerCore(talker: talker);
      SharedPreferences.setMockInitialValues({});
      final settings = SettingsCubit(SettingsRepository());
      await settings.loadSettings();
      await settings.changeLanguage('ru');
      await settings.setSoundEnabled(false);
      addTearDown(() async {
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
        await DBManager().close();
        await GetIt.I.reset();
      });
      await tester.runAsync(() => DbManagerDatabaseRuntime().initialize('ru'));
      await app.startApp(
        talker,
        initializeSettingsCubit: (_) async => settings,
      );
      Future<void> waitFor(Finder finder) async {
        await pumpUntilSmoke(
          tester,
          isReady: () => finder.evaluate().isNotEmpty,
          reason: finder.describeMatch(Plurality.zero),
          timeout: const Duration(seconds: 40),
        );
        await tester.pump(const Duration(milliseconds: 350));
      }

      await tester.pump();
      AppRouter().router.go('/primary_sources');
      final card = find.byWidgetPredicate(
        (w) => w is SourceItemWidget && w.source.id == 'U001',
      );
      await waitFor(card);
      final source = tester.widget<SourceItemWidget>(card).source;
      final credit = source.credits.first.text;
      expect(
        find.descendant(
          of: card,
          matching: find.byType(PrimarySourceAttributesFooter),
        ),
        findsNothing,
      );
      expect(
        find.descendant(
          of: card,
          matching: find.textContaining(credit, findRichText: true),
        ),
        findsNothing,
      );
      final thumb = find.descendant(
        of: card,
        matching: find.byType(ElevatedButton),
      );
      await tester.ensureVisible(thumb);
      await tester.tap(thumb);
      final viewer = find.byType(InteractiveViewer);
      await waitFor(viewer);
      final l10n = AppLocalizations.of(tester.element(viewer))!;
      final frame = find.byType(PrimarySourceAttributesFooter);
      void verifyFrame() {
        expect(
          find.descendant(
            of: frame,
            matching: find.textContaining(credit, findRichText: true),
          ),
          findsOneWidget,
        );
        expect(
          tester.getRect(frame).top,
          closeTo(tester.getRect(viewer).bottom, 2),
        );
      }

      Future<void> tool(String label) async {
        final shortcut = find.byTooltip(label);
        if (shortcut.evaluate().isNotEmpty) {
          await tester.tap(shortcut);
        } else {
          await tester.tap(find.byTooltip(l10n.menu));
          await waitFor(find.text(label));
          await tester.ensureVisible(find.text(label));
          await tester.tap(find.text(label));
        }
        await tester.pump(const Duration(milliseconds: 400));
      }

      verifyFrame();
      final pageSelector = find.byType(DropdownButton<model.Page>);
      Future<void> selectLeaf(model.Page page) async {
        await tester.pumpAndSettle();
        await tester.tap(pageSelector);
        await tester.pumpAndSettle();
        final label = find.text(
          '${page.name} (${page.content})',
          findRichText: true,
        );
        if (label.evaluate().isEmpty) {
          final list = find.byType(ListView).last;
          final scrollable = find.descendant(
            of: list,
            matching: find.byType(Scrollable),
          );
          final current = tester
              .widget<DropdownButton<model.Page>>(pageSelector)
              .value!;
          final delta =
              source.pages.indexOf(page) < source.pages.indexOf(current)
              ? -90.0
              : 90.0;
          await tester.scrollUntilVisible(label, delta, scrollable: scrollable);
        }
        expect(label, findsWidgets, reason: 'open page option ${page.name}');
        await tester.ensureVisible(label.last);
        await tester.tap(label.last);
        await pumpUntilSmoke(
          tester,
          isReady: () {
            final previews = tester.widgetList<ImagePreview>(
              find.byType(ImagePreview),
            );
            return previews.length == 1 &&
                viewer.evaluate().isNotEmpty &&
                previews.single.imageName.endsWith('_${page.image}');
          },
          reason: 'first usable frame of ${page.name}',
          timeout: const Duration(seconds: 40),
        );
        expect(
          tester.widget<DropdownButton<model.Page>>(pageSelector).value?.name,
          page.name,
        );
        final base = tester.widget<RawImage>(
          find.descendant(of: viewer, matching: find.byType(RawImage)).first,
        );
        expect(
          base.image,
          isNotNull,
          reason:
              'the first readable frame must paint the leaf under its annotations',
        );
      }

      Matrix4 currentView() => tester
          .widget<InteractiveViewer>(viewer)
          .transformationController!
          .value
          .clone();
      void expectView(Matrix4 saved) {
        final current = currentView();
        for (final i in [0, 5, 12, 13]) {
          expect(
            current.storage[i],
            closeTo(saved.storage[i], 0.001),
            reason: 'saved scale or offset at matrix index $i',
          );
        }
      }

      Future<void> pan(Offset delta) async {
        final gesture = await tester.startGesture(tester.getCenter(viewer));
        await gesture.moveBy(delta / 2);
        await tester.pump(const Duration(milliseconds: 100));
        await gesture.moveBy(delta / 2);
        await tester.pump(const Duration(milliseconds: 180));
        await gesture.up();
        await tester.pump();
      }

      final firstPage = source.pages.first;
      final nextPage = source.pages[1];
      final initial = currentView();
      await tool(l10n.zoom_in);
      await pan(const Offset(-45, -25));
      await tester.pump();
      final firstView = currentView();
      expect(firstView.storage[0], greaterThan(initial.storage[0]));
      expect(firstView.storage[12], isNot(closeTo(initial.storage[12], 0.001)));
      await selectLeaf(nextPage);
      verifyFrame();
      final beforeZoom = currentView().storage[0];
      await tool(l10n.zoom_in);
      await tool(l10n.zoom_in);
      await pan(const Offset(-85, -50));
      await tester.pump();
      final secondView = currentView();
      expect(secondView.storage[0], greaterThan(beforeZoom));
      expect(
        secondView.storage[12],
        isNot(closeTo(firstView.storage[12], 0.001)),
      );
      await selectLeaf(firstPage);
      expectView(firstView);
      await selectLeaf(nextPage);
      expectView(secondView);
      await tester.pump(const Duration(milliseconds: 1100));
      expectView(secondView);
      verifyFrame();

      await tool(l10n.brightness_contrast);
      await waitFor(find.byType(Slider));
      await tester.tap(find.byType(Slider).first);
      await tester.tap(find.text(l10n.reset));
      await tester.pump(const Duration(milliseconds: 400));
      await tool(l10n.color_replacement);
      await waitFor(find.byTooltip(l10n.eyedropper));
      await tester.tap(find.byTooltip(l10n.eyedropper).first);
      await waitFor(find.text(l10n.pick_color_description));
      expect(find.textContaining(credit, findRichText: true), findsNothing);
      await tester.tapAt(tester.getCenter(viewer));
      await waitFor(find.byTooltip(l10n.area_selection));
      await tester.tap(find.byTooltip(l10n.area_selection));
      await waitFor(find.text(l10n.select_area_description));
      expect(find.textContaining(credit, findRichText: true), findsNothing);
      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await waitFor(find.text(l10n.reset));
      await tester.tap(find.text(l10n.reset));
      await tester.pump(const Duration(milliseconds: 400));
      verifyFrame();

      await selectLeaf(firstPage);
      expectView(firstView);
      await pan(const Offset(-42, -24));
      final beforeExit = currentView();
      AppRouter().router.go('/primary_sources');
      await waitFor(card);
      await tester.ensureVisible(thumb);
      await tester.tap(thumb);
      await pumpUntilSmoke(
        tester,
        isReady: () => viewer.evaluate().isNotEmpty,
        reason: 'reopened source',
        timeout: const Duration(seconds: 40),
      );
      expectView(beforeExit);
      expect(tester.takeException(), isNull);
    },
  );
}
