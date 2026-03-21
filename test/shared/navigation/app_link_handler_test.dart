@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:url_launcher_platform_interface/link.dart';
import 'package:url_launcher_platform_interface/url_launcher_platform_interface.dart';

import '../../test_harness/widget_test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late UrlLauncherPlatform originalUrlLauncherPlatform;
  late _FakeUrlLauncherPlatform fakeUrlLauncherPlatform;

  setUpAll(() {
    originalUrlLauncherPlatform = UrlLauncherPlatform.instance;
    fakeUrlLauncherPlatform = _FakeUrlLauncherPlatform();
    UrlLauncherPlatform.instance = fakeUrlLauncherPlatform;
  });

  tearDownAll(() async {
    UrlLauncherPlatform.instance = originalUrlLauncherPlatform;
    await GetIt.I.reset();
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    fakeUrlLauncherPlatform.clear();
    setDefaultGreekStrongTapHandler(null);
    setDefaultGreekStrongPickerTapHandler(null);
    setDefaultWordTapHandler(null);
  });

  tearDown(() async {
    setDefaultGreekStrongTapHandler(null);
    setDefaultGreekStrongPickerTapHandler(null);
    setDefaultWordTapHandler(null);
    await GetIt.I.reset();
  });

  group('base validation and fallback', () {
    testWidgets('returns false for null, empty and whitespace href', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      expect(await handleAppLink(context, null), isFalse);
      expect(await handleAppLink(context, ''), isFalse);
      expect(await handleAppLink(context, '   '), isFalse);
    });

    testWidgets('unknown scheme delegates to launchLink', (tester) async {
      final context = await pumpContext(tester);

      final handled = await handleAppLink(context, 'https://example.com/path');

      expect(handled, isTrue);
      expect(
        fakeUrlLauncherPlatform.launchedUrls,
        contains('https://example.com/path'),
      );
    });
  });

  group('screen and topic links', () {
    testWidgets('screen link pushes route and normalizes missing slash', (
      tester,
    ) async {
      final fixture = await _pumpRouterFixture(tester);

      final handled = await handleAppLink(
        fixture.contexts['home']!,
        'screen:settings',
      );
      await tester.pumpAndSettle();

      expect(handled, isTrue);
      expect(find.text('settings-screen'), findsOneWidget);
    });

    testWidgets('screen link accepts leading slash', (tester) async {
      final fixture = await _pumpRouterFixture(tester);

      final handled = await handleAppLink(
        fixture.contexts['home']!,
        'screen:/about',
      );
      await tester.pumpAndSettle();

      expect(handled, isTrue);
      expect(find.text('about-screen'), findsOneWidget);
    });

    testWidgets('screen link returns false for empty route', (tester) async {
      final fixture = await _pumpRouterFixture(tester);

      final handled = await handleAppLink(fixture.contexts['home']!, 'screen:');

      expect(handled, isFalse);
    });

    testWidgets('topic link pushes /topic with file query parameter', (
      tester,
    ) async {
      final fixture = await _pumpRouterFixture(tester);

      final handled = await handleAppLink(
        fixture.contexts['home']!,
        'topic:chapter_1.md',
      );
      await tester.pumpAndSettle();

      expect(handled, isTrue);
      expect(find.text('topic:chapter_1.md'), findsOneWidget);
    });

    testWidgets('topic link returns false for empty route payload', (
      tester,
    ) async {
      final fixture = await _pumpRouterFixture(tester);

      final handled = await handleAppLink(fixture.contexts['home']!, 'topic:');

      expect(handled, isFalse);
    });
  });

  group('strong links', () {
    testWidgets('greek strong link uses explicit callback', (tester) async {
      final context = await pumpContext(tester);
      int? capturedStrongNumber;

      final handled = await handleAppLink(
        context,
        'strong:G321',
        onGreekStrongTap: (strongNumber, _) {
          capturedStrongNumber = strongNumber;
        },
      );

      expect(handled, isTrue);
      expect(capturedStrongNumber, 321);
    });

    testWidgets('greek strong link falls back to default callback', (
      tester,
    ) async {
      final context = await pumpContext(tester);
      int? capturedStrongNumber;
      setDefaultGreekStrongTapHandler((strongNumber, _) {
        capturedStrongNumber = strongNumber;
      });

      final handled = await handleAppLink(context, 'strong:g12');

      expect(handled, isTrue);
      expect(capturedStrongNumber, 12);
    });

    testWidgets('greek strong link returns false when callback is missing', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      final handled = await handleAppLink(context, 'strong:G7');

      expect(handled, isFalse);
    });

    testWidgets('hebrew strong link launches external bible hub url', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      final handled = await handleAppLink(context, 'strong:H7225');

      expect(handled, isTrue);
      expect(
        fakeUrlLauncherPlatform.launchedUrls,
        contains('https://biblehub.com/hebrew/7225.htm'),
      );
    });

    testWidgets('strong link rejects malformed or unknown numbers', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      expect(await handleAppLink(context, 'strong:H'), isFalse);
      expect(await handleAppLink(context, 'strong:Gx'), isFalse);
      expect(await handleAppLink(context, 'strong:Z10'), isFalse);
      expect(await handleAppLink(context, 'strong:'), isFalse);
    });
  });

  group('strong picker links', () {
    testWidgets('picker link uses explicit callback when provided', (
      tester,
    ) async {
      final context = await pumpContext(tester);
      int? capturedStrongNumber;

      final handled = await handleAppLink(
        context,
        'strong_picker:G44',
        onGreekStrongPickerTap: (strongNumber, _) {
          capturedStrongNumber = strongNumber;
        },
      );

      expect(handled, isTrue);
      expect(capturedStrongNumber, 44);
    });

    testWidgets('picker link falls back to default picker handler', (
      tester,
    ) async {
      final context = await pumpContext(tester);
      int? capturedStrongNumber;
      setDefaultGreekStrongPickerTapHandler((strongNumber, _) {
        capturedStrongNumber = strongNumber;
      });

      final handled = await handleAppLink(context, 'strong_picker:g77');

      expect(handled, isTrue);
      expect(capturedStrongNumber, 77);
    });

    testWidgets('picker link falls back to default strong handler', (
      tester,
    ) async {
      final context = await pumpContext(tester);
      int? capturedStrongNumber;
      setDefaultGreekStrongTapHandler((strongNumber, _) {
        capturedStrongNumber = strongNumber;
      });

      final handled = await handleAppLink(context, 'strong_picker:G88');

      expect(handled, isTrue);
      expect(capturedStrongNumber, 88);
    });

    testWidgets('picker link returns false on invalid format or callback', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      expect(await handleAppLink(context, 'strong_picker:H1'), isFalse);
      expect(await handleAppLink(context, 'strong_picker:Gx'), isFalse);
      expect(await handleAppLink(context, 'strong_picker:'), isFalse);
      expect(await handleAppLink(context, 'strong_picker:G1'), isFalse);
    });
  });

  group('word links', () {
    testWidgets('word link uses explicit onWordTap callback', (tester) async {
      final context = await pumpContext(tester);
      String? capturedSourceId;
      String? capturedPageName;
      int? capturedWordIndex;

      final handled = await handleAppLink(
        context,
        'word:source-a:page-a:3',
        onWordTap: (sourceId, pageName, wordIndex, _) {
          capturedSourceId = sourceId;
          capturedPageName = pageName;
          capturedWordIndex = wordIndex;
        },
      );

      expect(handled, isTrue);
      expect(capturedSourceId, 'source-a');
      expect(capturedPageName, 'page-a');
      expect(capturedWordIndex, 3);
    });

    testWidgets('word link falls back to default callback', (tester) async {
      final context = await pumpContext(tester);
      String? capturedSourceId;
      String? capturedPageName;
      int? capturedWordIndex;

      setDefaultWordTapHandler((sourceId, pageName, wordIndex, _) {
        capturedSourceId = sourceId;
        capturedPageName = pageName;
        capturedWordIndex = wordIndex;
      });

      final handled = await handleAppLink(context, 'word:source-b:page-b:1');

      expect(handled, isTrue);
      expect(capturedSourceId, 'source-b');
      expect(capturedPageName, 'page-b');
      expect(capturedWordIndex, 1);
    });

    testWidgets('word link supports only source id without page/index', (
      tester,
    ) async {
      final context = await pumpContext(tester);
      String? capturedSourceId;
      String? capturedPageName;
      int? capturedWordIndex;

      setDefaultWordTapHandler((sourceId, pageName, wordIndex, _) {
        capturedSourceId = sourceId;
        capturedPageName = pageName;
        capturedWordIndex = wordIndex;
      });

      final handled = await handleAppLink(context, 'word:source-only');

      expect(handled, isTrue);
      expect(capturedSourceId, 'source-only');
      expect(capturedPageName, isNull);
      expect(capturedWordIndex, isNull);
    });

    testWidgets('word link pops current route before default callback', (
      tester,
    ) async {
      late BuildContext rootContext;
      late BuildContext childContext;
      var callbackCalls = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              rootContext = context;
              return const Text('root');
            },
          ),
        ),
      );
      await tester.pump();

      unawaited(
        Navigator.of(rootContext).push<void>(
          MaterialPageRoute<void>(
            builder: (context) {
              childContext = context;
              return const Text('child');
            },
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('child'), findsOneWidget);

      setDefaultWordTapHandler((_, __, ___, ____) {
        callbackCalls++;
      });

      final handled = await handleAppLink(
        childContext,
        'word:source',
        popBeforeScreenPush: true,
      );
      await tester.pumpAndSettle();

      expect(handled, isTrue);
      expect(callbackCalls, 1);
      expect(find.text('root'), findsOneWidget);
      expect(find.text('child'), findsNothing);
    });

    testWidgets('word link rejects malformed payloads and invalid indexes', (
      tester,
    ) async {
      final context = await pumpContext(tester);

      expect(await handleAppLink(context, 'word'), isTrue);
      expect(fakeUrlLauncherPlatform.launchedUrls, contains('word'));
      expect(await handleAppLink(context, 'word:a:b:c:d'), isFalse);
      expect(await handleAppLink(context, 'word:   :page:1'), isFalse);
      expect(await handleAppLink(context, 'word:source:   :1'), isFalse);
      expect(await handleAppLink(context, 'word:source:page:-1'), isFalse);
      expect(await handleAppLink(context, 'word:source:page:abc'), isFalse);
      expect(await handleAppLink(context, 'word:source:page:1'), isFalse);
    });
  });

  group('bible links', () {
    testWidgets('bible link uses locale-aware translation and verse', (
      tester,
    ) async {
      final context = await pumpLocalizedContext(
        tester,
        locale: const Locale('uk'),
      );

      final handled = await handleAppLink(context, 'bible:Rev22:3');

      expect(handled, isTrue);
      expect(
        fakeUrlLauncherPlatform.launchedUrls.last,
        'https://on-bible.com/bible?b=ubo&bk=Rev&ch=22&v=3',
      );
    });

    testWidgets(
      'bible link falls back to english translation for unknown locale',
      (tester) async {
        final context = await pumpLocalizedContext(
          tester,
          locale: const Locale('de'),
        );

        final handled = await handleAppLink(context, 'bible:John3');

        expect(handled, isTrue);
        expect(
          fakeUrlLauncherPlatform.launchedUrls.last,
          'https://on-bible.com/bible?b=kjv&bk=John&ch=3',
        );
      },
    );

    testWidgets('bible link rejects malformed payload', (tester) async {
      final context = await pumpContext(tester);

      expect(await handleAppLink(context, 'bible:'), isFalse);
    });
  });
}

