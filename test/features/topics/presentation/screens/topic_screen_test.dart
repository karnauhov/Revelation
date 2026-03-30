@Tags(['widget'])
import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/application/orchestrators/topic_markdown_image_orchestrator.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/features/topics/presentation/screens/topic_screen.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../../../test_harness/fakes/fake_settings_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Map<String, Uint8List> assetBytes = <String, Uint8List>{};
  Map<String, Uint8List> savedDownloads = <String, Uint8List>{};

  setUpAll(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (message) async {
          if (message == null) {
            return null;
          }
          final key = utf8.decode(message.buffer.asUint8List());
          final data = assetBytes[key];
          if (data == null) {
            return null;
          }
          return ByteData.sublistView(data);
        });
  });

  tearDownAll(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', null);
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );

    savedDownloads = <String, Uint8List>{};
    TopicScreen.resetTestOverrides();
    TopicScreen.saveDownloadableFileForTest =
        ({
          required Uint8List bytes,
          required String fileName,
          required String mimeType,
        }) async {
          savedDownloads[fileName] = Uint8List.fromList(bytes);
          return 'saved/$fileName';
        };

    debugDefaultTargetPlatformOverride = null;

    assetBytes = _withManifest(<String, Uint8List>{
      ..._dialogAssets,
      'assets/test/icon.png': _png1x1,
      'assets/test/readme.txt': _bytes('readme'),
      'assets/test/doc.md': _bytes('# doc'),
      'assets/test/image.jpg': _png1x1,
      'assets/test/image.jpeg': _png1x1,
      'assets/test/image.gif': _png1x1,
      'assets/test/image.svg': _bytes(_svg),
      'assets/test/book.pdf': _bytes('%PDF-1.7'),
      'assets/test/archive.zip': _bytes('PK'),
      'assets/test/data.bin': _bytes('binary'),
    });
  });

  tearDown(() async {
    debugDefaultTargetPlatformOverride = null;
    TopicScreen.resetTestOverrides();
    await GetIt.I.reset();
  });

  testWidgets('TopicScreen shows error when language is empty', (tester) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      language: '',
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(MarkdownBody), findsNothing);
  });

  testWidgets('TopicScreen renders markdown when route is empty', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      language: 'en',
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    expect(find.byType(ErrorMessage), findsNothing);
    expect(find.byType(MarkdownBody), findsOneWidget);
  });

  testWidgets('TopicScreen prefers explicit widget title and subtitle', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(
        name: 'Provided title',
        description: 'Provided subtitle',
        topicContentCubitBuilder: _topicCubitBuilder(repo),
      ),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    expect(find.text('Provided title'), findsOneWidget);
    expect(find.text('Provided subtitle'), findsOneWidget);
  });

  testWidgets(
    'TopicScreen resolves title/subtitle from repository metadata when missing',
    (tester) async {
      final repo = _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'intro|en': const AppSuccess<String>('Repository markdown'),
        },
        topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
          'intro|en': AppSuccess<TopicInfo?>(
            TopicInfo(
              name: 'Repository title',
              idIcon: '',
              description: 'Repository subtitle',
              route: 'intro',
            ),
          ),
        },
      );
      final harness = await _buildHarness(
        child: TopicScreen(
          file: 'intro',
          topicContentCubitBuilder: _topicCubitBuilder(repo),
        ),
      );
      addTearDown(harness.dispose);

      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      expect(find.text('Repository title'), findsOneWidget);
      expect(find.text('Repository subtitle'), findsOneWidget);
      expect(find.byType(MarkdownBody), findsOneWidget);
    },
  );

  testWidgets('TopicScreen falls back to localized title when metadata empty', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository(
      markdownByRouteLanguage: <String, AppResult<String>>{
        'intro|en': const AppSuccess<String>('Fallback markdown'),
      },
      topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
        'intro|en': AppSuccess<TopicInfo?>(
          TopicInfo(
            name: '   ',
            idIcon: '',
            description: '   ',
            route: 'intro',
          ),
        ),
      },
    );
    final harness = await _buildHarness(
      child: TopicScreen(
        file: 'intro',
        name: '   ',
        description: '   ',
        topicContentCubitBuilder: _topicCubitBuilder(repo),
      ),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(TopicScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text(l10n.topic), findsOneWidget);
  });

  testWidgets('TopicScreen delegates markdown screen links to app router', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'screen:settings');

    expect(find.text('settings-page'), findsOneWidget);
  });

  testWidgets('TopicScreen delegates markdown topic links to app router', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'topic:intro_file');

    expect(find.text('topic-page:intro_file'), findsOneWidget);
  });

  testWidgets('TopicScreen ignores empty markdown link', (tester) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, '   ');

    expect(find.byType(TopicScreen), findsOneWidget);
    expect(find.text('settings-page'), findsNothing);
  });

  testWidgets('TopicScreen downloads DB file from dbfile link', (tester) async {
    final resource = TopicResource(
      fileName: 'manual.pdf',
      mimeType: 'application/pdf',
      data: _bytes('db-file'),
    );
    final repo = _FakeTopicsRepository(
      resourceByKey: <String, AppResult<TopicResource?>>{
        'manual': AppSuccess<TopicResource?>(resource),
      },
    );
    final harness = await _buildHarness(
      includeDialogHost: false,
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'dbfile:manual', settle: false);
    expect(savedDownloads['manual.pdf'], orderedEquals(_bytes('db-file')));
  });

  testWidgets('TopicScreen shows error dialog for missing DB file resource', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'dbfile:missing');

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.textContaining('Resource not found in DB: missing'),
      findsOneWidget,
    );
    await _closeDialog(tester);
  });

  testWidgets('TopicScreen validates empty DB file key and empty asset path', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'dbfile:   ');
    expect(find.textContaining('DB file key is empty'), findsOneWidget);
    await _closeDialog(tester);

    await _invokeMarkdownLink(tester, 'resource:   ');
    expect(find.textContaining('Asset path is empty'), findsOneWidget);
    await _closeDialog(tester);
  });

  testWidgets('TopicScreen downloads assets and covers mime type mapping', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      includeDialogHost: false,
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final assetPaths = <String>[
      'assets/test/icon.png',
      'assets/test/image.jpg',
      'assets/test/image.jpeg',
      'assets/test/image.gif',
      'assets/test/image.svg',
      'assets/test/book.pdf',
      'assets/test/archive.zip',
      'assets/test/readme.txt',
      'assets/test/doc.md',
      'assets/test/data.bin',
    ];

    for (final assetPath in assetPaths) {
      await _invokeMarkdownLink(tester, 'resource:$assetPath', settle: false);
      final expectedName = p.basename(assetPath);
      expect(
        savedDownloads[expectedName],
        orderedEquals(assetBytes[assetPath]!),
        reason: 'Missing downloaded file: $expectedName',
      );
    }
  });

  testWidgets('TopicScreen shows dialog when asset download fails', (
    tester,
  ) async {
    final repo = _FakeTopicsRepository();
    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'resource:assets/test/missing.bin');

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.textContaining('Asset not found: assets/test/missing.bin'),
      findsOneWidget,
    );
    await _closeDialog(tester);
  });

  testWidgets('TopicScreen shows error when file save throws', (tester) async {
    final resource = TopicResource(
      fileName: 'manual.pdf',
      mimeType: 'application/pdf',
      data: _bytes('db-file'),
    );
    final repo = _FakeTopicsRepository(
      resourceByKey: <String, AppResult<TopicResource?>>{
        'manual': AppSuccess<TopicResource?>(resource),
      },
    );
    TopicScreen.saveDownloadableFileForTest =
        ({
          required Uint8List bytes,
          required String fileName,
          required String mimeType,
        }) async => throw PlatformException(code: 'downloads-missing');

    final harness = await _buildHarness(
      child: TopicScreen(topicContentCubitBuilder: _topicCubitBuilder(repo)),
    );
    addTearDown(harness.dispose);

    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    await _invokeMarkdownLink(tester, 'dbfile:manual');

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.textContaining('Unable to download file: manual.pdf'),
      findsOneWidget,
    );
    await _closeDialog(tester);
  });

  testWidgets(
    'TopicScreen markdown images resolve db/resource/network branches',
    (tester) async {
      final repo = _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'images|en': const AppSuccess<String>(
            '![DB image](dbres:icon)\n'
            '![Missing alt](dbres:missing)\n'
            '![](dbres:missing_without_alt)\n'
            '![Asset image](resource:assets/test/icon.png)\n'
            '![Network alt](https://example.invalid/missing.png)',
          ),
        },
        topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
          'images|en': AppSuccess<TopicInfo?>(
            TopicInfo(
              name: 'Images',
              idIcon: '',
              description: 'Image rendering',
              route: 'images',
            ),
          ),
        },
      );
      final imageOrchestrator = _FakeTopicMarkdownImageOrchestrator(
        imageResultsByCacheKey: <String, TopicMarkdownImageLoadResult>{
          _cacheKeyForSource(
            'dbres:icon',
          ): TopicMarkdownImageLoadResult.success(
            bytes: _png1x1,
            mimeType: 'image/png',
          ),
          _cacheKeyForSource('dbres:missing'):
              const TopicMarkdownImageLoadResult.failure(),
          _cacheKeyForSource('dbres:missing_without_alt'):
              const TopicMarkdownImageLoadResult.failure(),
          _cacheKeyForSource(
            'https://example.invalid/missing.png',
          ): TopicMarkdownImageLoadResult.success(
            bytes: _png1x1,
            mimeType: 'image/png',
          ),
        },
      );
      final harness = await _buildHarness(
        includeDialogHost: false,
        child: TopicScreen(
          file: 'images',
          topicContentCubitBuilder: _topicCubitBuilder(
            repo,
            topicMarkdownImageOrchestrator: imageOrchestrator,
          ),
        ),
      );
      addTearDown(harness.dispose);

      await tester.pumpWidget(harness.app);
      await tester.pump();
      await tester.pump();

      expect(
        find.byWidgetPredicate(
          (widget) => widget is Image && widget.image is MemoryImage,
        ),
        findsAtLeastNWidgets(2),
      );
      expect(find.text('Missing alt'), findsOneWidget);
      expect(find.text('Image not loaded'), findsOneWidget);
      expect(
        find.byWidgetPredicate(
          (widget) => widget is Image && widget.image is AssetImage,
        ),
        findsAtLeastNWidgets(1),
      );
    },
  );

  testWidgets(
    'TopicScreen keeps db image loading indicator until resource arrives',
    (tester) async {
      final repo = _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'delayed|en': const AppSuccess<String>('![Delayed](dbres:delayed)'),
        },
        topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
          'delayed|en': AppSuccess<TopicInfo?>(
            TopicInfo(
              name: 'Delayed',
              idIcon: '',
              description: 'Delayed image',
              route: 'delayed',
            ),
          ),
        },
      );
      final imageOrchestrator = _FakeTopicMarkdownImageOrchestrator(
        imageResultsByCacheKey: <String, TopicMarkdownImageLoadResult>{
          _cacheKeyForSource(
            'dbres:delayed',
          ): TopicMarkdownImageLoadResult.success(
            bytes: _png1x1,
            mimeType: 'image/png',
          ),
        },
        imageDelayByCacheKey: <String, Duration>{
          _cacheKeyForSource('dbres:delayed'): const Duration(
            milliseconds: 250,
          ),
        },
      );
      final harness = await _buildHarness(
        includeDialogHost: false,
        child: TopicScreen(
          file: 'delayed',
          topicContentCubitBuilder: _topicCubitBuilder(
            repo,
            topicMarkdownImageOrchestrator: imageOrchestrator,
          ),
        ),
      );
      addTearDown(harness.dispose);

      await tester.pumpWidget(harness.app);
      await _pumpUntilCondition(
        tester,
        condition: () => find.byType(MarkdownBody).evaluate().isNotEmpty,
      );

      expect(find.byType(CircularProgressIndicator), findsAtLeastNWidgets(1));

      await tester.pump(const Duration(milliseconds: 300));
      await tester.pump();

      expect(find.byType(MarkdownBody), findsOneWidget);
    },
  );

  testWidgets(
    'TopicScreen shows and clears loading state for delayed markdown',
    (tester) async {
      final repo = _ControllableTopicsRepository();
      final harness = await _buildHarness(
        includeDialogHost: false,
        child: TopicScreen(
          file: 'async_topic',
          topicContentCubitBuilder: _topicCubitBuilder(repo),
        ),
      );
      addTearDown(harness.dispose);

      await tester.pumpWidget(harness.app);
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      repo.completeMarkdown(
        requestKey: 'async_topic|en',
        result: const AppSuccess<String>('Async markdown ready'),
      );
      await tester.pumpAndSettle();

      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(find.byType(MarkdownBody), findsOneWidget);
    },
  );

  testWidgets(
    'TopicScreen desktop drag scrolls markdown content',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 700));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final longMarkdown = List<String>.generate(
        120,
        (index) => 'Paragraph $index with long test content.',
      ).join('\n\n');
      final repo = _FakeTopicsRepository(
        markdownByRouteLanguage: <String, AppResult<String>>{
          'long|en': AppSuccess<String>(longMarkdown),
        },
        topicByRouteLanguage: <String, AppResult<TopicInfo?>>{
          'long|en': AppSuccess<TopicInfo?>(
            TopicInfo(
              name: 'Long',
              idIcon: '',
              description: 'Long content',
              route: 'long',
            ),
          ),
        },
      );
      final harness = await _buildHarness(
        includeDialogHost: false,
        child: TopicScreen(
          file: 'long',
          topicContentCubitBuilder: _topicCubitBuilder(repo),
        ),
      );
      addTearDown(harness.dispose);

      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      final listenerFinder = find.byWidgetPredicate(
        (widget) =>
            widget is Listener &&
            widget.onPointerDown != null &&
            widget.onPointerMove != null &&
            widget.onPointerUp != null,
      );
      expect(listenerFinder, findsAtLeastNWidgets(1));

      final scrollableFinder = find.byType(Scrollable).first;
      final before = tester.state<ScrollableState>(scrollableFinder).position;
      expect(before.pixels, 0);

      final start = tester.getCenter(listenerFinder.first);
      final gesture = await tester.createGesture(kind: PointerDeviceKind.mouse);
      await gesture.addPointer(location: start);
      await gesture.down(start);
      await gesture.moveTo(Offset(start.dx, start.dy - 220));
      await gesture.up();
      await tester.pump();

      final after = tester.state<ScrollableState>(scrollableFinder).position;
      expect(after.pixels, greaterThan(0));
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );
}

