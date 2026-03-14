class AppSettings {
  final String selectedLanguage;
  final String selectedTheme;
  final String selectedFontSize;
  final bool soundEnabled;

  AppSettings({
    required this.selectedLanguage,
    required this.selectedTheme,
    required this.selectedFontSize,
    required this.soundEnabled,
  });

  Map<String, dynamic> toMap() {
    return {
      'selectedLanguage': selectedLanguage,
      'selectedTheme': selectedTheme,
      'selectedFontSize': selectedFontSize,
      'soundEnabled': soundEnabled,
    };
  }

  factory AppSettings.fromMap(Map<String, dynamic> map) {
    return AppSettings(
      selectedLanguage: map['selectedLanguage'] ?? 'en',
      selectedTheme: map['selectedTheme'] ?? 'manuscript',
      selectedFontSize: map['selectedFontSize'] ?? 'medium',
      soundEnabled: map['soundEnabled'] ?? true,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AppSettings &&
            runtimeType == other.runtimeType &&
            selectedLanguage == other.selectedLanguage &&
            selectedTheme == other.selectedTheme &&
            selectedFontSize == other.selectedFontSize &&
            soundEnabled == other.soundEnabled;
  }

  @override
  int get hashCode => Object.hash(
    selectedLanguage,
    selectedTheme,
    selectedFontSize,
    soundEnabled,
  );
}
