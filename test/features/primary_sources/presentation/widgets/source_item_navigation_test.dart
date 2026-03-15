@Tags(['widget'])

import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/source_item.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  testWidgets('SourceItemWidget navigates to primary source route', (
    tester,
  ) async {
    final source = PrimarySource(
      id: 'source-1',
      title: 'Title',
      date: 'Date',
      content: 'Content',
      quantity: 1,
      material: 'Material',
      textStyle: 'Style',
      found: 'Found',
      classification: 'Class',
      currentLocation: 'Location',
      preview: '',
      previewBytes: _loadPreviewBytes(),
      maxScale: 1,
      isMonochrome: false,
      pages: const [],
      attributes: const [],
      permissionsReceived: false,
    );
    PrimarySourceRouteArgs? captured;

    final router = GoRouter(
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => Scaffold(
            body: SourceItemWidget(
              source: source,
              showMore: false,
              onToggleShowMore: () {},
            ),
          ),
        ),
        GoRoute(
          path: '/primary_source',
          builder: (context, state) {
            captured = state.extra as PrimarySourceRouteArgs?;
            return const Scaffold(body: Text('primary-source-route'));
          },
        ),
      ],
    );

    await tester.pumpWidget(_buildRouterApp(router));
    await tester.pumpAndSettle();

    await tester.tap(find.byType(ElevatedButton));
    await tester.pumpAndSettle();

    expect(find.text('primary-source-route'), findsOneWidget);
    expect(captured?.primarySource.id, 'source-1');
  });
}

Uint8List _loadPreviewBytes() {
  // 1x1 transparent PNG to avoid asset dependency in widget tests.
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

Widget _buildRouterApp(GoRouter router) {
  return MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
  );
}
