@Tags(['widget'])
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_card.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
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
