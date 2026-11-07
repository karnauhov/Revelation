import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/strongs_dictionary/presentation/screens/strongs_dictionary_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';
import 'smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Strong dictionary smoke: route renders real page', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/strongs_dictionary?number=G2',
      routes: <RouteBase>[
        GoRoute(
          path: '/strongs_dictionary',
          builder: (context, state) {
            final args = StrongDictionaryRouteArgs.tryParse(
              state.extra,
              state.uri.queryParameters,
            );
            return StrongsDictionaryScreen(
              initialStrongNumber:
                  args?.resolvedInitialStrongNumber ??
                  StrongDictionaryRouteArgs.defaultInitialStrongNumber,
            );
          },
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      MaterialApp.router(
        locale: const Locale('en'),
        routerConfig: router,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await pumpAndSettleSmoke(tester);

    final context = tester.element(find.byType(StrongsDictionaryScreen));
    final localizations = AppLocalizations.of(context)!;

    expect(find.byType(StrongsDictionaryScreen), findsOneWidget);
    expect(find.byType(PlannedFeatureScreen), findsNothing);
    expect(find.text(localizations.strongs_dictionary_screen), findsOneWidget);
    expect(
      find.byKey(const Key('strong_dictionary_search_field')),
      findsOneWidget,
    );
    expect(
      find.text(
        localizations.planned_feature_message(
          localizations.strongs_dictionary_screen,
        ),
      ),
      findsNothing,
    );
  });

  testWidgets('Greek keyboard semantics survives animated dictionary routes', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
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
          path: '/strongs_dictionary',
          pageBuilder: (context, state) => buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: const StrongsDictionaryScreen(initialStrongNumber: 2),
          ),
        ),
      ],
    );
    try {
      await tester.pumpWidget(
        MaterialApp.router(
          locale: const Locale('uk'),
          routerConfig: router,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
        ),
      );
      await pumpAndSettleSmoke(tester);
      expect(tester.binding.semanticsEnabled, isTrue);
      for (var cycle = 0; cycle < 3; cycle++) {
        router.push<void>('/strongs_dictionary');
        await _pumpAccessibleTransition(tester);
        expect(find.byType(StrongsDictionaryScreen), findsOneWidget);
        final button = find.byKey(const Key('greek_keyboard_button'));
        expect(button, findsOneWidget);
        await tester.tap(button);
        await pumpAndSettleSmoke(tester);
        final alpha = find.byKey(const Key('greek_keyboard_key_α'));
        // RenderObject.debugSemantics is intentionally absent in release mode.
        // The same scenario also runs in Web debug to inspect the node itself.
        if (kDebugMode) {
          expect(tester.getSemantics(alpha).getSemanticsData().label, 'α');
        }
        await tester.tap(alpha);
        await pumpAndSettleSmoke(tester);
        router.pop();
        await _pumpAccessibleTransition(tester);
        expect(find.text('Home'), findsOneWidget);
      }
      expect(tester.takeException(), isNull);
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      router.dispose();
      semantics.dispose();
    }
  });
}

Future<void> _pumpAccessibleTransition(WidgetTester tester) async {
  await tester.pump();
  for (var frame = 0; frame < 22; frame++) {
    await tester.pump(const Duration(milliseconds: 16));
    expect(tester.takeException(), isNull, reason: 'route frame $frame');
  }
  await pumpAndSettleSmoke(tester);
}
