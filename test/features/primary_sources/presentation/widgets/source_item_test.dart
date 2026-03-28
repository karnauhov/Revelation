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
    expect(
      find.textContaining('[${l10n.wikipedia}]', findRichText: true),
      findsOneWidget,
    );
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
    attributes: const [],
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
