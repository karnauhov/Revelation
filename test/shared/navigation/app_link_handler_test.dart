@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:talker_flutter/talker_flutter.dart';
import '../../test_harness/test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    setDefaultWordTapHandler(null);
  });

  tearDown(() async {
    setDefaultWordTapHandler(null);
    await GetIt.I.reset();
  });

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

  testWidgets('word link returns false when callbacks are not provided', (
    tester,
  ) async {
    final context = await pumpContext(tester);

    final handled = await handleAppLink(context, 'word:source-c:page-c:2');

    expect(handled, isFalse);
  });
}
