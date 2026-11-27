typedef BibleBookmarkLocation = ({int bookId, int chapter, int verse});

enum BibleBookmarkColor { blue, green, amber, red, violet }

class BibleBookmark {
  const BibleBookmark({
    required this.id,
    required this.location,
    required this.name,
    required this.color,
  });

  final String id;
  final BibleBookmarkLocation location;
  final String name;
  final BibleBookmarkColor color;

  @override
  bool operator ==(Object other) =>
      other is BibleBookmark &&
      id == other.id &&
      location == other.location &&
      name == other.name &&
      color == other.color;

  @override
  int get hashCode => Object.hash(id, location, name, color);
}
