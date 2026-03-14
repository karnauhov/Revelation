import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/about/about.dart' show AboutScreen;
import 'package:revelation/features/download/download.dart' show DownloadScreen;
import 'package:revelation/features/settings/settings.dart' show SettingsScreen;
import 'package:revelation/features/topics/topics.dart'
    show MainScreen, TopicScreen;
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/detail/primary_source_screen.dart';
import 'package:revelation/features/primary_sources/presentation/list/primary_sources_screen.dart';
import 'package:talker_flutter/talker_flutter.dart';

class AppRouter {
  static final AppRouter _instance = AppRouter._internal();

  factory AppRouter() {
    return _instance;
  }

  AppRouter._internal();

  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  final aud = AudioController();

  late final GoRouter router = GoRouter(
    navigatorKey: navigatorKey,
    routes: [
      GoRoute(
        path: '/',
        name: 'main',
        pageBuilder: (BuildContext context, GoRouterState state) {
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: MainScreen(),
          );
        },
      ),
      GoRoute(
        path: '/topic',
        name: 'topic',
        pageBuilder: (BuildContext context, GoRouterState state) {
          final topicArgs = TopicRouteArgs.tryParse(
            state.extra,
            state.uri.queryParameters,
          );
          if (topicArgs == null) {
            log.error('Please, send it with correct topic route parameters');
            WidgetsBinding.instance.addPostFrameCallback((_) {
              context.go('/');
            });
            return buildPageWithDefaultTransition<void>(
              context: context,
              state: state,
              child: const SizedBox.shrink(),
            );
          }

          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: TopicScreen(
              name: topicArgs.name,
              description: topicArgs.description,
              file: topicArgs.file,
            ),
          );
        },
      ),
      GoRoute(
        path: '/primary_sources',
        name: 'primary_sources',
        pageBuilder: (BuildContext context, GoRouterState state) {
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: PrimarySourcesScreen(),
          );
        },
      ),
      GoRoute(
        path: '/primary_source',
        name: 'primary_source',
        pageBuilder: (BuildContext context, GoRouterState state) {
          final primarySourceArgs = PrimarySourceRouteArgs.tryParse(
            state.extra,
          );
          if (primarySourceArgs == null) {
            log.error('Please, send it with correct primary source parameter');
            WidgetsBinding.instance.addPostFrameCallback((_) {
              context.go('/');
            });
            return buildPageWithDefaultTransition<void>(
              context: context,
              state: state,
              child: const SizedBox.shrink(),
            );
          }
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: PrimarySourceScreen(
              primarySource: primarySourceArgs.primarySource,
              initialPageName: primarySourceArgs.pageName,
              initialWordIndex: primarySourceArgs.wordIndex,
            ),
          );
        },
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        pageBuilder: (BuildContext context, GoRouterState state) {
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: SettingsScreen(),
          );
        },
      ),
      GoRoute(
        path: '/about',
        name: 'about',
        pageBuilder: (BuildContext context, GoRouterState state) {
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: AboutScreen(),
          );
        },
      ),
      GoRoute(
        path: '/download',
        name: 'download',
        pageBuilder: (BuildContext context, GoRouterState state) {
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: DownloadScreen(),
          );
        },
      ),
    ],
    observers: <NavigatorObserver>[TalkerRouteObserver(GetIt.I<Talker>())],
  );
}

CustomTransitionPage buildPageWithDefaultTransition<T>({
  required BuildContext context,
  required GoRouterState state,
  required Widget child,
}) {
  return CustomTransitionPage<T>(
    key: state.pageKey,
    name: state.name,
    arguments: _getRouteArgs(state),
    child: child,
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      return SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(1.0, 0.0),
          end: Offset.zero,
        ).animate(animation),
        child: child,
      );
    },
    transitionDuration: const Duration(milliseconds: 300),
  );
}

String? _getRouteArgs(GoRouterState state) {
  if (state.extra is TopicRouteArgs) {
    return (state.extra as TopicRouteArgs).file;
  }
  if (state.extra is PrimarySourceRouteArgs) {
    return (state.extra as PrimarySourceRouteArgs).primarySource.id;
  }
  return null;
}
