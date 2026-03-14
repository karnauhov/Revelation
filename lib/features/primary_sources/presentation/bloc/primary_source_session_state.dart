import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

class PrimarySourceSessionState {
  const PrimarySourceSessionState({
    required this.source,
    required this.selectedPage,
    required this.imageName,
    required this.isMenuOpen,
  });

  factory PrimarySourceSessionState.initial({required PrimarySource source}) {
    final model.Page? initialPage =
        source.permissionsReceived && source.pages.isNotEmpty
        ? source.pages.first
        : null;
    return PrimarySourceSessionState(
      source: source,
      selectedPage: initialPage,
      imageName: '',
      isMenuOpen: false,
    );
  }

  final PrimarySource source;
  final model.Page? selectedPage;
  final String imageName;
  final bool isMenuOpen;

  PrimarySourceSessionState copyWith({
    PrimarySource? source,
    model.Page? selectedPage,
    bool selectedPageSet = false,
    String? imageName,
    bool? isMenuOpen,
  }) {
    return PrimarySourceSessionState(
      source: source ?? this.source,
      selectedPage: selectedPageSet ? selectedPage : this.selectedPage,
      imageName: imageName ?? this.imageName,
      isMenuOpen: isMenuOpen ?? this.isMenuOpen,
    );
  }
}
