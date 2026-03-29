@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/about/presentation/widgets/institution_card.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_card.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Map<String, Uint8List> assetBytes = <String, Uint8List>{};

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
    assetBytes = _buildAboutAssets();
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    debugDefaultTargetPlatformOverride = null;
  });

  tearDown(() async {
    debugDefaultTargetPlatformOverride = null;
    await GetIt.I.reset();
  });

  testWidgets('AboutScreen renders loaded content and expands major sections', (
    tester,
  ) async {
    final harness = _AboutScreenTestHarness();
    final cubit = await _createSettingsCubit(language: 'de');
    addTearDown(cubit.close);

    await tester.pumpWidget(
      _buildApp(
        cubit,
        dependencies: harness.buildDependencies(),
        aboutCubitBuilder: _buildAboutCubitBuilder(),
      ),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await _pumpUntilAboutScreenLoaded(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(
      find.byKey(const ValueKey('about-version-metadata')),
      findsOneWidget,
    );
    expect(find.byKey(const ValueKey('about-version-app')), findsOneWidget);
    expect(
      find.byKey(const ValueKey('about-version-common-db')),
      findsOneWidget,
    );
    expect(
      find.byKey(const ValueKey('about-version-localized-db')),
      findsOneWidget,
    );
    expect(find.text('1.2.3 (45)'), findsOneWidget);
    expect(find.text('-'), findsNWidgets(2));
    expect(
      find.descendant(
        of: find.byKey(const ValueKey('about-version-metadata')),
        matching: find.text(';'),
      ),
      findsNothing,
    );
    expect(
      find.byKey(const ValueKey('about-version-localized-db-code')),
      findsOneWidget,
    );
    expect(find.text('EN'), findsOneWidget);
    expect(find.textContaining(l10n.version), findsNothing);
    expect(find.textContaining(l10n.common_data_update), findsNothing);
    expect(
      find.textContaining(l10n.localized_data_update(l10n.language_name_en)),
      findsNothing,
    );

    await tester.ensureVisible(find.text(l10n.acknowledgements_title));
    await tester.tap(find.text(l10n.acknowledgements_title));
    await _pumpUntilFound(tester, find.byType(InstitutionCard));
    expect(find.byType(InstitutionCard), findsOneWidget);

    await tester.ensureVisible(find.text(l10n.recommended_title));
    await tester.tap(find.text(l10n.recommended_title));
    await _pumpUntilFound(tester, find.byType(RecommendedCard));
    expect(find.byType(RecommendedCard), findsOneWidget);
  });

  testWidgets(
    'AboutScreen localized DB badge supports es/uk/ru and fallback to en',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final cases = <String, String>{
        'es': 'ES',
        'uk': 'UK',
        'ru': 'RU',
        'de': 'EN',
      };

      for (final entry in cases.entries) {
        final cubit = await _createSettingsCubit(language: entry.key);
        await tester.pumpWidget(
          _buildApp(
            cubit,
            dependencies: harness.buildDependencies(),
            aboutCubitBuilder: _buildAboutCubitBuilder(),
          ),
        );
        await _pumpUntilAboutScreenLoaded(tester);

        expect(
          find.byKey(const ValueKey('about-version-localized-db-code')),
          findsOneWidget,
        );
        expect(find.text(entry.value), findsOneWidget);

        await cubit.close();
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      }
    },
  );

  testWidgets('AboutScreen app version tooltip shows localized build date', (
    tester,
  ) async {
    final harness = _AboutScreenTestHarness()
      ..appBuildTimestamp = DateTime(2026, 3, 29, 14, 15, 16);
    final cubit = await _createSettingsCubit(language: 'ru');
    addTearDown(cubit.close);

    await tester.pumpWidget(
      _buildApp(
        cubit,
        dependencies: harness.buildDependencies(),
        aboutCubitBuilder: _buildAboutCubitBuilder(
          appBuildTimestamp: harness.appBuildTimestamp,
        ),
        locale: const Locale('ru'),
      ),
    );
    await _pumpUntilAboutScreenLoaded(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;
    final expectedTooltip =
        '${l10n.app_version_from} '
        '${DateFormat.yMd('ru').add_jms().format(harness.appBuildTimestamp!)}';

    expect(find.byTooltip(expectedTooltip), findsOneWidget);
  });

  testWidgets(
    'AboutScreen app version tooltip falls back to version label without build timestamp',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final cubit = await _createSettingsCubit(language: 'en');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(
            appBuildTimestamp: harness.appBuildTimestamp,
          ),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);

      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;
      expect(find.byTooltip(l10n.version), findsOneWidget);
    },
  );

  testWidgets(
    'AboutScreen app version tooltip opens on tap for Android',
    (tester) async {
      final harness = _AboutScreenTestHarness()
        ..appBuildTimestamp = DateTime(2026, 3, 29, 14, 15, 16);
      final cubit = await _createSettingsCubit(language: 'ru');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(
            appBuildTimestamp: harness.appBuildTimestamp,
          ),
          locale: const Locale('ru'),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);

      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;
      final expectedTooltip =
          '${l10n.app_version_from} '
          '${DateFormat.yMd('ru').add_jms().format(harness.appBuildTimestamp!)}';

      final appVersionItem = find.byKey(const ValueKey('about-version-app'));
      await tester.ensureVisible(appVersionItem);
      await tester.tap(appVersionItem);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 250));

      expect(find.text(expectedTooltip), findsOneWidget);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );

  testWidgets('AboutScreen opens contact and legal external links', (
    tester,
  ) async {
    final harness = _AboutScreenTestHarness();
    final cubit = await _createSettingsCubit(language: 'en');
    addTearDown(cubit.close);

    await tester.pumpWidget(
      _buildApp(
        cubit,
        dependencies: harness.buildDependencies(),
        aboutCubitBuilder: _buildAboutCubitBuilder(),
      ),
    );
    await _pumpUntilAboutScreenLoaded(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.ensureVisible(find.text(AppConstants.supportEmail));
    await tester.tap(find.text(AppConstants.supportEmail));
    await tester.pump();

    await tester.tap(find.text(l10n.website));
    await tester.pump();

    await tester.tap(find.text(l10n.github_project));
    await tester.pump();

    await tester.tap(find.text(l10n.installation_packages));
    await tester.pump();

    await tester.tap(find.text(l10n.support_us));
    await tester.pump();

    expect(harness.launchedUrls.length, 5);
    expect(harness.launchedUrls[0], startsWith('mailto:'));
    expect(harness.launchedUrls[1], AppConstants.websiteUrl);
    expect(harness.launchedUrls[2], AppConstants.projectUrl);
    expect(harness.launchedUrls[3], AppConstants.latestReleaseUrl);
    expect(harness.launchedUrls[4], contains('en.html#join'));
  });

  testWidgets(
    'AboutScreen app info does not overflow on narrow Android width',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final cubit = await _createSettingsCubit(language: 'ru');
      addTearDown(cubit.close);

      tester.view.devicePixelRatio = 1.0;
      tester.view.physicalSize = const Size(376.7, 900);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(),
          locale: const Locale('ru'),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);
      await tester.pump();

      expect(_takeAllPumpExceptions(tester), isEmpty);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );

  testWidgets('AboutScreen legal topic links navigate through app router', (
    tester,
  ) async {
    final harness = _AboutScreenTestHarness();
    final cubit = await _createSettingsCubit(language: 'en');
    addTearDown(cubit.close);

    final router = GoRouter(
      routes: <RouteBase>[
        GoRoute(
          path: '/',
          builder: (_, __) => BlocProvider<SettingsCubit>.value(
            value: cubit,
            child: AboutScreen(
              dependencies: harness.buildDependencies(),
              aboutCubitBuilder: _buildAboutCubitBuilder(),
              diagnosticsIoTimeout: const Duration(milliseconds: 200),
            ),
          ),
        ),
        GoRoute(
          path: '/topic',
          builder: (_, state) => Scaffold(
            body: Text('Topic: ${state.uri.queryParameters['file']}'),
          ),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      MaterialApp.router(
        routerConfig: router,
        locale: const Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await _pumpUntilAboutScreenLoaded(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;

    final privacyPolicyTileFinder = find.widgetWithText(
      ListTile,
      l10n.privacy_policy,
    );
    await tester.ensureVisible(privacyPolicyTileFinder);
    await tester.tap(privacyPolicyTileFinder);
    await _pumpUntilFound(tester, find.text('Topic: privacy_policy'));
    expect(find.text('Topic: privacy_policy'), findsOneWidget);

    router.go('/');
    await pumpAndSettleSafe(tester);
    await _pumpUntilFound(tester, find.text(l10n.license));

    final licenseTileFinder = find.widgetWithText(ListTile, l10n.license);
    await tester.ensureVisible(licenseTileFinder);
    await tester.tap(licenseTileFinder);
    await _pumpUntilFound(tester, find.text('Topic: license'));
    expect(find.text('Topic: license'), findsOneWidget);
  });

  testWidgets(
    'AboutScreen changelog markdown link delegates to app link handler',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final handledLinks = <String?>[];
      final cubit = await _createSettingsCubit(language: 'en');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(
            appLinkHandler: (context, href) async {
              handledLinks.add(href);
              return true;
            },
          ),
          aboutCubitBuilder: _buildAboutCubitBuilder(
            changelog: '[Open site](https://example.com/md)',
          ),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);

      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.ensureVisible(find.text(l10n.changelog));
      await tester.tap(find.text(l10n.changelog));
      await _pumpUntilFound(tester, find.byType(MarkdownBody));

      final markdownBody = tester.widget<MarkdownBody>(
        find.byType(MarkdownBody),
      );
      markdownBody.onTapLink?.call('Open site', 'https://example.com/md', '');
      await tester.pump();

      expect(handledLinks, contains('https://example.com/md'));
    },
  );

  testWidgets(
    'AboutScreen bug report copies diagnostics and shows fallback message',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      harness.launchResult = false;
      harness.primarySourceFiles = const [
        PrimarySourceFileInfo(
          relativePath: 'primary_sources/a.txt',
          sizeBytes: 4096,
        ),
      ];
      harness.dbFileSizesByName.addAll({
        AppConstants.commonDB: 2048,
        AppConstants.localizedDB.replaceAll('@loc', 'en'): 4096,
        AppConstants.localizedDB.replaceAll('@loc', 'es'): 2048,
        AppConstants.localizedDB.replaceAll('@loc', 'uk'): 1024,
        AppConstants.localizedDB.replaceAll('@loc', 'ru'): 512,
      });
      harness.dbVersionByName.addAll({
        AppConstants.commonDB: DatabaseVersionInfo(
          schemaVersion: 4,
          dataVersion: 11,
          date: DateTime.utc(2026, 3, 21, 12, 0, 0),
        ),
        AppConstants.localizedDB.replaceAll('@loc', 'en'): DatabaseVersionInfo(
          schemaVersion: 4,
          dataVersion: 9,
          date: DateTime.utc(2026, 3, 21, 12, 10, 0),
        ),
      });
      harness.systemAndAppInfoBuilder = ({context, dbFilesSection}) {
        return [
          '=======PLATFORM / DART=======',
          'IsWeb: false',
          '',
          '=======DATA / DB FILES=======',
          dbFilesSection ?? '',
        ].join('\r\n');
      };

      final cubit = await _createSettingsCubit(language: 'en');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);

      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.ensureVisible(find.text(l10n.bug_report));
      await tester.tap(find.text(l10n.bug_report));
      await _pumpUntilFound(
        tester,
        find.textContaining(l10n.log_copied_message),
        maxTicks: 120,
      );
      await _pumpUntilCondition(
        tester,
        condition: () => harness.launchedUrls.isNotEmpty,
        maxTicks: 120,
      );

      expect(harness.launchedUrls, hasLength(1));
      expect(harness.launchedUrls.first, startsWith('mailto:'));

      final clipboardText = harness.clipboardText ?? '';
      expect(clipboardText, contains('=======TIMESTAMP======='));
      expect(clipboardText, contains('=======DATA / DB FILES======='));
      expect(clipboardText, contains('[PRIMARY SOURCES FILES]'));
      expect(clipboardText, contains('size=4.0 KB'));
      expect(clipboardText, contains('=======APP SETTINGS======='));
    },
  );

  testWidgets(
    'AboutScreen desktop drag listener handles pointer drag',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final cubit = await _createSettingsCubit(language: 'en');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(),
        ),
      );
      await pumpAndSettleSafe(tester);

      final listenerFinder = find.byWidgetPredicate(
        (widget) =>
            widget is Listener &&
            widget.onPointerDown != null &&
            widget.onPointerMove != null &&
            widget.onPointerUp != null,
      );
      expect(listenerFinder, findsAtLeastNWidgets(1));

      final start = tester.getCenter(listenerFinder.first);
      final gesture = await tester.createGesture(kind: PointerDeviceKind.mouse);
      await gesture.addPointer(location: start);
      await gesture.down(start);
      await gesture.moveTo(Offset(start.dx, start.dy - 60));
      await gesture.up();
      await tester.pump();

      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;
      expect(find.text(l10n.about_screen), findsOneWidget);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );

  testWidgets(
    'AboutScreen keeps section dividers visible on Windows when sections expand',
    (tester) async {
      final harness = _AboutScreenTestHarness();
      final cubit = await _createSettingsCubit(language: 'en');
      addTearDown(cubit.close);

      await tester.pumpWidget(
        _buildApp(
          cubit,
          dependencies: harness.buildDependencies(),
          aboutCubitBuilder: _buildAboutCubitBuilder(),
        ),
      );
      await _pumpUntilAboutScreenLoaded(tester);

      final dividerCountBefore = find.byType(Divider).evaluate().length;
      final context = tester.element(find.byType(AboutScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.ensureVisible(find.text(l10n.acknowledgements_title));
      await tester.tap(find.text(l10n.acknowledgements_title));
      await pumpFrames(tester, count: 20);

      await tester.ensureVisible(find.text(l10n.recommended_title));
      await tester.tap(find.text(l10n.recommended_title));
      await pumpFrames(tester, count: 20);

      await tester.ensureVisible(find.text(l10n.changelog));
      await tester.tap(find.text(l10n.changelog));
      await pumpFrames(tester, count: 20);

      final dividerCountAfter = find.byType(Divider).evaluate().length;
      expect(dividerCountAfter, dividerCountBefore);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );
}

class _AboutScreenTestHarness {
  final List<String> launchedUrls = <String>[];
  final Map<String, int?> dbFileSizesByName = <String, int?>{};
  final Map<String, DatabaseVersionInfo?> dbVersionByName =
      <String, DatabaseVersionInfo?>{};
  List<PrimarySourceFileInfo> primarySourceFiles = const [];
  String? clipboardText;
  DateTime? appBuildTimestamp;
  bool launchResult = true;
  String Function({BuildContext? context, String? dbFilesSection})?
  systemAndAppInfoBuilder;

  AboutScreenDependencies buildDependencies({
    AboutAppLinkHandler? appLinkHandler,
  }) {
    return AboutScreenDependencies(
      launchLink: (url) async {
        launchedUrls.add(url);
        return launchResult;
      },
      appLinkHandler: appLinkHandler ?? handleAppLink,
      collectSystemAndAppInfo: ({context, dbFilesSection}) async {
        if (systemAndAppInfoBuilder != null) {
          return systemAndAppInfoBuilder!(
            context: context,
            dbFilesSection: dbFilesSection,
          );
        }
        return '=======DATA / DB FILES=======\r\n${dbFilesSection ?? ''}\r\n';
      },
      databaseFileSizeLoader: (dbFile) async => dbFileSizesByName[dbFile],
      databaseVersionLoader: (dbFile) async => dbVersionByName[dbFile],
      primarySourceFilesLoader: () async => primarySourceFiles,
      writeClipboardText: (text) async {
        clipboardText = text;
      },
    );
  }
}

AboutCubitBuilder _buildAboutCubitBuilder({
  String changelog = _changelog,
  DateTime? appBuildTimestamp,
}) {
  return (initialLanguageCode) => AboutCubit(
    initialLanguageCode: initialLanguageCode,
    packageInfoLoader: () async => PackageInfo(
      appName: 'Revelation',
      packageName: 'revelation.app',
      version: '1.2.3',
      buildNumber: '45',
    ),
    changelogLoader: () async => changelog,
    appBuildTimestampLoader: () async => appBuildTimestamp,
    dbVersionInfoLoader: (_) async => null,
  );
}

Future<SettingsCubit> _createSettingsCubit({required String language}) async {
  final repository = FakeSettingsRepository(
    initialSettings: AppSettings(
      selectedLanguage: language,
      selectedTheme: 'manuscript',
      selectedFontSize: 'medium',
      soundEnabled: true,
    ),
  );
  final cubit = SettingsCubit(repository);
  await cubit.loadSettings();
  return cubit;
}

Future<void> _pumpUntilFound(
  WidgetTester tester,
  Finder finder, {
  int maxTicks = 40,
  Duration step = const Duration(milliseconds: 120),
}) async {
  for (var i = 0; i < maxTicks; i++) {
    await tester.pump(step);
    if (finder.evaluate().isNotEmpty) {
      return;
    }
  }
  fail('Finder did not appear within $maxTicks ticks: $finder');
}

Future<void> _pumpUntilCondition(
  WidgetTester tester, {
  required bool Function() condition,
  int maxTicks = 40,
  Duration step = const Duration(milliseconds: 120),
}) async {
  for (var i = 0; i < maxTicks; i++) {
    await tester.pump(step);
    if (condition()) {
      return;
    }
  }
  fail('Condition was not met within $maxTicks ticks.');
}

Future<void> _pumpUntilAboutScreenLoaded(
  WidgetTester tester, {
  int maxTicks = 60,
  Duration step = const Duration(milliseconds: 120),
}) async {
  for (var i = 0; i < maxTicks; i++) {
    await tester.pump(step);
    if (find.byType(CircularProgressIndicator).evaluate().isEmpty &&
        find.byType(AboutScreen).evaluate().isNotEmpty) {
      return;
    }
  }
  fail('AboutScreen did not finish loading within $maxTicks ticks.');
}

Widget _buildApp(
  SettingsCubit cubit, {
  required AboutScreenDependencies dependencies,
  required AboutCubitBuilder aboutCubitBuilder,
  Locale locale = const Locale('en'),
}) {
  return BlocProvider<SettingsCubit>.value(
    value: cubit,
    child: buildLocalizedTestApp(
      locale: locale,
      child: AboutScreen(
        dependencies: dependencies,
        aboutCubitBuilder: aboutCubitBuilder,
        diagnosticsIoTimeout: const Duration(milliseconds: 200),
      ),
      withScaffold: false,
    ),
  );
}

List<Object> _takeAllPumpExceptions(WidgetTester tester) {
  final exceptions = <Object>[];
  while (true) {
    final exception = tester.takeException();
    if (exception == null) {
      return exceptions;
    }
    exceptions.add(exception);
  }
}

Map<String, Uint8List> _buildAboutAssets({
  String institutions = _institutionsXml,
  String recommended = _recommendedXml,
  String libraries = _librariesXml,
}) {
  return <String, Uint8List>{
    'assets/data/about_libraries.xml': _bytes(libraries),
    'assets/data/about_institutions.xml': _bytes(institutions),
    'assets/data/about_recommended.xml': _bytes(recommended),
    'assets/images/UI/main-icon.svg': _bytes(_svg),
    'assets/images/UI/email.svg': _bytes(_svg),
    'assets/images/UI/www.svg': _bytes(_svg),
    'assets/images/UI/github.svg': _bytes(_svg),
    'assets/images/UI/download.svg': _bytes(_svg),
    'assets/images/UI/shield.svg': _bytes(_svg),
    'assets/images/UI/license.svg': _bytes(_svg),
    'assets/images/UI/support_us.svg': _bytes(_svg),
    'assets/images/UI/thank-you.svg': _bytes(_svg),
    'assets/images/UI/like.svg': _bytes(_svg),
    'assets/images/UI/changelog.svg': _bytes(_svg),
    'assets/images/UI/bug.svg': _bytes(_svg),
    'assets/images/UI/google_play.svg': _bytes(_svg),
    'assets/images/UI/microsoft_store.svg': _bytes(_svg),
    'assets/images/UI/snapcraft.svg': _bytes(_svg),
    'assets/images/UI/code.svg': _bytes(_svg),
    'assets/images/UI/institution.svg': _bytes(_svg),
  };
}

Uint8List _bytes(String value) => Uint8List.fromList(utf8.encode(value));

const String _svg = '<svg viewBox="0 0 24 24"></svg>';

const String _changelog = '''
# Changelog
- Added tests
''';

const String _librariesXml = '''
<libraries>
  <library>
    <name>Sample @Package</name>
    <idIcon></idIcon>
    <license>MIT</license>
    <officialSite>https://example.com</officialSite>
    <licenseLink></licenseLink>
  </library>
</libraries>
''';

const String _institutionsXml = '''
<institutions>
  <institution>
    <name>Institution</name>
    <idIcon></idIcon>
    <officialSite>https://example.com</officialSite>
    <sources>
      <source>
        <text>Source A</text>
        <link></link>
      </source>
    </sources>
  </institution>
</institutions>
''';

const String _recommendedXml = '''
<recommendations>
  <recommendation>
    <name>Recommendation</name>
    <idIcon></idIcon>
    <officialSite>https://example.com</officialSite>
  </recommendation>
</recommendations>
''';
