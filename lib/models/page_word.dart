import 'package:revelation/models/page_rect.dart';

class PageWord {
  final String text;
  final List<PageRect> rectangles;
  final List<int> notExist;
  final int? sn;
  final bool snPronounce;
  final double snXshift;

  PageWord(
    this.text,
    this.rectangles, {
    this.notExist = const [],
    this.sn = null,
    this.snPronounce = false,
    this.snXshift = 0,
  });
}
