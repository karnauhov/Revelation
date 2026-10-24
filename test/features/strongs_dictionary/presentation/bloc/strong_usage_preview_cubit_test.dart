import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_text_provider.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strong_usage_preview_cubit.dart';

void main() {
  test(
    'rapid requests share loading and copying; later requests reuse text',
    () async {
      final loaded = Completer<String?>();
      final copied = Completer<void>();
      final provider = _Provider(() => loaded.future);
      var copyCalls = 0;
      final cubit = StrongUsagePreviewCubit(
        verseKey: '001',
        textProvider: provider,
        copyText: (text) async {
          expect(text, 'verse');
          copyCalls++;
          await copied.future;
        },
      );
      addTearDown(cubit.close);

      final first = cubit.requestPreview();
      final second = cubit.requestPreview();
      expect(provider.calls, 1);
      loaded.complete(' verse ');
      await Future<void>.delayed(Duration.zero);
      final third = cubit.requestPreview();
      expect(copyCalls, 1);
      expect(cubit.state.requestId, 0);
      copied.complete();
      await Future.wait([first, second, third]);
      expect(cubit.state.requestId, 1);

      await cubit.requestPreview();
      expect(provider.calls, 1);
      expect(copyCalls, 2);
      expect(cubit.state.requestId, 2);
    },
  );

  test(
    'closing during loading discards the stale result and skips copying',
    () async {
      final loaded = Completer<String?>();
      var copyCalls = 0;
      final cubit = StrongUsagePreviewCubit(
        verseKey: '001',
        textProvider: _Provider(() => loaded.future),
        copyText: (_) async {
          copyCalls++;
        },
      );
      final pending = cubit.requestPreview();
      await cubit.close();
      loaded.complete('stale');
      await pending;
      expect(copyCalls, 0);
      expect(cubit.state.requestId, 0);
    },
  );

  test('closing during copying prevents a late presentation request', () async {
    final copied = Completer<void>();
    final cubit = StrongUsagePreviewCubit(
      verseKey: '001',
      textProvider: _Provider(() async => 'verse'),
      copyText: (_) => copied.future,
    );
    final pending = cubit.requestPreview();
    await Future<void>.delayed(Duration.zero);
    await cubit.close();
    copied.complete();
    await pending;
    expect(cubit.state.requestId, 0);
  });

  test('load failures show unavailable without copying', () async {
    final cubit = StrongUsagePreviewCubit(
      verseKey: '001',
      textProvider: _Provider(() async => throw StateError('load failed')),
      copyText: (_) async => fail('unavailable text must not be copied'),
    );
    addTearDown(cubit.close);
    await cubit.requestPreview();
    expect(
      cubit.state,
      const StrongUsagePreviewState(
        status: StrongUsagePreviewStatus.unavailable,
        requestId: 1,
      ),
    );
  });

  test('copy failures still request the loaded preview', () async {
    final cubit = StrongUsagePreviewCubit(
      verseKey: '001',
      textProvider: _Provider(() async => 'verse'),
      copyText: (_) async => throw StateError('copy failed'),
    );
    addTearDown(cubit.close);
    await cubit.requestPreview();
    expect(
      cubit.state,
      const StrongUsagePreviewState(
        status: StrongUsagePreviewStatus.ready,
        text: 'verse',
        requestId: 1,
      ),
    );
  });
}

class _Provider implements StrongUsageBibleTextProvider {
  _Provider(this.load);
  final Future<String?> Function() load;
  int calls = 0;

  @override
  Future<String?> loadVerseText(String verseKey) {
    calls++;
    return load();
  }
}