TopicContentCubitBuilder _topicCubitBuilder(
  TopicsRepository repository, {
  TopicMarkdownImageOrchestrator? topicMarkdownImageOrchestrator,
}) {
  return ({
    required SettingsCubit settingsCubit,
    required String route,
    String? name,
    String? description,
  }) {
    return TopicContentCubit(
      topicsRepository: repository,
      settingsCubit: settingsCubit,
      route: route,
      name: name,
      description: description,
      topicMarkdownImageOrchestrator: topicMarkdownImageOrchestrator,
    );
  };
}

String _cacheKeyForSource(String source) {
  return RevelationMarkdownImageSource.parse(source).cacheKey;
}

Future<void> _invokeMarkdownLink(
  WidgetTester tester,
  String? href, {
  bool settle = true,
}) async {
  final markdownBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
  final callback = markdownBody.onTapLink;
  expect(callback, isNotNull);
  final result = (callback as dynamic)('test-link', href, '');
  if (result is Future) {
    await result;
  }
  if (settle) {
    await tester.pumpAndSettle();
  } else {
    await tester.pump();
  }
}

Future<void> _closeDialog(WidgetTester tester) async {
  if (find.byType(AlertDialog).evaluate().isEmpty) {
    return;
  }
  final context = tester.element(find.byType(AlertDialog));
  final l10n = AppLocalizations.of(context)!;
  await tester.tap(find.text(l10n.close));
  await tester.pumpAndSettle();
}

