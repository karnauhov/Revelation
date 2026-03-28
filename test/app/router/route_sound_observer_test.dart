import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/app/router/route_sound_observer.dart';

void main() {
  test('RouteSoundObserver plays page sound for named pushed routes', () {
    final playedSources = <String>[];
    final observer = RouteSoundObserver(playSound: playedSources.add);

    observer.didPush(_route(name: 'about'), null);

    expect(playedSources, ['page']);
  });

  test('RouteSoundObserver ignores unnamed pushed routes', () {
    final playedSources = <String>[];
    final observer = RouteSoundObserver(playSound: playedSources.add);

    observer.didPush(_route(), null);

    expect(playedSources, isEmpty);
  });

  test('RouteSoundObserver plays page sound for named replacements', () {
    final playedSources = <String>[];
    final observer = RouteSoundObserver(playSound: playedSources.add);

    observer.didReplace(newRoute: _route(name: 'settings'));

    expect(playedSources, ['page']);
  });
}

PageRoute<void> _route({String? name}) {
  return PageRouteBuilder<void>(
    settings: RouteSettings(name: name),
    pageBuilder: (_, _, _) => const SizedBox.shrink(),
  );
}
