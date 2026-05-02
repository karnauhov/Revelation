import 'package:flutter/foundation.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';

enum PrimarySourceWordImagesStatus { loading, loaded }

class PrimarySourceWordImagesState {
  PrimarySourceWordImagesState({
    required this.status,
    required List<PrimarySourceWordImageResult> items,
    this.sharedWordDetailsMarkdown,
  }) : items = List<PrimarySourceWordImageResult>.unmodifiable(items);

  factory PrimarySourceWordImagesState.loading({
    List<PrimarySourceWordImageResult> items =
        const <PrimarySourceWordImageResult>[],
    String? sharedWordDetailsMarkdown,
  }) {
    return PrimarySourceWordImagesState(
      status: PrimarySourceWordImagesStatus.loading,
      items: items,
      sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
    );
  }

  PrimarySourceWordImagesState.loaded({
    required List<PrimarySourceWordImageResult> items,
    String? sharedWordDetailsMarkdown,
  }) : this(
         status: PrimarySourceWordImagesStatus.loaded,
         items: items,
         sharedWordDetailsMarkdown: sharedWordDetailsMarkdown,
       );

  final PrimarySourceWordImagesStatus status;
  final List<PrimarySourceWordImageResult> items;
  final String? sharedWordDetailsMarkdown;

  bool get isLoading => status == PrimarySourceWordImagesStatus.loading;
  bool get hasPendingItems => items.any((item) => item.isLoading);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceWordImagesState &&
            runtimeType == other.runtimeType &&
            status == other.status &&
            sharedWordDetailsMarkdown == other.sharedWordDetailsMarkdown &&
            listEquals(items, other.items);
  }

  @override
  int get hashCode =>
      Object.hash(status, sharedWordDetailsMarkdown, Object.hashAll(items));
}
