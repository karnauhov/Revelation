class PrimarySourcePageSettingsState {
  const PrimarySourcePageSettingsState({
    required this.rawSettings,
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
    required this.showWordSeparators,
    required this.showStrongNumbers,
    required this.showVerseNumbers,
  });

  static const PrimarySourcePageSettingsState defaults =
      PrimarySourcePageSettingsState(
        rawSettings: '',
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      );

  final String rawSettings;
  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;
  final bool showWordSeparators;
  final bool showStrongNumbers;
  final bool showVerseNumbers;

  PrimarySourcePageSettingsState copyWith({
    String? rawSettings,
    bool? isNegative,
    bool? isMonochrome,
    double? brightness,
    double? contrast,
    bool? showWordSeparators,
    bool? showStrongNumbers,
    bool? showVerseNumbers,
  }) {
    return PrimarySourcePageSettingsState(
      rawSettings: rawSettings ?? this.rawSettings,
      isNegative: isNegative ?? this.isNegative,
      isMonochrome: isMonochrome ?? this.isMonochrome,
      brightness: brightness ?? this.brightness,
      contrast: contrast ?? this.contrast,
      showWordSeparators: showWordSeparators ?? this.showWordSeparators,
      showStrongNumbers: showStrongNumbers ?? this.showStrongNumbers,
      showVerseNumbers: showVerseNumbers ?? this.showVerseNumbers,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourcePageSettingsState &&
            runtimeType == other.runtimeType &&
            rawSettings == other.rawSettings &&
            isNegative == other.isNegative &&
            isMonochrome == other.isMonochrome &&
            brightness == other.brightness &&
            contrast == other.contrast &&
            showWordSeparators == other.showWordSeparators &&
            showStrongNumbers == other.showStrongNumbers &&
            showVerseNumbers == other.showVerseNumbers;
  }

  @override
  int get hashCode => Object.hash(
    rawSettings,
    isNegative,
    isMonochrome,
    brightness,
    contrast,
    showWordSeparators,
    showStrongNumbers,
    showVerseNumbers,
  );
}
