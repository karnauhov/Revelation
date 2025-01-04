class AppSettings {
  final String selectedLanguage;

  AppSettings({
    required this.selectedLanguage,
  });

  Map<String, dynamic> toMap() {
    return {
      'selectedLanguage': selectedLanguage,
    };
  }

  factory AppSettings.fromMap(Map<String, dynamic> map) {
    return AppSettings(
      selectedLanguage: map['selectedLanguage'] ?? 'en',
    );
  }
}
