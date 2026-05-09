@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_content.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_item.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    await GetIt.I.reset();
    DrawerContent.resetPlatformTestOverrides();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    DrawerContent.resetPlatformTestOverrides();
    await GetIt.I.reset();
  });

  setUp(() {
    addTearDown(_suppressOverflowErrors());
  });

  testWidgets('DrawerContent shows non-web actions including planned entries', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(480, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final app = _buildApp(onItemClicked: () {});
    await tester.pumpWidget(app);
    await tester.pumpAndSettle();

    await _openDrawer(tester);

    final context = tester.element(find.byType(DrawerContent));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.primary_sources_screen), findsOneWidget);
    for (final destination in _plannedFeatureDestinations(l10n)) {
      expect(find.text(destination.label), findsOneWidget);
      expect(
        find.byWidgetPredicate(
          (widget) =>
              widget is DrawerItem &&
              widget.text == destination.label &&
              widget.assetPath == destination.iconAssetPath,
        ),
        findsOneWidget,
      );
    }
    expect(find.text(l10n.settings_screen), findsOneWidget);
    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(find.text(l10n.close_app), findsOneWidget);
    expect(find.text(l10n.download), findsOneWidget);
  });

  testWidgets(
    'DrawerContent shows web download action, hides close action, and navigates',
    (tester) async {
      DrawerContent.isWebForTest = () => true;
      DrawerContent.isDesktopForTest = () => false;

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

      expect(find.text(l10n.download), findsOneWidget);
      expect(find.text(l10n.close_app), findsNothing);

      await tester.tap(find.text(l10n.download));
      await tester.pumpAndSettle();

      expect(clicks, 1);
      expect(find.text('download-page'), findsOneWidget);
    },
  );

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

  testWidgets('DrawerContent navigates to primary sources and about', (
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

    await tester.tap(find.text(l10n.primary_sources_screen));
    await tester.pumpAndSettle();
    expect(find.text('primary-sources-page'), findsOneWidget);

    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();
    await _openDrawer(tester);
    await tester.tap(find.text(l10n.about_screen));
    await tester.pumpAndSettle();
    expect(find.text('about-page'), findsOneWidget);
    expect(clicks, 2);
  });

  testWidgets('DrawerContent navigates to planned feature placeholder routes', (
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
    final destinations = _plannedFeatureDestinations(l10n);

    for (var i = 0; i < destinations.length; i += 1) {
      final destination = destinations[i];
      await _tapDrawerItem(tester, destination.label);

      expect(clicks, i + 1);
      expect(find.text(destination.pageText), findsOneWidget);

      if (i < destinations.length - 1) {
        await tester.binding.handlePopRoute();
        await tester.pumpAndSettle();
        await _openDrawer(tester);
      }
    }
  });

  testWidgets(
    'DrawerContent desktop close uses window channel when available',
    (tester) async {
      var clicks = 0;
      var systemPopCalls = 0;
      var closeWindowCalls = 0;

      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(const MethodChannel('revelation/window'), (
            methodCall,
          ) async {
            if (methodCall.method == 'closeWindow') {
              closeWindowCalls += 1;
            }
            return null;
          });
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(SystemChannels.platform, (
            methodCall,
          ) async {
            if (methodCall.method == 'SystemNavigator.pop') {
              systemPopCalls += 1;
            }
            return null;
          });
      addTearDown(() {
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
              const MethodChannel('revelation/window'),
              null,
            );
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
      expect(closeWindowCalls, 1);
      expect(systemPopCalls, 0);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );

  testWidgets(
    'DrawerContent desktop close falls back to SystemNavigator when channel fails',
    (tester) async {
      var clicks = 0;
      var systemPopCalls = 0;

      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(const MethodChannel('revelation/window'), (
            methodCall,
          ) async {
            throw PlatformException(code: 'channel-error');
          });
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(SystemChannels.platform, (
            methodCall,
          ) async {
            if (methodCall.method == 'SystemNavigator.pop') {
              systemPopCalls += 1;
            }
            return null;
          });
      addTearDown(() {
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
              const MethodChannel('revelation/window'),
              null,
            );
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
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );

  testWidgets(
    'DrawerContent custom drag handlers scroll the list and keep taps working',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(420, 220));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final app = _buildApp(onItemClicked: () {});
      await tester.pumpWidget(app);
      await tester.pumpAndSettle();
      await _openDrawer(tester);

      final context = tester.element(find.byType(DrawerContent));
      final l10n = AppLocalizations.of(context)!;

      final scrollableFinder = find.byType(Scrollable).first;
      final before = tester.state<ScrollableState>(scrollableFinder).position;
      expect(before.pixels, 0);

      final dragSurfaceFinder = find.byWidgetPredicate(
        (widget) =>
            widget is GestureDetector &&
            widget.onVerticalDragStart != null &&
            widget.onVerticalDragUpdate != null &&
            widget.onVerticalDragEnd != null,
      );
      expect(dragSurfaceFinder, findsOneWidget);

      final detector = tester.widget<GestureDetector>(dragSurfaceFinder);
      detector.onVerticalDragStart!(
        DragStartDetails(globalPosition: const Offset(0, 160)),
      );
      await tester.pump();

      detector.onVerticalDragUpdate!(
        DragUpdateDetails(globalPosition: const Offset(0, 40)),
      );
      await tester.pump();

      detector.onVerticalDragEnd!(DragEndDetails());
      await tester.pumpAndSettle();

      final after = tester.state<ScrollableState>(scrollableFinder).position;
      expect(after.pixels, greaterThan(0));

      await tester.tap(find.text(l10n.bible_screen));
      await tester.pumpAndSettle();

      expect(find.text('bible-page'), findsOneWidget);
    },
  );
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
        path: '/strongs_dictionary',
        builder: (context, state) =>
            const Scaffold(body: Text('strongs-dictionary-page')),
      ),
      GoRoute(
        path: '/allusion_search',
        builder: (context, state) =>
            const Scaffold(body: Text('allusion-search-page')),
      ),
      GoRoute(
        path: '/bible',
        builder: (context, state) => const Scaffold(body: Text('bible-page')),
      ),
      GoRoute(
        path: '/revelation_structure',
        builder: (context, state) =>
            const Scaffold(body: Text('revelation-structure-page')),
      ),
      GoRoute(
        path: '/historical_background',
        builder: (context, state) =>
            const Scaffold(body: Text('historical-background-page')),
      ),
      GoRoute(
        path: '/practical_faith',
        builder: (context, state) =>
            const Scaffold(body: Text('practical-faith-page')),
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

Future<void> _tapDrawerItem(WidgetTester tester, String label) async {
  await tester.scrollUntilVisible(
    find.text(label),
    80,
    scrollable: find.byType(Scrollable).first,
  );
  await tester.pumpAndSettle();
  await tester.tap(find.text(label));
  await tester.pumpAndSettle();
}

List<_PlannedFeatureDestination> _plannedFeatureDestinations(
  AppLocalizations l10n,
) {
  return <_PlannedFeatureDestination>[
    _PlannedFeatureDestination(
      label: l10n.strongs_dictionary_screen,
      pageText: 'strongs-dictionary-page',
      iconAssetPath: 'assets/images/UI/dictionary.svg',
    ),
    _PlannedFeatureDestination(
      label: l10n.allusion_search_screen,
      pageText: 'allusion-search-page',
      iconAssetPath: 'assets/images/UI/search_book.svg',
    ),
    _PlannedFeatureDestination(
      label: l10n.bible_screen,
      pageText: 'bible-page',
      iconAssetPath: 'assets/images/UI/bible.svg',
    ),
    _PlannedFeatureDestination(
      label: l10n.revelation_structure_screen,
      pageText: 'revelation-structure-page',
      iconAssetPath: 'assets/images/UI/structure.svg',
    ),
    _PlannedFeatureDestination(
      label: l10n.historical_background_screen,
      pageText: 'historical-background-page',
      iconAssetPath: 'assets/images/UI/history.svg',
    ),
    _PlannedFeatureDestination(
      label: l10n.practical_faith_screen,
      pageText: 'practical-faith-page',
      iconAssetPath: 'assets/images/UI/candle.svg',
    ),
  ];
}

class _PlannedFeatureDestination {
  const _PlannedFeatureDestination({
    required this.label,
    required this.pageText,
    required this.iconAssetPath,
  });

  final String label;
  final String pageText;
  final String iconAssetPath;
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
