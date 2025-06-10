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
}
