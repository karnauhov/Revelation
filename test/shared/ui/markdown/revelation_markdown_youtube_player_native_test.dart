import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_player_native.dart';

void main() {
  test('allows localhost main-frame navigation inside the player shell', () {
    final decision = resolveRevelationMarkdownYoutubeNavigation(
      uri: Uri.parse(
        'http://localhost:8787/data/markdown/markdown_youtube_player.html',
      ),
      isForMainFrame: true,
    );

    expect(decision.allowInWebView, isTrue);
    expect(decision.externalUrl, isNull);
  });

  test('opens external main-frame navigation outside the player shell', () {
    final decision = resolveRevelationMarkdownYoutubeNavigation(
      uri: Uri.parse('https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
      isForMainFrame: true,
    );

    expect(decision.allowInWebView, isFalse);
    expect(decision.externalUrl, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  });

  test('allows subframe requests to keep the embedded player working', () {
    final decision = resolveRevelationMarkdownYoutubeNavigation(
      uri: Uri.parse('https://www.youtube.com/embed/dQw4w9WgXcQ'),
      isForMainFrame: false,
    );

    expect(decision.allowInWebView, isTrue);
    expect(decision.externalUrl, isNull);
  });

  test('create-window attempts resolve to an external browser url', () {
    final externalUrl = resolveRevelationMarkdownYoutubeCreateWindowExternalUrl(
      Uri.parse('https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
    );

    expect(externalUrl, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  });

  test('escaped shell url resolver ignores localhost player shell urls', () {
    final externalUrl = resolveRevelationMarkdownYoutubeEscapedShellExternalUrl(
      Uri.parse(
        'http://localhost:8787/data/markdown/markdown_youtube_player.html',
      ),
    );

    expect(externalUrl, isNull);
  });

  test(
    'escaped shell url resolver returns external urls for recovery flow',
    () {
      final externalUrl =
          resolveRevelationMarkdownYoutubeEscapedShellExternalUrl(
            Uri.parse('https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
          );

      expect(externalUrl, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    },
  );

  test('external launch dedupe suppresses the same url in a short window', () {
    final suppress = shouldSuppressRevelationMarkdownYoutubeExternalLaunch(
      externalUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      lastExternalUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      lastExternalLaunchAt: DateTime(2026, 4, 18, 12, 0, 0),
      now: DateTime(2026, 4, 18, 12, 0, 0, 500),
    );

    expect(suppress, isTrue);
  });

  test('external launch dedupe allows the same url after the time window', () {
    final suppress = shouldSuppressRevelationMarkdownYoutubeExternalLaunch(
      externalUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      lastExternalUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      lastExternalLaunchAt: DateTime(2026, 4, 18, 12, 0, 0),
      now: DateTime(2026, 4, 18, 12, 0, 2),
    );

    expect(suppress, isFalse);
  });

  test('external launch dedupe allows a different url immediately', () {
    final suppress = shouldSuppressRevelationMarkdownYoutubeExternalLaunch(
      externalUrl: 'https://www.youtube.com/watch?v=aqz-KE-bpKQ',
      lastExternalUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      lastExternalLaunchAt: DateTime(2026, 4, 18, 12, 0, 0),
      now: DateTime(2026, 4, 18, 12, 0, 0, 500),
    );

    expect(suppress, isFalse);
  });
}
