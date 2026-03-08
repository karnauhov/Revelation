import 'package:revelation/shared/models/description_kind.dart';

class DescriptionContent {
  final String markdown;
  final DescriptionKind kind;

  const DescriptionContent({required this.markdown, required this.kind});
}
