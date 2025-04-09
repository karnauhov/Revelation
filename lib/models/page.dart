class Page {
  final String name;
  final String content;
  final String image;

  Page({
    required this.name,
    required this.content,
    required this.image,
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
