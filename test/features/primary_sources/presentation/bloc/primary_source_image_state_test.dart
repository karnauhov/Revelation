import 'dart:typed_data';

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

  test('copyWith imageDataSet controls explicit null replacement', () {
    final bytes = Uint8List.fromList(<int>[1, 2, 3]);
    final withImage = PrimarySourceImageState.initial(
      maxTextureSize: 2048,
    ).copyWith(imageDataSet: true, imageData: bytes);

    final unchanged = withImage.copyWith(imageData: null);
    final cleared = withImage.copyWith(imageDataSet: true, imageData: null);

    expect(unchanged.imageData, same(bytes));
    expect(cleared.imageData, isNull);
  });

  test('value equality includes identity of image bytes and metadata', () {
    final bytes = Uint8List.fromList(<int>[9, 9, 9]);
    final equalBytesByContent = Uint8List.fromList(<int>[9, 9, 9]);
    final a = PrimarySourceImageState(
      imageData: bytes,
      isLoading: true,
      refreshError: true,
      localPageLoaded: const <String, bool?>{'a.png': true},
      maxTextureSize: 1024,
    );
    final b = PrimarySourceImageState(
      imageData: bytes,
      isLoading: true,
      refreshError: true,
      localPageLoaded: const <String, bool?>{'a.png': true},
      maxTextureSize: 1024,
    );
    final different = b.copyWith(maxTextureSize: 4096);
    final differentIdentity = b.copyWith(
      imageDataSet: true,
      imageData: equalBytesByContent,
    );

    expect(a, b);
    expect(a.hashCode, isA<int>());
    expect(b.hashCode, isA<int>());
    expect(a, isNot(different));
    expect(a, isNot(differentIdentity));
    expect(a.hashCode, isNot(different.hashCode));
  });
}
