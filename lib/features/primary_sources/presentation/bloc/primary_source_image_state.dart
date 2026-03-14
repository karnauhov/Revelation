import 'dart:typed_data';

class PrimarySourceImageState {
  const PrimarySourceImageState({
    required this.imageData,
    required this.isLoading,
    required this.imageShown,
    required this.refreshError,
    required this.localPageLoaded,
    required this.maxTextureSize,
  });

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
}
