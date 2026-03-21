@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_content.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
  setUp(() {
    addTearDown(_suppressOverflowErrors());
  });

  testWidgets('DrawerContent shows expected items on non-web platforms', (
    tester,
  ) async {
    final app = _buildApp(onItemClicked: () {});
    await tester.pumpWidget(app);
    await tester.pumpAndSettle();

    await _openDrawer(tester);

    final context = tester.element(find.byType(DrawerContent));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.primary_sources_screen), findsOneWidget);
    expect(find.text(l10n.settings_screen), findsOneWidget);
    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(find.text(l10n.close_app), findsOneWidget);
  });

  testWidgets('DrawerContent navigates to settings and invokes callback', (
    tester,
  ) async {
    var clicks = 0;
    final app = _buildApp(
      onItemClicked: () {
        clicks += 1;
      },
    );
    await tester.pumpWidget(app);
    await tester.pumpAndSettle();

    await _openDrawer(tester);

    final context = tester.element(find.byType(DrawerContent));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.text(l10n.settings_screen));
    await tester.pumpAndSettle();

    expect(clicks, 1);
    expect(find.text('settings-page'), findsOneWidget);
  });

  testWidgets('DrawerContent close button requests SystemNavigator.pop', (
    tester,
  ) async {
    var clicks = 0;
    var systemPopCalls = 0;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(SystemChannels.platform, (methodCall) async {
          if (methodCall.method == 'SystemNavigator.pop') {
            systemPopCalls += 1;
          }
          return null;
        });
    addTearDown(() {
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(SystemChannels.platform, null);
    });

    final app = _buildApp(
      onItemClicked: () {
        clicks += 1;
      },
    );
    await tester.pumpWidget(app);
    await tester.pumpAndSettle();

    await _openDrawer(tester);

    final context = tester.element(find.byType(DrawerContent));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.text(l10n.close_app));
    await tester.pumpAndSettle();

    expect(clicks, 1);
    expect(systemPopCalls, 1);
  });
}

Widget _buildApp({required VoidCallback onItemClicked}) {
  final router = GoRouter(
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (context, state) => Scaffold(
          drawer: Drawer(child: DrawerContent(onItemClicked: onItemClicked)),
          body: const Center(child: Text('home')),
        ),
      ),
      GoRoute(
        path: '/primary_sources',
        builder: (context, state) =>
            const Scaffold(body: Text('primary-sources-page')),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) =>
            const Scaffold(body: Text('settings-page')),
      ),
      GoRoute(
        path: '/about',
        builder: (context, state) => const Scaffold(body: Text('about-page')),
      ),
      GoRoute(
        path: '/download',
        builder: (context, state) =>
            const Scaffold(body: Text('download-page')),
      ),
    ],
  );

  return MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(
      textTheme: const TextTheme(bodyLarge: TextStyle(fontSize: 12)),
    ),
  );
}

Future<void> _openDrawer(WidgetTester tester) async {
  final scaffoldState = tester.state<ScaffoldState>(
    find.byType(Scaffold).first,
  );
  scaffoldState.openDrawer();
  await tester.pumpAndSettle();
}

VoidCallback _suppressOverflowErrors() {
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('A RenderFlex overflowed by')) {
      return;
    }
    if (originalHandler != null) {
      originalHandler(details);
    }
  };

  return () {
    FlutterError.onError = originalHandler;
  };
}
