@Tags(['widget'])
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/about/presentation/widgets/institution_card.dart';
import 'package:revelation/features/about/presentation/widgets/institution_list.dart';
import 'package:revelation/features/about/presentation/widgets/library_card.dart';
import 'package:revelation/features/about/presentation/widgets/library_list.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_card.dart';
import 'package:revelation/features/about/presentation/widgets/recommended_list.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

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

  testWidgets('LibraryList renders cards from bundle data', (tester) async {
    assetBytes = <String, Uint8List>{
      'assets/data/about_libraries.xml': _bytes(_librariesXml),
      'assets/images/UI/code.svg': _bytes(_svg),
    };

    await tester.pumpWidget(buildLocalizedTestApp(child: const LibraryList()));
    await pumpAndSettleSafe(tester);

    final context = tester.element(find.byType(LibraryList));
    final l10n = AppLocalizations.of(context)!;

    expect(find.byType(LibraryCard), findsOneWidget);
    expect(find.text('Sample ${l10n.package}'), findsOneWidget);
  });

  testWidgets('InstitutionList renders cards and sources', (tester) async {
    assetBytes = <String, Uint8List>{
      'assets/data/about_institutions.xml': _bytes(_institutionsXml),
      'assets/images/UI/institution.svg': _bytes(_svg),
    };

    await tester.pumpWidget(
      buildLocalizedTestApp(child: const InstitutionList()),
    );
    await pumpAndSettleSafe(tester);

    expect(find.byType(InstitutionCard), findsOneWidget);
    expect(find.text('Source A', findRichText: true), findsOneWidget);
  });

  testWidgets('RecommendedList shows error message on load failure', (
    tester,
  ) async {
    assetBytes = <String, Uint8List>{};

    await tester.pumpWidget(
      buildLocalizedTestApp(child: const RecommendedList()),
    );
    await pumpAndSettleSafe(tester);

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(RecommendedCard), findsNothing);
  });
}

Uint8List _bytes(String value) => Uint8List.fromList(utf8.encode(value));

const String _svg = '<svg viewBox="0 0 24 24"></svg>';

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
