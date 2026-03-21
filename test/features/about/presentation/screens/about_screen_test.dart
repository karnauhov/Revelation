@Tags(['widget'])
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Map<String, Uint8List> assetBytes = <String, Uint8List>{};

  setUpAll(() {
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation.app',
      version: '1.2.3',
      buildNumber: '45',
      buildSignature: 'build',
    );
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

  setUp(() {
    assetBytes = _buildAboutAssets();
  });

  testWidgets('AboutScreen renders loading then content', (tester) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await pumpAndSettleSafe(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(find.text('${l10n.version} 1.2.3 (45)'), findsOneWidget);
    expect(find.textContaining(l10n.common_data_update), findsOneWidget);
    expect(
      find.textContaining(l10n.localized_data_update(l10n.language_name_en)),
      findsOneWidget,
    );
    await tester.tap(find.text(l10n.changelog));
    await pumpAndSettleSafe(tester);

    final markdown = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
    expect(markdown.data, contains('Added tests'));
    expect(find.text(l10n.acknowledgements_title), findsOneWidget);
    expect(find.text(l10n.recommended_title), findsOneWidget);
  });
}

Widget _buildApp(SettingsCubit cubit) {
  return BlocProvider<SettingsCubit>.value(
    value: cubit,
    child: buildLocalizedTestApp(
      locale: const Locale('en'),
      child: const AboutScreen(),
      withScaffold: false,
    ),
  );
}

Map<String, Uint8List> _buildAboutAssets() {
  return <String, Uint8List>{
    'CHANGELOG.md': _bytes(_changelog),
    'assets/data/about_libraries.xml': _bytes(_librariesXml),
    'assets/data/about_institutions.xml': _bytes(_institutionsXml),
    'assets/data/about_recommended.xml': _bytes(_recommendedXml),
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
