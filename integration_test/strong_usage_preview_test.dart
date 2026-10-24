import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('first long press shows the verse preview and copies it once', (
    tester,
  ) async {
    final copied = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: StrongDictionaryEntryView(
            strongNumber: 1,
            markdown: '[Gen 1:1](bible:Gen1:1 "strong_usage_ref:001")',
            bibleTextProvider: _TextProvider(),
            copyBibleText: (text) async {
              copied.add(text);
            },
            onStrongNumberSelected: (_) {},
            onStrongNumberPickerRequested: (_, __) {},
            onNavigateBackward: () {},
            onNavigateForward: () {},
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.longPress(find.text('Gen 1:1'));
    await tester.pumpAndSettle();
    expect(copied, ['first verse preview']);
    expect(
      find.text('first verse preview', findRichText: true),
      findsOneWidget,
    );
    binding.reportData = {'firstLongPressPreviewAndCopy': true};
  });
}

class _TextProvider implements StrongUsageBibleTextProvider {
  @override
  Future<String?> loadVerseText(String verseKey) async => 'first verse preview';
}