Future<void> _pumpUntilCondition(
  WidgetTester tester, {
  required bool Function() condition,
  int maxTicks = 20,
  Duration step = const Duration(milliseconds: 100),
}) async {
  for (var i = 0; i < maxTicks; i++) {
    await tester.pump(step);
    if (condition()) {
      return;
    }
  }
  fail('Condition was not met within $maxTicks ticks.');
}

Future<_TopicScreenHarness> _buildHarness({
  String language = 'en',
  required Widget child,
  bool includeDialogHost = true,
}) async {
  final settingsCubit = SettingsCubit(
    FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: language,
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    ),
  );
  await settingsCubit.loadSettings();

  final router = GoRouter(
    navigatorKey: includeDialogHost ? AppRouter().navigatorKey : null,
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (context, state) => BlocProvider<SettingsCubit>.value(
          value: settingsCubit,
          child: child,
        ),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) =>
            const Scaffold(body: Text('settings-page')),
      ),
      GoRoute(
        path: '/topic',
        builder: (context, state) => Scaffold(
          body: Text('topic-page:${state.uri.queryParameters['file']}'),
        ),
      ),
    ],
  );

  final app = MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
  );

  return _TopicScreenHarness(
    app: app,
    settingsCubit: settingsCubit,
    router: router,
  );
}

