import 'package:flutter/widgets.dart';
import 'package:revelation/core/audio/audio_controller.dart';

typedef RouteSoundPlayer = void Function(String sourceName);

class RouteSoundObserver extends NavigatorObserver {
  RouteSoundObserver({RouteSoundPlayer? playSound})
    : _playSound = playSound ?? AudioController().playSound;

  final RouteSoundPlayer _playSound;

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    _playFor(route);
    super.didPush(route, previousRoute);
  }

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    if (newRoute != null) {
      _playFor(newRoute);
    }
    super.didReplace(newRoute: newRoute, oldRoute: oldRoute);
  }

  void _playFor(Route<dynamic> route) {
    final routeName = route.settings.name;
    if (routeName == null || routeName.isEmpty) {
      return;
    }
    _playSound('page');
  }
}
