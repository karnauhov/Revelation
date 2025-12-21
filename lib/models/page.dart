import 'package:revelation/models/page_line.dart';

import 'page_text.dart';

class Page {
  final String name;
  final String content;
  final String image;
  final List<PageLine> wordSeparators;
  final List<PageText> strongNumbers;

  Page({
    required this.name,
    required this.content,
    required this.image,
    this.wordSeparators = const [],
    this.strongNumbers = const [],
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Page &&
          runtimeType == other.runtimeType &&
          name == other.name &&
          content == other.content &&
          image == other.image;

  @override
  int get hashCode => name.hashCode ^ content.hashCode ^ image.hashCode;
}
