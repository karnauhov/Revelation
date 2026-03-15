import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test('fromMap fills defaults for missing values', () {
    final settings = AppSettings.fromMap({'selectedLanguage': 'es'});

    expect(settings.selectedLanguage, 'es');
    expect(settings.selectedTheme, 'manuscript');
    expect(settings.selectedFontSize, 'medium');
    expect(settings.soundEnabled, isTrue);
  });

  test('toMap round-trips with fromMap', () {
    final settings = AppSettings(
      selectedLanguage: 'ru',
      selectedTheme: 'sky',
      selectedFontSize: 'small',
      soundEnabled: false,
    );

    final restored = AppSettings.fromMap(settings.toMap());

    expect(restored, settings);
  });
}
