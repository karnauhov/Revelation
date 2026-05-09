import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/strongs_dictionary/presentation/screens/strongs_dictionary_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';
import 'smoke_test_harness.dart';

void main() {
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
}