class _TopicScreenHarness {
  _TopicScreenHarness({
    required this.app,
    required this.settingsCubit,
    required this.router,
  });

  final Widget app;
  final SettingsCubit settingsCubit;
  final GoRouter router;

  Future<void> dispose() async {
    router.dispose();
    await settingsCubit.close();
  }
}

class _FakeTopicsRepository extends TopicsRepository {
  _FakeTopicsRepository({
    this.markdownByRouteLanguage = const <String, AppResult<String>>{},
    this.topicByRouteLanguage = const <String, AppResult<TopicInfo?>>{},
    this.resourceByKey = const <String, AppResult<TopicResource?>>{},
  }) : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<String>> markdownByRouteLanguage;
  final Map<String, AppResult<TopicInfo?>> topicByRouteLanguage;
  final Map<String, AppResult<TopicResource?>> resourceByKey;

  @override
  Future<AppResult<String>> getArticleMarkdown({
    required String route,
    required String language,
  }) async {
    final requestKey = '$route|$language';
    return markdownByRouteLanguage[requestKey] ?? const AppSuccess<String>('');
  }

  @override
  Future<AppResult<TopicInfo?>> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    final requestKey = '$route|$language';
    return topicByRouteLanguage[requestKey] ??
        const AppSuccess<TopicInfo?>(null);
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return resourceByKey[key] ??
        const AppFailureResult<TopicResource?>(
          AppFailure.notFound('Missing resource'),
        );
  }
}

