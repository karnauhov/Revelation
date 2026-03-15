import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/logging/app_bloc_observer.dart';
import 'package:talker_flutter/talker_flutter.dart';

class _TestCubit extends Cubit<int> {
  _TestCubit() : super(0);

  void increment() => emit(state + 1);
}

class _FailingCubit extends Cubit<int> {
  _FailingCubit() : super(0);

  void explode() {
    addError(StateError('boom'), StackTrace.current);
  }
}

class _IncrementEvent {
  const _IncrementEvent(this.delta);
  final int delta;

  @override
  String toString() => 'Increment($delta)';
}

class _TestBloc extends Bloc<_IncrementEvent, int> {
  _TestBloc() : super(0) {
    on<_IncrementEvent>((event, emit) => emit(state + event.delta));
  }
}

void main() {
  group('AppBlocObserver', () {
    late Talker talker;
    late StreamSubscription<TalkerData> subscription;
    late List<TalkerData> events;
    late BlocObserver previousObserver;

    setUp(() {
      previousObserver = Bloc.observer;
      talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      events = <TalkerData>[];
      subscription = talker.stream.listen(events.add);
    });

    tearDown(() async {
      Bloc.observer = previousObserver;
      await subscription.cancel();
    });

    test('logs lifecycle and transitions when enabled', () async {
      Bloc.observer = AppBlocObserver(talker: talker, logTransitions: true);

      final cubit = _TestCubit();
      cubit.increment();
      await cubit.close();

      final bloc = _TestBloc();
      bloc.add(const _IncrementEvent(2));
      await bloc.stream.first;
      await bloc.close();

      final messages = events
          .whereType<TalkerLog>()
          .map((log) => log.message)
          .whereType<String>()
          .toList();

      expect(
        messages,
        containsAll(<String>[
          '[BLoC] create _TestCubit',
          '[BLoC] change _TestCubit: 0 -> 1',
          '[BLoC] close _TestCubit',
          '[BLoC] create _TestBloc',
          '[BLoC] event _TestBloc: Increment(2)',
          '[BLoC] transition _TestBloc: 0 --(Increment(2))-> 2',
          '[BLoC] close _TestBloc',
        ]),
      );
    });

    test(
      'suppresses transition logs when disabled but still handles errors',
      () async {
        Bloc.observer = AppBlocObserver(talker: talker, logTransitions: false);

        final cubit = _FailingCubit();
        cubit.explode();
        await cubit.close();

        final logs = events.whereType<TalkerLog>().toList();
        final errors = events
            .whereType<TalkerError>()
            .cast<TalkerData>()
            .toList();
        final exceptions = events
            .whereType<TalkerException>()
            .cast<TalkerData>()
            .toList();

        expect(logs, isEmpty);
        expect(
          [...errors, ...exceptions].any(
            (event) =>
                (event.message ?? '').contains('[BLoC] error in _FailingCubit'),
          ),
          isTrue,
        );
      },
    );
  });
}
