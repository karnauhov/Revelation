import 'package:flutter/foundation.dart';

class PrimarySourceImageState {
  PrimarySourceImageState({
    required this.imageData,
    required this.isLoading,
    required this.imageShown,
    required this.refreshError,
    required Map<String, bool?> localPageLoaded,
    required this.maxTextureSize,
  }) : localPageLoaded = Map<String, bool?>.unmodifiable(localPageLoaded);

  factory PrimarySourceImageState.initial({required int maxTextureSize}) {
    return PrimarySourceImageState(
      imageData: null,
      isLoading: false,
      imageShown: false,
      refreshError: false,
      localPageLoaded: const <String, bool?>{},
      maxTextureSize: maxTextureSize,
    );
  }

  final Uint8List? imageData;
  final bool isLoading;
  final bool imageShown;
  final bool refreshError;
  final Map<String, bool?> localPageLoaded;
  final int maxTextureSize;

  PrimarySourceImageState copyWith({
    Uint8List? imageData,
    bool imageDataSet = false,
    bool? isLoading,
    bool? imageShown,
    bool? refreshError,
    Map<String, bool?>? localPageLoaded,
    int? maxTextureSize,
  }) {
    return PrimarySourceImageState(
      imageData: imageDataSet ? imageData : this.imageData,
      isLoading: isLoading ?? this.isLoading,
      imageShown: imageShown ?? this.imageShown,
      refreshError: refreshError ?? this.refreshError,
      localPageLoaded: localPageLoaded ?? this.localPageLoaded,
      maxTextureSize: maxTextureSize ?? this.maxTextureSize,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceImageState &&
            runtimeType == other.runtimeType &&
            identical(imageData, other.imageData) &&
            isLoading == other.isLoading &&
            imageShown == other.imageShown &&
            refreshError == other.refreshError &&
            mapEquals(localPageLoaded, other.localPageLoaded) &&
            maxTextureSize == other.maxTextureSize;
  }

  @override
  int get hashCode => Object.hash(
    imageData,
    isLoading,
    imageShown,
    refreshError,
    Object.hashAllUnordered(localPageLoaded.entries),
    maxTextureSize,
  );
}
