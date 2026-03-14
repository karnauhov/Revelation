import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_state.dart';

void main() {
  test('constructor stores immutable copy of localPageLoaded', () {
    final sourceMap = <String, bool?>{'p1.png': true};

    final state = PrimarySourceImageState(
      imageData: null,
      isLoading: false,
      refreshError: false,
      localPageLoaded: sourceMap,
      maxTextureSize: 4096,
    );

    sourceMap.clear();

    expect(state.localPageLoaded['p1.png'], isTrue);
    expect(
      () => state.localPageLoaded['p2.png'] = false,
      throwsUnsupportedError,
    );
  });

  test('copyWith keeps localPageLoaded immutable', () {
    final initial = PrimarySourceImageState.initial(maxTextureSize: 4096);
    final nextMap = <String, bool?>{'p2.png': false};

    final updated = initial.copyWith(localPageLoaded: nextMap);
    nextMap['p2.png'] = true;

    expect(updated.localPageLoaded['p2.png'], isFalse);
    expect(
      () => updated.localPageLoaded['p3.png'] = true,
      throwsUnsupportedError,
    );
  });
}
