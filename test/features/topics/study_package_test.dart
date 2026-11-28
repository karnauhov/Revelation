@TestOn('vm')
library;

import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';
import 'package:sqlite3/sqlite3.dart';

const _sources = 'docs/ru/content/study/rev-01-01-03';
const _route = 'topic_1';
const _image = 'study/rev-01-01-03/reading.webp';

class _StudyImageLoader implements MarkdownImageLoader {
  @override
  Future<MarkdownImageLoadResult> loadImage(
    MarkdownImageRequest request,
  ) async {
    expect(request.databaseResourceKey, _image);
    final db = sqlite3.open(
      'web/db/revelation.sqlite',
      mode: OpenMode.readOnly,
    );
    try {
      final row = db.select(
        'SELECT data, mime_type FROM common_resources WHERE key = ?',
        [request.databaseResourceKey],
      ).single;
      final bytes = row['data'] as Uint8List;
      expect(
        bytes,
        orderedEquals(File('$_sources/reading.webp').readAsBytesSync()),
      );
      return MarkdownImageLoadResult.success(
        bytes: bytes,
        mimeType: row['mime_type'] as String,
      );
    } finally {
      db.dispose();
    }
  }
}

void main() {
  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets(
      'ships the illustrated introduction and its manuscript study in $language',
      (tester) async {
        final db = sqlite3.open(
          'web/db/revelation_$language.sqlite',
          mode: OpenMode.readOnly,
        );
        addTearDown(db.dispose);
        final row = db.select(
          'SELECT markdown FROM articles WHERE route = ? AND is_visible = 1 AND sort_order = 2',
          [_route],
        ).single;
        final markdown = row['markdown'] as String;
        final source = File(
          '$_sources/$language.md',
        ).readAsStringSync().replaceAll('\r\n', '\n');
        expect(
          markdown,
          source
              .replaceAll('](reading.webp)', '](dbres:$_image)')
              .replaceAll(
                '](ephesus-terrace-house.webp)',
                '](dbres:study/rev-01-01-03/ephesus-terrace-house.webp)',
              ),
        );
        expect(
          db.select(
            "SELECT route FROM articles WHERE route = 'study_rev_1_1_3'",
          ),
          isEmpty,
        );
        final reading = TopicContentState.initial().copyWith(
          markdown: markdown,
        );
        expect(reading.isStudyExpanded, isFalse);
        expect(reading.openingMarkdown, isNot(startsWith('#')));
        expect(reading.openingMarkdown, contains('](dbres:$_image)'));
        expect(reading.openingMarkdown, isNot(contains('](words:')));
        expect(reading.deeperMarkdown, contains('](word:U025)'));
        expect(
          reading.deeperMarkdown,
          contains('](words:U001:325v:2;U002:150r:0;U046;U025)'),
        );
        expect(
          reading.deeperMarkdown,
          contains('](words:U001:325v:55;U002:150r:50;U004:197r:24)'),
        );
        await tester.binding.setSurfaceSize(const Size(390, 800));
        addTearDown(() => tester.binding.setSurfaceSize(null));
        await tester.pumpWidget(
          MaterialApp(
            locale: Locale(language),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: RevelationMarkdownBody(
                  data: reading.openingMarkdown,
                  markdownImageLoader: _StudyImageLoader(),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.byType(Table), findsOneWidget);
        expect(
          find.byWidgetPredicate((w) => w is Image && w.image is MemoryImage),
          findsOneWidget,
        );
        if (language == 'uk') {
          for (final width in [360.0, 960.0]) {
            await tester.binding.setSurfaceSize(Size(width, 800));
            await tester.pumpAndSettle();
            _expectVerseTableFits(tester);
          }
        }
        expect(tester.takeException(), isNull);
      },
    );
  }
}

void _expectVerseTableFits(WidgetTester tester) {
  final table = find.byType(Table);
  final rows = tester.widget<Table>(table).children;
  final verseHeader = find.byWidget(rows.first.children.first);
  expect(
    find.descendant(
      of: verseHeader,
      matching: find.text('Вірш', findRichText: true),
    ),
    findsOneWidget,
  );
  final verseWidth = tester.getSize(verseHeader).width;
  final requiredWidth = rows
      .map((row) {
        final cell = tester.renderObject<RenderBox>(
          find.byWidget(row.children.first),
        );
        return cell.getMaxIntrinsicWidth(double.infinity);
      })
      .reduce((a, b) => a > b ? a : b);
  expect(verseWidth, lessThanOrEqualTo(requiredWidth + 1));
  final textWidth = tester
      .getSize(find.byWidget(rows.first.children.last))
      .width;
  expect(textWidth, greaterThan(verseWidth));

  final viewport = tester.getRect(find.byType(Scaffold));
  final bounds = tester.getRect(table);
  expect(bounds.left, greaterThanOrEqualTo(viewport.left - 1));
  expect(bounds.right, lessThanOrEqualTo(viewport.right + 1));
  final text = find.descendant(of: table, matching: find.byType(RichText));
  for (final paragraph in tester.renderObjectList<RenderParagraph>(text)) {
    expect(paragraph.didExceedMaxLines, isFalse);
  }
}
