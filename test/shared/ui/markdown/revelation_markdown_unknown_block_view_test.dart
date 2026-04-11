@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_view.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  test('resolve update action returns null on web', () {
    final action = RevelationMarkdownUnknownBlockUpdateAction.resolve(
      isWebOverride: true,
    );

    expect(action, isNull);
  });

  test('resolve update action returns download route outside web', () {
    expect(
      RevelationMarkdownUnknownBlockUpdateAction.resolve(
        isWebOverride: false,
      )?.routeName,
      'download',
    );
  });

  testWidgets(
    'RevelationMarkdownBody renders fallback card for unknown markdown blocks',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: const RevelationMarkdownBody(
            data: '''
Before

{{timeline}}
title: Seven seals
{{/timeline}}

After
''',
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Before'), findsOneWidget);
      expect(find.text('After'), findsOneWidget);
      expect(find.text('Unsupported content block'), findsOneWidget);
      expect(find.textContaining('timeline'), findsOneWidget);
      expect(find.text('Update app'), findsOneWidget);
    },
  );
}
