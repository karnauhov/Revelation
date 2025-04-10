import 'package:revelation/models/page.dart';

class PrimarySource {
  final String title;
  final String date;
  final String content;
  final int quantity;
  final String material;
  final String textStyle;
  final String found;
  final String classification;
  final String currentLocation;
  final String link1Title;
  final String link1Url;
  final String link2Title;
  final String link2Url;
  final String preview;
  final double maxScale;
  final List<Page> pages;
  bool showMore = false;

  PrimarySource(
      {required this.title,
      required this.date,
      required this.content,
      required this.quantity,
      required this.material,
      required this.textStyle,
      required this.found,
      required this.classification,
      required this.currentLocation,
      required this.link1Title,
      required this.link1Url,
      required this.link2Title,
      required this.link2Url,
      required this.preview,
      required this.maxScale,
      required this.pages});
}
