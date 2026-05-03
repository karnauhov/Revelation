import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:talker_flutter/talker_flutter.dart';

/// Centralized BLoC runtime observer:
/// - logs lifecycle and state transitions (debug mode by default),
/// - always reports BLoC/Cubit errors with stack traces.
class AppBlocObserver extends BlocObserver {
  AppBlocObserver({
    required Talker talker,
    AppAnalyticsReporter? analyticsReporter,
    bool logTransitions = kDebugMode,
  }) : _talker = talker,
       _analyticsReporter =
           analyticsReporter ?? const NoopAppAnalyticsReporter(),
       _logTransitions = logTransitions;

  final Talker _talker;
  final AppAnalyticsReporter _analyticsReporter;
  final bool _logTransitions;

  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    if (_logTransitions) {
      _talker.debug('[BLoC] create ${bloc.runtimeType}');
    }
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    if (_logTransitions) {
      _talker.debug('[BLoC] event ${bloc.runtimeType}: $event');
    }
    super.onEvent(bloc, event);
  }

  @override
  void onChange(BlocBase bloc, Change change) {
    // For Bloc, transition-level logging is handled by onTransition.
    if (_logTransitions && bloc is! Bloc) {
      _talker.debug(
        '[BLoC] change ${bloc.runtimeType}: ${change.currentState} -> ${change.nextState}',
      );
    }
    super.onChange(bloc, change);
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    if (_logTransitions) {
      _talker.debug(
        '[BLoC] transition ${bloc.runtimeType}: ${transition.currentState} --(${transition.event})-> ${transition.nextState}',
      );
    }
    super.onTransition(bloc, transition);
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    final source = '[BLoC] error in ${bloc.runtimeType}';
    _talker.handle(error, stackTrace, source);
    unawaited(
      _analyticsReporter
          .captureException(error, stackTrace, source: source, fatal: false)
          .catchError((Object analyticsError, StackTrace analyticsStackTrace) {
            _talker.handle(
              analyticsError,
              analyticsStackTrace,
              'Failed to report BLoC error to analytics',
            );
          }),
    );
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onClose(BlocBase bloc) {
    if (_logTransitions) {
      _talker.debug('[BLoC] close ${bloc.runtimeType}');
    }
    super.onClose(bloc);
  }
}
