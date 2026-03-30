import 'package:flutter/foundation.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_state.dart';

class RevelationMarkdownImagesState {
  RevelationMarkdownImagesState({
    required this.documentRevision,
    required Map<String, RevelationMarkdownImageState> images,
    required this.totalCount,
    required this.completedCount,
    required this.failedCount,
  }) : images = Map<String, RevelationMarkdownImageState>.unmodifiable(images);

  factory RevelationMarkdownImagesState.initial() {
    return RevelationMarkdownImagesState(
      documentRevision: 0,
      images: const <String, RevelationMarkdownImageState>{},
      totalCount: 0,
      completedCount: 0,
      failedCount: 0,
    );
  }

  final int documentRevision;
  final Map<String, RevelationMarkdownImageState> images;
  final int totalCount;
  final int completedCount;
  final int failedCount;

  bool get hasPreload => totalCount > 0;

  bool get isPreloadActive => completedCount < totalCount;

  double? get preloadProgress =>
      totalCount == 0 ? null : completedCount / totalCount;

  RevelationMarkdownImagesState copyWith({
    int? documentRevision,
    Map<String, RevelationMarkdownImageState>? images,
    int? totalCount,
    int? completedCount,
    int? failedCount,
  }) {
    return RevelationMarkdownImagesState(
      documentRevision: documentRevision ?? this.documentRevision,
      images: images ?? this.images,
      totalCount: totalCount ?? this.totalCount,
      completedCount: completedCount ?? this.completedCount,
      failedCount: failedCount ?? this.failedCount,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is RevelationMarkdownImagesState &&
            runtimeType == other.runtimeType &&
            documentRevision == other.documentRevision &&
            mapEquals(images, other.images) &&
            totalCount == other.totalCount &&
            completedCount == other.completedCount &&
            failedCount == other.failedCount;
  }

  @override
  int get hashCode => Object.hash(
    documentRevision,
    Object.hashAllUnordered(images.entries),
    totalCount,
    completedCount,
    failedCount,
  );
}
