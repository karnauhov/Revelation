@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('DescriptionMarkdownView uses Markdown when scrollable', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(data: 'Hello **world**'),
      ),
    );

    final markdown = tester.widget<Markdown>(find.byType(Markdown));
    expect(markdown.data, contains('Hello'));
  });

  testWidgets('DescriptionMarkdownView uses MarkdownBody when static', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: 'Static text',
          scrollable: false,
        ),
      ),
    );

    final markdownBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
    expect(markdownBody.data, contains('Static text'));
  });
}