Future<_RouterFixture> _pumpRouterFixture(WidgetTester tester) async {
  final contexts = <String, BuildContext>{};
  final router = GoRouter(
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (context, state) {
          contexts['home'] = context;
          return const Scaffold(body: Text('home-screen'));
        },
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) {
          contexts['settings'] = context;
          return const Scaffold(body: Text('settings-screen'));
        },
      ),
      GoRoute(
        path: '/about',
        builder: (context, state) {
          contexts['about'] = context;
          return const Scaffold(body: Text('about-screen'));
        },
      ),
      GoRoute(
        path: '/topic',
        builder: (context, state) {
          contexts['topic'] = context;
          final file = state.uri.queryParameters['file'] ?? '';
          return Scaffold(body: Text('topic:$file'));
        },
      ),
    ],
  );

  await tester.pumpWidget(
    MaterialApp.router(
      routerConfig: router,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
    ),
  );
  await tester.pumpAndSettle();

  return _RouterFixture(contexts: contexts);
}

class _RouterFixture {
  const _RouterFixture({required this.contexts});

  final Map<String, BuildContext> contexts;
}

class _FakeUrlLauncherPlatform extends UrlLauncherPlatform {
  @override
  LinkDelegate? get linkDelegate => null;

  final List<String> launchedUrls = <String>[];
  bool nextResult = true;

  @override
  Future<bool> canLaunch(String url) async => true;

  @override
  Future<void> closeWebView() async {}

  @override
  Future<bool> launch(
    String url, {
    required bool useSafariVC,
    required bool useWebView,
    required bool enableJavaScript,
    required bool enableDomStorage,
    required bool universalLinksOnly,
    required Map<String, String> headers,
    String? webOnlyWindowName,
  }) async {
    launchedUrls.add(url);
    return nextResult;
  }

  void clear() {
    launchedUrls.clear();
    nextResult = true;
  }
}
