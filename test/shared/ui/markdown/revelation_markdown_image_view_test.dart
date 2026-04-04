@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_state.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_view.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets(
    'RevelationMarkdownImageView clips loading frame overflow in tiny explicit size',
    (tester) async {
      final cleanupErrors = _captureRenderFlexOverflows();
      addTearDown(cleanupErrors);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: Center(
            child: RevelationMarkdownImageView(
              image: RevelationMarkdownImageData(
                source: RevelationMarkdownImageSource.parse(
                  'https://example.com/image.png',
                ),
                alt: '',
                alignment: RevelationMarkdownImageAlignment.center,
                isBlockImage: true,
                width: 120,
                height: 40,
              ),
            ),
          ),
        ),
      );
      await tester.pump();

      expect(_capturedRenderFlexOverflowMessages, isEmpty);
    },
  );

  testWidgets(
    'RevelationMarkdownImageView clips block image caption overflow in constrained height',
    (tester) async {
      final cleanupErrors = _captureRenderFlexOverflows();
      addTearDown(cleanupErrors);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: SizedBox(
            width: 140,
            height: 60,
            child: RevelationMarkdownImageView(
              image: RevelationMarkdownImageData(
                source: RevelationMarkdownImageSource.parse('bad-source'),
                alt: 'Fallback label',
                caption: 'Caption text that should be silently clipped',
                alignment: RevelationMarkdownImageAlignment.center,
                isBlockImage: true,
                width: 120,
                height: 40,
              ),
              imageState: const RevelationMarkdownImageState.failure(),
            ),
          ),
        ),
      );
      await tester.pump();

      expect(_capturedRenderFlexOverflowMessages, isEmpty);
    },
  );

  testWidgets(
    'RevelationMarkdownImageView does not trigger constraint assertions inside wrap layouts',
    (tester) async {
      final cleanupErrors = _captureConstraintAssertions();
      addTearDown(cleanupErrors);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: SingleChildScrollView(
            child: Wrap(
              children: [
                RevelationMarkdownImageView(
                  image: RevelationMarkdownImageData(
                    source: RevelationMarkdownImageSource.parse('bad-source'),
                    alt: 'Fallback label',
                    caption: 'Caption text that should be silently clipped',
                    alignment: RevelationMarkdownImageAlignment.center,
                    isBlockImage: true,
                    width: 120,
                    height: 40,
                  ),
                  imageState: const RevelationMarkdownImageState.failure(),
                ),
              ],
            ),
          ),
        ),
      );
      await tester.pump();

      expect(_capturedConstraintAssertionMessages, isEmpty);
    },
  );
}

final List<String> _capturedRenderFlexOverflowMessages = <String>[];
final List<String> _capturedConstraintAssertionMessages = <String>[];

VoidCallback _captureRenderFlexOverflows() {
  _capturedRenderFlexOverflowMessages.clear();
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('A RenderFlex overflowed by')) {
      _capturedRenderFlexOverflowMessages.add(message);
      return;
    }
    originalHandler?.call(details);
  };

  return () {
    FlutterError.onError = originalHandler;
    _capturedRenderFlexOverflowMessages.clear();
  };
}

VoidCallback _captureConstraintAssertions() {
  _capturedConstraintAssertionMessages.clear();
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('does not meet its constraints') ||
        message.contains('RenderBox was not laid out')) {
      _capturedConstraintAssertionMessages.add(message);
      return;
    }
    originalHandler?.call(details);
  };

  return () {
    FlutterError.onError = originalHandler;
    _capturedConstraintAssertionMessages.clear();
  };
}
