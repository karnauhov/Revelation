class GreekStrongPickerEntry {
  final int number;
  final String word;

  const GreekStrongPickerEntry({required this.number, required this.word});

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is GreekStrongPickerEntry &&
            runtimeType == other.runtimeType &&
            number == other.number &&
            word == other.word;
  }

  @override
  int get hashCode => Object.hash(number, word);
}
