import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/screens/primary_source/primary_source_screen.dart';
import 'package:revelation/screens/primary_sources/primary_sources_screen.dart';
import 'package:revelation/screens/settings/settings_screen.dart';
import 'package:revelation/screens/about/about_screen.dart';
import 'package:revelation/screens/download/download_screen.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'screens/main/main_screen.dart';
import 'screens/topic/topic_screen.dart';

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
          aud.playSound("page");
          return buildPageWithDefaultTransition<void>(
            context: context,
            state: state,
            child: TopicScreen(
              name: (state.extra as Map<String, dynamic>?)?['name'],
              description:
                  (state.extra as Map<String, dynamic>?)?['description'],
              file: (state.extra as Map<String, dynamic>?)?['file'],
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
          PrimarySource? primarySource;
          String? initialPageName;
          int? initialWordIndex;

          if (state.extra is PrimarySource) {
            primarySource = state.extra as PrimarySource;
          } else if (state.extra is Map<String, dynamic>) {
            final extra = state.extra as Map<String, dynamic>;
            if (extra['primarySource'] is PrimarySource) {
              primarySource = extra['primarySource'] as PrimarySource;
            }
            if (extra['pageName'] is String) {
              initialPageName = extra['pageName'] as String;
            }
            final rawWordIndex = extra['wordIndex'];
            if (rawWordIndex is int) {
              initialWordIndex = rawWordIndex;
            } else if (rawWordIndex is String) {
              initialWordIndex = int.tryParse(rawWordIndex);
            }
          }

          if (primarySource == null) {
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
              primarySource: primarySource,
              initialPageName: initialPageName,
              initialWordIndex: initialWordIndex,
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
  if (state.extra is Map<String, dynamic>) {
    final extra = state.extra as Map<String, dynamic>;
    if (extra['primarySource'] is PrimarySource) {
      return (extra['primarySource'] as PrimarySource).id;
    }
    return extra['file'];
  } else if (state.extra is PrimarySource) {
    return (state.extra as PrimarySource).id;
  }
  return null;
}
