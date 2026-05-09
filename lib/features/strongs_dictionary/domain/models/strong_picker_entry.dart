class StrongPickerEntry {
  const StrongPickerEntry({
    required this.number,
    required this.word,
    this.description = '',
    this.searchText = '',
  });

  final int number;
  final String word;
  final String description;
  final String searchText;

  String get code => 'G$number';

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is StrongPickerEntry &&
            runtimeType == other.runtimeType &&
            number == other.number &&
            word == other.word &&
            description == other.description &&
            searchText == other.searchText;
  }

  @override
  int get hashCode => Object.hash(number, word, description, searchText);
}
