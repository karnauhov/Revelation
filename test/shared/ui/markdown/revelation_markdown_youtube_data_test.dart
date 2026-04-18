import 'package:flutter_test/flutter_test.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';

void main() {
  test('parses direct video id and explicit configuration', () {
    final element = md.Element.empty(RevelationMarkdownYoutubeData.tag)
      ..attributes.addAll(<String, String>{
        'id': 'dQw4w9WgXcQ',
        'title': 'Example video',
        'caption': 'Optional caption',
        'width': '960',
        'height': '540',
        'start': '95',
      });

    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);

    expect(video, isNotNull);
    expect(video!.isValid, isTrue);
    expect(video.videoId, 'dQw4w9WgXcQ');
    expect(video.title, 'Example video');
    expect(video.caption, 'Optional caption');
    expect(video.startAtSeconds, 95);
    expect(video.resolvedAspectRatio, closeTo(16 / 9, 0.0001));
    expect(video.maxWidth, 960);
    expect(
      video.embedUri.toString(),
      'https://www.youtube.com/embed/dQw4w9WgXcQ?playsinline=1&fs=1&rel=0&loop=1&playlist=dQw4w9WgXcQ&start=95',
    );
    expect(
      video.originalVideoUri.toString(),
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=95s',
    );
  });

  test('extracts video id and start time from watch url', () {
    final element = md.Element.empty(
      RevelationMarkdownYoutubeData.tag,
    )..attributes['url'] = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=1m5s';

    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);

    expect(video, isNotNull);
    expect(video!.isValid, isTrue);
    expect(video.videoId, 'aqz-KE-bpKQ');
    expect(video.startAtSeconds, 65);
  });

  test('extracts video id from short youtube urls', () {
    final element = md.Element.empty(RevelationMarkdownYoutubeData.tag)
      ..attributes['url'] = 'https://youtu.be/M7lc1UVf-VE';

    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);

    expect(video, isNotNull);
    expect(video!.isValid, isTrue);
    expect(video.videoId, 'M7lc1UVf-VE');
    expect(video.startAtSeconds, 0);
  });

  test('keeps invalid sources visible for fallback rendering', () {
    final element = md.Element.empty(RevelationMarkdownYoutubeData.tag)
      ..attributes['url'] = 'https://example.com/not-youtube';

    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);

    expect(video, isNotNull);
    expect(video!.isValid, isFalse);
    expect(video.videoId, isEmpty);
    expect(
      video.originalVideoUri.toString(),
      'https://example.com/not-youtube',
    );
  });
}
