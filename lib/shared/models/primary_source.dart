import 'dart:typed_data';

import 'package:revelation/shared/models/page.dart';
import 'package:revelation/shared/models/primary_source_link_info.dart';

class PrimarySource {
  final String id;
  final String title;
  final String date;
  final String content;
  final int quantity;
  final String material;
  final String textStyle;
  final String found;
  final String classification;
  final String currentLocation;
  final String preview;
  final Uint8List? previewBytes;
  final double maxScale;
  final bool isMonochrome;
  final List<Page> pages;
  final List<PrimarySourceLinkInfo> links;
  final List<Map<String, String>>? attributes;
  final bool permissionsReceived;

  PrimarySource({
    required this.id,
    required this.title,
    required this.date,
    required this.content,
    required this.quantity,
    required this.material,
    required this.textStyle,
    required this.found,
    required this.classification,
    required this.currentLocation,
    required this.preview,
    this.previewBytes,
    required this.maxScale,
    required this.isMonochrome,
    required this.pages,
    this.links = const [],
    required this.attributes,
    required this.permissionsReceived,
  });
}
