@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/dialogs/dialogs_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late _DialogRouteObserver observer;
  late _FakeAssetBundle bundle;

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    observer = _DialogRouteObserver();
    bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/error.svg': _svg,
      'assets/images/UI/attention.svg': _svg,
      'assets/images/UI/info.svg': _svg,
      'assets/images/UI/additional.svg': _svg,
    });
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets('showCustomDialog is no-op when AppRouter context is absent', (
    tester,
  ) async {
    expect(
      () => showCustomDialog(MessageType.errorCommon, param: 'x'),
      returnsNormally,
    );
    await tester.pump();
    expect(find.byType(AlertDialog), findsNothing);
  });

  testWidgets('error broken link dialog uses error route and localized text', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await _pumpDialogHost(tester, observer: observer, bundle: bundle);

    showCustomDialog(
      MessageType.errorBrokenLink,
      param: 'https://example.com/broken',
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(AlertDialog));
    final l10n = AppLocalizations.of(context)!;

    expect(observer.lastPushedName, 'error_dialog');
    expect(find.text(l10n.error), findsOneWidget);
    expect(find.textContaining(l10n.unable_to_follow_the_link), findsOneWidget);
    expect(find.textContaining('https://example.com/broken'), findsOneWidget);
  });

  testWidgets('warning and info dialogs use their route contracts', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await _pumpDialogHost(tester, observer: observer, bundle: bundle);

    showCustomDialog(MessageType.warningCommon, param: 'Careful');
    await tester.pumpAndSettle();
    expect(observer.lastPushedName, 'warning_dialog');
    await tester.tap(find.byType(TextButton));
    await tester.pumpAndSettle();

    showCustomDialog(MessageType.infoCommon, param: 'All good');
    await tester.pumpAndSettle();
    expect(observer.lastPushedName, 'info_dialog');
    expect(find.text('All good'), findsOneWidget);
  });

  testWidgets(
    'dialog shows additional markdown section when extension provided',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 900));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await _pumpDialogHost(tester, observer: observer, bundle: bundle);

      showCustomDialog(
        MessageType.errorCommon,
        param: 'Base message',
        markdownExtension: '**Trace details**',
      );
      await tester.pumpAndSettle();
      _consumeExpectedOverflowIfAny(tester);

      final context = tester.element(find.byType(AlertDialog));
      final l10n = AppLocalizations.of(context)!;

      expect(find.text('Base message'), findsOneWidget);
      expect(find.text(l10n.more_information), findsOneWidget);

      await tester.tap(find.text(l10n.more_information));
      await tester.pumpAndSettle();
      _consumeExpectedOverflowIfAny(tester);

      expect(find.byType(MarkdownBody), findsOneWidget);
      expect(find.textContaining('Trace details'), findsOneWidget);
    },
  );

  testWidgets('close button dismisses dialog', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1200, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await _pumpDialogHost(tester, observer: observer, bundle: bundle);

    showCustomDialog(MessageType.infoCommon, param: 'Info');
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsOneWidget);

    final context = tester.element(find.byType(AlertDialog));
    final l10n = AppLocalizations.of(context)!;
    await tester.tap(find.text(l10n.close));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsNothing);
  });
}

Future<void> _pumpDialogHost(
  WidgetTester tester, {
  required NavigatorObserver observer,
  required AssetBundle bundle,
}) async {
  await tester.pumpWidget(
    DefaultAssetBundle(
      bundle: bundle,
      child: MaterialApp(
        navigatorKey: AppRouter().navigatorKey,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        navigatorObservers: <NavigatorObserver>[observer],
        home: const Scaffold(body: SizedBox.shrink()),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

class _DialogRouteObserver extends NavigatorObserver {
  String? lastPushedName;

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    lastPushedName = route.settings.name;
    super.didPush(route, previousRoute);
  }
}

class _FakeAssetBundle extends AssetBundle {
  _FakeAssetBundle(this._assets);

  final Map<String, String> _assets;

  @override
  Future<ByteData> load(String key) async {
    final value = _assets[key];
    if (value == null) {
      throw Exception('Unable to load asset: $key');
    }
    final bytes = Uint8List.fromList(utf8.encode(value));
    return ByteData.sublistView(bytes);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final value = _assets[key];
    if (value == null) {
      throw Exception('Unable to load asset: $key');
    }
    return value;
  }

  @override
  Future<T> loadStructuredData<T>(
    String key,
    Future<T> Function(String value) parser,
  ) async {
    return parser(await loadString(key));
  }

  @override
  void evict(String key) {}

  @override
  void clear() {}
}

const String _svg = '<svg viewBox="0 0 24 24"></svg>';

void _consumeExpectedOverflowIfAny(WidgetTester tester) {
  final exception = tester.takeException();
  if (exception == null) {
    return;
  }

  expect(exception, isA<FlutterError>());
  expect(exception.toString(), contains('A RenderFlex overflowed'));
}
