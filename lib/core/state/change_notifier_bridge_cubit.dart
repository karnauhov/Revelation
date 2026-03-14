import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class ChangeNotifierBridgeState<T extends ChangeNotifier> {
  const ChangeNotifierBridgeState({
    required this.notifier,
    required this.revision,
  });

  final T notifier;
  final int revision;
}

/// Transitional bridge that mirrors ChangeNotifier updates into Cubit events.
/// Used during phased migration from Provider/ChangeNotifier to BLoC/Cubit.
class ChangeNotifierBridgeCubit<T extends ChangeNotifier>
    extends Cubit<ChangeNotifierBridgeState<T>> {
  ChangeNotifierBridgeCubit(T notifier)
    : _notifier = notifier,
      super(ChangeNotifierBridgeState<T>(notifier: notifier, revision: 0)) {
    _notifier.addListener(_handleNotifierChanged);
  }

  final T _notifier;
  int _revision = 0;

  void _handleNotifierChanged() {
    _revision += 1;
    emit(
      ChangeNotifierBridgeState<T>(notifier: _notifier, revision: _revision),
    );
  }

  @override
  Future<void> close() async {
    _notifier.removeListener(_handleNotifierChanged);
    await super.close();
  }
}
