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
    'full-size leaves keep their credits through zoom and restore them after tool hints',
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
      final nextPage = source.pages[1];
      await tester.tap(pageSelector);
      final nextLabel = find.text(
        '${nextPage.name} (${nextPage.content})',
        findRichText: true,
      );
      await waitFor(nextLabel);
      await tester.tap(nextLabel.last);
      await waitFor(viewer);
      expect(
        tester.widget<DropdownButton<model.Page>>(pageSelector).value?.name,
        nextPage.name,
      );
      verifyFrame();
      final scale = tester
          .widget<ImagePreview>(find.byType(ImagePreview))
          .controller
          .transformationController;
      final beforeZoom = scale.value.getMaxScaleOnAxis();
      await tool(l10n.zoom_in);
      expect(scale.value.getMaxScaleOnAxis(), greaterThan(beforeZoom));
      await tester.drag(viewer, const Offset(40, 20));
      await tester.pump();
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
      expect(tester.takeException(), isNull);
    },
  );
}
