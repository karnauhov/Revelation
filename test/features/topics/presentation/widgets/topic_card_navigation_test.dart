@Tags(['widget'])
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_card.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
  testWidgets('TopicCard renders fallback icon when icon resource is absent', (
    tester,
  ) async {
    final topic = TopicInfo(
      name: 'Fallback Topic',
      idIcon: 'fallback',
      description: 'Fallback description',
      route: 'fallback-route',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: TopicCard(topic: topic, iconResource: null)),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Fallback Topic'), findsOneWidget);
    expect(find.text('Fallback description'), findsOneWidget);
    expect(find.byType(SvgPicture), findsOneWidget);
  });

  testWidgets(
    'TopicCard treats svg extension as vector icon even with generic mime type',
    (tester) async {
      final topic = TopicInfo(
        name: 'SVG Topic',
        idIcon: 'svg-topic',
        description: 'SVG description',
        route: 'svg-route',
      );
      final icon = TopicResource(
        fileName: 'icon.svg',
        mimeType: 'application/octet-stream',
        data: Uint8List.fromList(
          utf8.encode('<svg xmlns="http://www.w3.org/2000/svg"></svg>'),
        ),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TopicCard(topic: topic, iconResource: icon),
          ),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(SvgPicture), findsOneWidget);
      expect(find.byType(Image), findsNothing);
    },
  );

  testWidgets('TopicCard renders raster icon from bytes for non-svg mime', (
    tester,
  ) async {
    final topic = TopicInfo(
      name: 'Raster Topic',
      idIcon: 'raster-topic',
      description: 'Raster description',
      route: 'raster-route',
    );
    final icon = TopicResource(
      fileName: 'icon.png',
      mimeType: 'image/png',
      data: Uint8List.fromList(_singlePixelPng),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TopicCard(topic: topic, iconResource: icon),
        ),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(Image), findsOneWidget);
  });

  testWidgets('TopicCard falls back to default icon when raster decode fails', (
    tester,
  ) async {
    final topic = TopicInfo(
      name: 'Broken Topic',
      idIcon: 'broken-topic',
      description: 'Broken description',
      route: 'broken-route',
    );
    final icon = TopicResource(
      fileName: 'broken.png',
      mimeType: 'image/png',
      data: Uint8List.fromList(const <int>[1, 2, 3, 4]),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TopicCard(topic: topic, iconResource: icon),
        ),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(SvgPicture), findsOneWidget);
  });

  testWidgets('TopicCard navigates to topic route with args', (tester) async {
    final topic = TopicInfo(
      name: 'Topic',
      idIcon: 'topic-icon',
      description: 'Description',
      route: 'topic-route',
    );
    final icon = TopicResource(
      fileName: 'topic.svg',
      mimeType: 'image/svg+xml',
      data: Uint8List.fromList(
        utf8.encode('<svg xmlns="http://www.w3.org/2000/svg"></svg>'),
      ),
    );
    TopicRouteArgs? captured;

    final router = GoRouter(
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => Scaffold(
            body: TopicCard(topic: topic, iconResource: icon),
          ),
        ),
        GoRoute(
          path: '/topic',
          builder: (context, state) {
            captured = state.extra as TopicRouteArgs?;
            return const Scaffold(body: Text('topic-route'));
          },
        ),
      ],
    );

    await tester.pumpWidget(_buildRouterApp(router));
    await tester.pumpAndSettle();

    await tester.tap(find.byType(TopicCard));
    await tester.pumpAndSettle();

    expect(find.text('topic-route'), findsOneWidget);
    expect(captured?.file, 'topic-route');
    expect(captured?.name, 'Topic');
    expect(captured?.description, 'Description');
  });
}

Widget _buildRouterApp(GoRouter router) {
  return MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
  );
}

const List<int> _singlePixelPng = <int>[
  137,
  80,
  78,
  71,
  13,
  10,
  26,
  10,
  0,
  0,
  0,
  13,
  73,
  72,
  68,
  82,
  0,
  0,
  0,
  1,
  0,
  0,
  0,
  1,
  8,
  4,
  0,
  0,
  0,
  181,
  28,
  12,
  2,
  0,
  0,
  0,
  11,
  73,
  68,
  65,
  84,
  120,
  156,
  99,
  96,
  96,
  0,
  0,
  0,
  3,
  0,
  1,
  104,
  38,
  89,
  13,
  0,
  0,
  0,
  0,
  73,
  69,
  78,
  68,
  174,
  66,
  96,
  130,
];
