@Tags(['widget'])
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/source_item.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/primary_source_link_info.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('show-more toggle calls callback and reveals extra metadata', (
    tester,
  ) async {
    var toggleCalls = 0;
    final source = _buildSource(
      links: const [
        PrimarySourceLinkInfo(
          role: 'wikipedia',
          url: 'https://example.com/wiki',
          titleOverride: '',
        ),
      ],
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: SourceItemWidget(
          source: source,
          showMore: false,
          onToggleShowMore: () {
            toggleCalls++;
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(SourceItemWidget));
    final l10n = AppLocalizations.of(context)!;

    expect(
      find.text('(${l10n.show_more})', findRichText: true),
      findsOneWidget,
    );
    expect(find.textContaining(source.material), findsNothing);
    expect(find.text('Collection credit', findRichText: true), findsNothing);
    expect(
      find.textContaining(
        '${l10n.source_date}: ${source.date}',
        findRichText: true,
      ),
      findsOneWidget,
    );
    final open = find.text('[${l10n.open_primary_source}]');
    expect(open, findsNothing);

    await tester.tap(find.text('(${l10n.show_more})', findRichText: true));
    await tester.pump();
    expect(toggleCalls, 1);

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: SourceItemWidget(
          source: source,
          showMore: true,
          onToggleShowMore: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining(source.material), findsOneWidget);
    expect(find.textContaining(source.textStyle), findsOneWidget);
    expect(find.textContaining(source.classification), findsOneWidget);
    expect(find.textContaining(source.found), findsOneWidget);
    expect(find.textContaining(source.currentLocation), findsOneWidget);
    expect(open, findsOneWidget);
    expect(
      find.textContaining('[${l10n.wikipedia}]', findRichText: true),
      findsOneWidget,
    );
    final links = tester.widget<Text>(
      find.ancestor(
        of: open,
        matching: find.byWidgetPredicate(
          (widget) => widget is Text && widget.textSpan != null,
        ),
      ),
    );
    final linksText = links.textSpan! as TextSpan;
    final spans = linksText.children!;
    expect(spans.first.toPlainText(), '${l10n.primary_source_links}:');
    expect(spans.first.style?.fontWeight, FontWeight.bold);
    expect(spans.whereType<WidgetSpan>(), hasLength(1));
    expect(spans.last.toPlainText(), ', [${l10n.wikipedia}]');
    expect(spans.last.style?.fontWeight, isNot(FontWeight.bold));
  });

  testWidgets('only the localized field labels use bold in both card states', (
    tester,
  ) async {
    final source = _buildSource();
    for (final locale in AppLocalizations.supportedLocales) {
      for (final expanded in [false, true]) {
        await tester.pumpWidget(
          buildLocalizedTestApp(
            locale: locale,
            child: SourceItemWidget(
              source: source,
              showMore: expanded,
              onToggleShowMore: () {},
            ),
          ),
        );
        await tester.pumpAndSettle();
        final l10n = AppLocalizations.of(
          tester.element(find.byType(SourceItemWidget)),
        )!;
        final labels = [
          l10n.source_date,
          l10n.source_contents,
          if (expanded) ...[
            l10n.source_material,
            l10n.source_script,
            l10n.source_classification,
            l10n.source_discovery,
            l10n.source_location,
            l10n.primary_source_links,
          ],
        ];
        for (final label in labels) {
          final row = tester.widget<RichText>(
            find.byWidgetPredicate(
              (w) =>
                  w is RichText && w.text.toPlainText().startsWith('$label: '),
            ),
          );
          final prefix = row.text.getSpanForPosition(
            const TextPosition(offset: 0, affinity: TextAffinity.downstream),
          );
          expect(prefix?.toPlainText(), '$label:');
          expect(prefix?.style?.fontWeight, FontWeight.bold);
          expect(row.text.style?.fontWeight, isNot(FontWeight.bold));
          final value = row.text.getSpanForPosition(
            TextPosition(
              offset: label.length + 1,
              affinity: TextAffinity.downstream,
            ),
          );
          expect(value?.style?.fontWeight, isNot(FontWeight.bold));
        }
      }
    }
  });

  testWidgets(
    'fallback preview renders unsupported icon when no bytes and no asset',
    (tester) async {
      final source = _buildSource(
        preview: 'remote_key',
        includePreviewBytes: false,
      );

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: SourceItemWidget(
            source: source,
            showMore: false,
            onToggleShowMore: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    },
  );
}

PrimarySource _buildSource({
  String preview = '',
  bool includePreviewBytes = true,
  List<PrimarySourceLinkInfo> links = const [],
}) {
  return PrimarySource(
    id: 'source-1',
    title: 'Title',
    date: 'Date',
    content: 'Content',
    quantity: 1,
    material: 'Material',
    textStyle: 'TextStyle',
    found: 'Found',
    classification: 'Classification',
    currentLocation: 'Location',
    preview: preview,
    previewBytes: includePreviewBytes ? _loadPreviewBytes() : null,
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    links: links,
    attributes: const [
      {'text': 'Collection credit', 'url': ''},
    ],
    permissionsReceived: false,
  );
}

Uint8List _loadPreviewBytes() {
  return Uint8List.fromList(<int>[
    0x89,
    0x50,
    0x4E,
    0x47,
    0x0D,
    0x0A,
    0x1A,
    0x0A,
    0x00,
    0x00,
    0x00,
    0x0D,
    0x49,
    0x48,
    0x44,
    0x52,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x01,
    0x08,
    0x06,
    0x00,
    0x00,
    0x00,
    0x1F,
    0x15,
    0xC4,
    0x89,
    0x00,
    0x00,
    0x00,
    0x0A,
    0x49,
    0x44,
    0x41,
    0x54,
    0x78,
    0x9C,
    0x63,
    0x00,
    0x01,
    0x00,
    0x00,
    0x05,
    0x00,
    0x01,
    0x0D,
    0x0A,
    0x2D,
    0xB4,
    0x00,
    0x00,
    0x00,
    0x00,
    0x49,
    0x45,
    0x4E,
    0x44,
    0xAE,
    0x42,
    0x60,
    0x82,
  ]);
}
