class StrongDictionaryEntry {
  const StrongDictionaryEntry({
    required this.number,
    required this.word,
    required this.category,
    required this.synonyms,
    required this.origin,
    required this.usage,
    required this.description,
  });

  final int number;
  final String word;
  final String category;
  final String synonyms;
  final String origin;
  final String usage;
  final String description;

  String get code => 'G$number';

  bool get hasDisplayWord => word.trim().isNotEmpty;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is StrongDictionaryEntry &&
            runtimeType == other.runtimeType &&
            number == other.number &&
            word == other.word &&
            category == other.category &&
            synonyms == other.synonyms &&
            origin == other.origin &&
            usage == other.usage &&
            description == other.description;
  }

  @override
  int get hashCode =>
      Object.hash(number, word, category, synonyms, origin, usage, description);
}
