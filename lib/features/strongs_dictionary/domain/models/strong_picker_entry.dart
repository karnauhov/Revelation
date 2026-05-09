class StrongPickerEntry {
  const StrongPickerEntry({required this.number, required this.word});

  final int number;
  final String word;

  String get code => 'G$number';

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is StrongPickerEntry &&
            runtimeType == other.runtimeType &&
            number == other.number &&
            word == other.word;
  }

  @override
  int get hashCode => Object.hash(number, word);
}
