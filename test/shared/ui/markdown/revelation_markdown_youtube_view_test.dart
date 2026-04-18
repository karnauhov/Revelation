@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_view.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  setUp(() {
    RevelationMarkdownYoutubeView.embedBuilderForTest =
        ({required video, key}) => DecoratedBox(
          key: key,
          decoration: const BoxDecoration(color: Colors.black),
          child: const Center(child: Text('Fake YouTube Player')),
        );
  });

  tearDown(() {
    RevelationMarkdownYoutubeView.embedBuilderForTest = null;
  });

  testWidgets('RevelationMarkdownBody renders youtube block with player only', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const SingleChildScrollView(
          child: RevelationMarkdownBody(
            data: '''
Before

{{youtube}}
url: https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=42s
title: Big Buck Bunny
caption: Optional caption.
{{/youtube}}

After
''',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Before'), findsOneWidget);
    expect(find.text('After'), findsOneWidget);
    expect(find.text('Fake YouTube Player'), findsOneWidget);
    expect(find.text('Optional caption.'), findsNothing);
    expect(find.text('Big Buck Bunny'), findsNothing);
    expect(find.text('Open on YouTube'), findsNothing);
  });

  testWidgets('invalid youtube block renders graceful fallback card', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const RevelationMarkdownBody(
          data: '''
{{youtube}}
url: https://example.com/not-youtube
{{/youtube}}
''',
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('YouTube video unavailable'), findsOneWidget);
  });

  testWidgets('view renders player when title is missing', (tester) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: RevelationMarkdownYoutubeView(
          video: const RevelationMarkdownYoutubeData(
            rawSource: 'dQw4w9WgXcQ',
            videoId: 'dQw4w9WgXcQ',
            startAtSeconds: 0,
            aspectRatio: 16 / 9,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Fake YouTube Player'), findsOneWidget);
  });
}
