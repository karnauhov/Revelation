@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/features/about/presentation/widgets/icon_url.dart';
import 'package:revelation/features/about/presentation/widgets/institution_card.dart';
import 'package:revelation/features/about/presentation/widgets/institution_list.dart';
import 'package:revelation/features/about/presentation/widgets/library_card.dart';
import 'package:revelation/features/about/presentation/widgets/library_list.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_card.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_list.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/institution_info.dart';
import 'package:revelation/shared/models/library_info.dart';
import 'package:revelation/shared/models/recommended_info.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/shared/ui/widgets/new_icon_button.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:url_launcher_platform_interface/link.dart';
import 'package:url_launcher_platform_interface/url_launcher_platform_interface.dart';

import '../../../../test_harness/widget_test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Map<String, Uint8List> assetBytes = <String, Uint8List>{};
  Map<String, Duration> assetDelays = <String, Duration>{};
  late UrlLauncherPlatform originalUrlLauncherPlatform;
  late _FakeUrlLauncherPlatform fakeUrlLauncherPlatform;

  setUpAll(() {
    fakeUrlLauncherPlatform = _FakeUrlLauncherPlatform();
    originalUrlLauncherPlatform = UrlLauncherPlatform.instance;
    UrlLauncherPlatform.instance = fakeUrlLauncherPlatform;

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (message) async {
          if (message == null) {
            return null;
          }
          final key = utf8.decode(message.buffer.asUint8List());
          final delay = assetDelays[key];
          if (delay != null) {
            await Future<void>.delayed(delay);
          }
          final data = assetBytes[key];
          if (data == null) {
            return null;
          }
          return ByteData.sublistView(data);
        });
  });

  tearDownAll(() {
    UrlLauncherPlatform.instance = originalUrlLauncherPlatform;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', null);
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    rootBundle.clear();
    assetBytes = <String, Uint8List>{};
    assetDelays = <String, Duration>{};
    fakeUrlLauncherPlatform.clear();
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets('LibraryList renders cards from bundle data', (tester) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/data/about_libraries.xml': _bytes(_librariesXml),
      'assets/images/UI/code.svg': _bytes(_svg),
    });

    await tester.pumpWidget(buildLocalizedTestApp(child: const LibraryList()));
    await _pumpUntil(tester, find.byType(LibraryCard));

    final context = tester.element(find.byType(LibraryList));
    final l10n = AppLocalizations.of(context)!;

    expect(find.byType(LibraryCard), findsOneWidget);
    expect(find.text('Sample ${l10n.package}'), findsOneWidget);
  });

  testWidgets('InstitutionList shows loader then renders cards', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/data/about_institutions.xml': _bytes(_institutionsXml),
      'assets/images/UI/institution.svg': _bytes(_svg),
    });
    assetDelays = <String, Duration>{
      'assets/data/about_institutions.xml': const Duration(milliseconds: 200),
    };

    await tester.pumpWidget(
      buildLocalizedTestApp(child: const InstitutionList()),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 300));
    await _pumpUntil(tester, find.byType(InstitutionCard));

    expect(find.byType(InstitutionCard), findsOneWidget);
    expect(find.text('Source A', findRichText: true), findsOneWidget);
  });

  testWidgets('InstitutionList shows error message on malformed xml', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/data/about_institutions.xml': _bytes(
        '<institutions><institution><name>Broken</name></institution></institutions>',
      ),
    });

    await tester.pumpWidget(
      buildLocalizedTestApp(child: const InstitutionList()),
    );
    await _pumpUntil(tester, find.byType(ErrorMessage));

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(InstitutionCard), findsNothing);
  });

  testWidgets('RecommendedList renders recommendation cards on success', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/data/about_recommended.xml': _bytes(_recommendedXml),
      'assets/images/UI/like.svg': _bytes(_svg),
      'assets/images/UI/recommended.svg': _bytes(_svg),
    });

    await tester.pumpWidget(
      buildLocalizedTestApp(child: const RecommendedList()),
    );
    await _pumpUntil(tester, find.byType(RecommendedCard));

    expect(find.byType(RecommendedCard), findsNWidgets(2));
    expect(find.text('Recommendation 1'), findsOneWidget);
    expect(find.text('Recommendation 2'), findsOneWidget);
  });

  testWidgets('RecommendedList shows error message on load failure', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{});
    await tester.pumpWidget(
      buildLocalizedTestApp(child: const RecommendedList()),
    );
    await _pumpUntil(tester, find.byType(ErrorMessage));

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(RecommendedCard), findsNothing);
  });

  testWidgets('IconUrl passes fixed button props and opens url on tap', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/store.svg': _bytes(_svg),
    });

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const IconUrl(
          iconPath: 'assets/images/UI/store.svg',
          url: 'https://example.com/store',
          tooltip: 'Store',
        ),
      ),
    );
    await _pumpFor(tester, const Duration(milliseconds: 200));

    final button = tester.widget<NewIconButton>(find.byType(NewIconButton));
    expect(button.assetPath, 'assets/images/UI/store.svg');
    expect(button.tooltip, 'Store');
    expect(button.size, 32);

    await tester.tap(find.byType(InkWell));
    await tester.pump();

    expect(fakeUrlLauncherPlatform.launchedUrls, ['https://example.com/store']);
  });

  testWidgets('InstitutionCard builds linked and plain sources contract', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/institution.svg': _bytes(_svg),
    });
    final institution = InstitutionInfo(
      name: 'Institution',
      idIcon: '',
      officialSite: 'https://example.com/institution',
      sources: <String, String>{
        'Source linked': 'https://example.com/source',
        'Source plain': '',
      },
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(child: InstitutionCard(institution: institution)),
    );
    await _pumpFor(tester, const Duration(milliseconds: 200));

    expect(find.text('Institution'), findsOneWidget);
    expect(find.byType(SvgPicture), findsOneWidget);

    final sourcesFinder = find.text(
      'Source linked, Source plain',
      findRichText: true,
    );
    expect(sourcesFinder, findsOneWidget);

    final sourcesText = tester.widget<RichText>(sourcesFinder).text as TextSpan;
    final children = sourcesText.children!;
    expect((children[0] as TextSpan).recognizer, isA<TapGestureRecognizer>());
    expect((children[2] as TextSpan).recognizer, isNull);
    expect(tester.widget<ListTile>(find.byType(ListTile)).onTap, isNotNull);
  });

  testWidgets('InstitutionCard uses raster icon for non-svg files', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/logo.png': _png1x1,
    });
    final institution = InstitutionInfo(
      name: 'Institution',
      idIcon: 'logo.png',
      officialSite: 'https://example.com/institution',
      sources: const <String, String>{},
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(child: InstitutionCard(institution: institution)),
    );
    await _pumpFor(tester, const Duration(milliseconds: 250));

    expect(find.byType(Image), findsOneWidget);
  });

  testWidgets('LibraryCard localizes placeholders and license text variants', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/code.svg': _bytes(_svg),
    });
    final linkedLibrary = LibraryInfo(
      name: 'Sample @Package @and @Icons @by Team',
      idIcon: '',
      license: 'MIT',
      officialSite: 'https://example.com/library',
      licenseLink: 'https://example.com/license',
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(child: LibraryCard(library: linkedLibrary)),
    );
    await _pumpFor(tester, const Duration(milliseconds: 250));

    final context = tester.element(find.byType(LibraryCard));
    final l10n = AppLocalizations.of(context)!;
    expect(
      find.text(
        'Sample ${l10n.package} ${l10n.and} ${l10n.icons} ${l10n.by} Team',
      ),
      findsOneWidget,
    );
    expect(find.text('${l10n.license} (MIT)'), findsOneWidget);
  });

  testWidgets('LibraryCard renders plain license when link is absent', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/code.svg': _bytes(_svg),
    });
    final library = LibraryInfo(
      name: 'Sample',
      idIcon: '',
      license: 'MIT',
      officialSite: 'https://example.com/library',
      licenseLink: '',
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(child: LibraryCard(library: library)),
    );
    await _pumpFor(tester, const Duration(milliseconds: 250));

    final context = tester.element(find.byType(LibraryCard));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text('MIT'), findsOneWidget);
    expect(find.text('${l10n.license} (MIT)'), findsNothing);
  });

  testWidgets('LibraryCard icon tint depends on icon id prefix', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/lib_sample.svg': _bytes(_svg),
      'assets/images/UI/custom.svg': _bytes(_svg),
    });

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: Column(
          children: <Widget>[
            LibraryCard(
              library: LibraryInfo(
                name: 'Lib icon',
                idIcon: 'lib_sample',
                license: 'MIT',
                officialSite: 'https://example.com',
                licenseLink: '',
              ),
            ),
            LibraryCard(
              library: LibraryInfo(
                name: 'Custom icon',
                idIcon: 'custom',
                license: 'MIT',
                officialSite: 'https://example.com',
                licenseLink: '',
              ),
            ),
          ],
        ),
      ),
    );
    await _pumpFor(tester, const Duration(milliseconds: 250));

    final icons = tester
        .widgetList<SvgPicture>(find.byType(SvgPicture))
        .toList();
    expect(icons, hasLength(2));
    expect(icons[0].colorFilter, isNull);
    expect(icons[1].colorFilter, isNotNull);
  });

  testWidgets('RecommendedCard renders fallback and raster icons', (
    tester,
  ) async {
    assetBytes = _withManifest(<String, Uint8List>{
      'assets/images/UI/like.svg': _bytes(_svg),
      'assets/images/UI/recommended.png': _png1x1,
    });

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: Column(
          children: <Widget>[
            RecommendedCard(
              recommended: RecommendedInfo(
                name: 'No icon',
                idIcon: '',
                officialSite: 'https://example.com/no-icon',
              ),
            ),
            RecommendedCard(
              recommended: RecommendedInfo(
                name: 'Png icon',
                idIcon: 'recommended.png',
                officialSite: 'https://example.com/png',
              ),
            ),
          ],
        ),
      ),
    );
    await _pumpFor(tester, const Duration(milliseconds: 250));

    expect(find.byType(SvgPicture), findsOneWidget);
    expect(find.byType(Image), findsOneWidget);
    expect(find.text('No icon'), findsOneWidget);
    expect(find.text('Png icon'), findsOneWidget);
  });
}

Uint8List _bytes(String value) => Uint8List.fromList(utf8.encode(value));

Future<void> _pumpFor(WidgetTester tester, Duration duration) async {
  await tester.pump();
  await tester.pump(duration);
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

Future<void> _pumpUntil(
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
}

const String _svg = '<svg viewBox="0 0 24 24"></svg>';
final Uint8List _png1x1 = base64Decode(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Zr8sAAAAASUVORK5CYII=',
);

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
    <name>Recommendation 1</name>
    <idIcon></idIcon>
    <officialSite>https://example.com/r1</officialSite>
  </recommendation>
  <recommendation>
    <name>Recommendation 2</name>
    <idIcon>recommended.svg</idIcon>
    <officialSite>https://example.com/r2</officialSite>
  </recommendation>
</recommendations>
''';

class _FakeUrlLauncherPlatform extends UrlLauncherPlatform {
  final List<String> launchedUrls = <String>[];

  @override
  LinkDelegate? get linkDelegate => null;

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
    return true;
  }

  void clear() {
    launchedUrls.clear();
  }
}
