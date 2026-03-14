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
}
