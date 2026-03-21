import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview_painters.dart';
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/verse.dart';

void main() {
  test('RelativeVersesPainter.verseLabel formats chapter and verse', () {
    const verse = Verse(
      chapterNumber: 3,
      verseNumber: 14,
      labelPosition: Offset.zero,
    );

    expect(RelativeVersesPainter.verseLabel(verse), '3:14');
  });

  test('RelativeVersesPainter.getLabelRect clamps to viewport bounds', () {
    const verse = Verse(
      chapterNumber: 1,
      verseNumber: 1,
      labelPosition: Offset(2, 2),
    );

    final rect = RelativeVersesPainter.getLabelRect(
      verse,
      const Size(320, 240),
    );

    expect(rect.left, greaterThanOrEqualTo(0));
    expect(rect.top, greaterThanOrEqualTo(0));
    expect(rect.right, lessThanOrEqualTo(320));
    expect(rect.bottom, lessThanOrEqualTo(240));
  });

  test('painters draw without throwing for representative input', () {
    expect(
      () => _paint(
        RelativeLinesPainter(
          lines: [SingleLine(0.1, 0.1, 0.8, 0.8, color: Colors.green)],
        ),
      ),
      returnsNormally,
    );
    expect(
      () => _paint(
        RelativeVersesPainter(
          verses: const [
            Verse(
              chapterNumber: 1,
              verseNumber: 2,
              labelPosition: Offset(0.2, 0.2),
              contours: [
                [Offset(0.1, 0.1), Offset(0.2, 0.1), Offset(0.2, 0.2)],
              ],
            ),
          ],
          selectedVerseIndex: 0,
        ),
      ),
      returnsNormally,
    );
    expect(
      () => _paint(
        RelativeTextsPainter(
          texts: [
            TextLabel(
              '123',
              0.2,
              0.4,
              strokeColor: Colors.black,
              strokeWidth: 1,
            ),
          ],
          selectedNumber: 123,
        ),
      ),
      returnsNormally,
    );
    expect(
      () => _paint(
        RelativeRectsDashedPainter(
          rects: [PageRect(0.7, 0.8, 0.2, 0.1)],
          color: Colors.blue.withValues(alpha: 0.2),
        ),
      ),
      returnsNormally,
    );
    expect(
      () => _paint(
        RelativeRectsPainter(
          rects: [PageRect(0.6, 0.7, 0.1, 0.2)],
          strokeColor: Colors.red,
          strokeWidth: 1.5,
        ),
      ),
      returnsNormally,
    );
  });

  test('shouldRepaint contracts follow explicit state differences', () {
    final linesA = RelativeLinesPainter(lines: [SingleLine(0, 0, 1, 1)]);
    final linesB = RelativeLinesPainter(lines: [SingleLine(0, 0, 1, 1)]);
    expect(linesA.shouldRepaint(linesA), isFalse);
    expect(linesA.shouldRepaint(linesB), isTrue);

    final versesA = RelativeVersesPainter(
      verses: const [
        Verse(chapterNumber: 1, verseNumber: 1, labelPosition: Offset.zero),
      ],
      selectedVerseIndex: 0,
    );
    final versesB = RelativeVersesPainter(
      verses: const [
        Verse(chapterNumber: 1, verseNumber: 2, labelPosition: Offset.zero),
      ],
      selectedVerseIndex: 0,
    );
    expect(versesA.shouldRepaint(versesA), isFalse);
    expect(versesA.shouldRepaint(versesB), isTrue);

    final textsA = RelativeTextsPainter(
      texts: [TextLabel('1', 0, 0)],
      selectedNumber: 1,
    );
    final textsB = RelativeTextsPainter(
      texts: [TextLabel('2', 0, 0)],
      selectedNumber: 1,
    );
    expect(textsA.shouldRepaint(textsA), isFalse);
    expect(textsA.shouldRepaint(textsB), isTrue);

    final dashedA = RelativeRectsDashedPainter(rects: [PageRect(0, 0, 1, 1)]);
    final dashedB = RelativeRectsDashedPainter(
      rects: [PageRect(0, 0, 1, 1)],
      strokeWidth: 3,
    );
    expect(dashedA.shouldRepaint(dashedA), isFalse);
    expect(dashedA.shouldRepaint(dashedB), isTrue);

    final rectsA = RelativeRectsPainter(rects: [PageRect(0, 0, 1, 1)]);
    final rectsB = RelativeRectsPainter(rects: [PageRect(0, 0, 1, 0.9)]);
    expect(rectsA.shouldRepaint(rectsA), isFalse);
    expect(rectsA.shouldRepaint(rectsB), isTrue);
  });
}

void _paint(CustomPainter painter) {
  final recorder = PictureRecorder();
  final canvas = Canvas(recorder);
  painter.paint(canvas, const Size(200, 120));
  recorder.endRecording();
}