class _ControllableTopicsRepository extends TopicsRepository {
  _ControllableTopicsRepository() : super(dataSource: _NoopTopicsDataSource());

  final Map<String, Completer<AppResult<String>>> _markdownByRequestKey =
      <String, Completer<AppResult<String>>>{};

  @override
  Future<AppResult<String>> getArticleMarkdown({
    required String route,
    required String language,
  }) {
    final requestKey = '$route|$language';
    final completer = _markdownByRequestKey.putIfAbsent(
      requestKey,
      () => Completer<AppResult<String>>(),
    );
    return completer.future;
  }

  @override
  Future<AppResult<TopicInfo?>> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    return const AppSuccess<TopicInfo?>(null);
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return const AppSuccess<TopicResource?>(null);
  }

  void completeMarkdown({
    required String requestKey,
    required AppResult<String> result,
  }) {
    final completer = _markdownByRequestKey[requestKey];
    if (completer == null) {
      throw StateError('No pending markdown request for key: $requestKey');
    }
    if (!completer.isCompleted) {
      completer.complete(result);
    }
  }
}

class _FakeTopicMarkdownImageOrchestrator
    extends TopicMarkdownImageOrchestrator {
  _FakeTopicMarkdownImageOrchestrator({
    this.imageResultsByCacheKey =
        const <String, TopicMarkdownImageLoadResult>{},
    this.imageDelayByCacheKey = const <String, Duration>{},
  }) : super(
         topicsRepository: TopicsRepository(
           dataSource: _NoopTopicsDataSource(),
         ),
       );

  final Map<String, TopicMarkdownImageLoadResult> imageResultsByCacheKey;
  final Map<String, Duration> imageDelayByCacheKey;

  @override
  Future<TopicMarkdownImageLoadResult> loadImage(
    RevelationMarkdownImageData image,
  ) async {
    final delay = imageDelayByCacheKey[image.cacheKey];
    if (delay != null) {
      await Future<void>.delayed(delay);
    }
    return imageResultsByCacheKey[image.cacheKey] ??
        const TopicMarkdownImageLoadResult.failure();
  }
}

class _NoopTopicsDataSource implements TopicsDataSource {
  @override
  Future<void> updateLanguage(String language) async {}

  @override
  Future<List<Article>> fetchArticles({bool onlyVisible = true}) async =>
      const <Article>[];

  @override
  Future<String> fetchArticleMarkdown(String route) async => '';

  @override
  Future<Article?> fetchArticleByRoute(String route) async => null;

  @override
  Future<CommonResource?> fetchCommonResource(String key) async => null;
}

Map<String, Uint8List> _withManifest(Map<String, Uint8List> assets) {
  final manifest = <String, List<Map<String, Object?>>>{};
  for (final key in assets.keys) {
    manifest[key] = <Map<String, Object?>>[
      <String, Object?>{'asset': key},
    ];
  }
  final encoded = const StandardMessageCodec().encodeMessage(manifest)!;
  return <String, Uint8List>{
    ...assets,
    'AssetManifest.bin': Uint8List.view(
      encoded.buffer,
      encoded.offsetInBytes,
      encoded.lengthInBytes,
    ),
  };
}

Uint8List _bytes(String value) => Uint8List.fromList(utf8.encode(value));

final Map<String, Uint8List> _dialogAssets = <String, Uint8List>{
  'assets/images/UI/error.svg': _bytes(_svg),
  'assets/images/UI/attention.svg': _bytes(_svg),
  'assets/images/UI/info.svg': _bytes(_svg),
  'assets/images/UI/additional.svg': _bytes(_svg),
};

const String _svg = '<svg viewBox="0 0 24 24"></svg>';

final Uint8List _png1x1 = base64Decode(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Zr8sAAAAASUVORK5CYII=',
);
