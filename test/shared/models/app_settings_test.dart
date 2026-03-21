import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  final baseSettings = AppSettings(
    selectedLanguage: 'ru',
    selectedTheme: 'sky',
    selectedFontSize: 'small',
    soundEnabled: false,
  );

  test('fromMap fills defaults for missing values', () {
    final settings = AppSettings.fromMap({'selectedLanguage': 'es'});

    expect(settings.selectedLanguage, 'es');
    expect(settings.selectedTheme, 'manuscript');
    expect(settings.selectedFontSize, 'medium');
    expect(settings.soundEnabled, isTrue);
  });

  test('fromMap falls back to defaults when values are null', () {
    final settings = AppSettings.fromMap(<String, dynamic>{
      'selectedLanguage': null,
      'selectedTheme': null,
      'selectedFontSize': null,
      'soundEnabled': null,
    });

    expect(settings.selectedLanguage, 'en');
    expect(settings.selectedTheme, 'manuscript');
    expect(settings.selectedFontSize, 'medium');
    expect(settings.soundEnabled, isTrue);
  });

  test('toMap round-trips with fromMap', () {
    final settings = baseSettings;

    final restored = AppSettings.fromMap(settings.toMap());

    expect(restored, settings);
  });

  test('toMap keeps stable keys and scalar values', () {
    final map = baseSettings.toMap();

    expect(map.keys, <String>[
      'selectedLanguage',
      'selectedTheme',
      'selectedFontSize',
      'soundEnabled',
    ]);
    expect(map['selectedLanguage'], 'ru');
    expect(map['selectedTheme'], 'sky');
    expect(map['selectedFontSize'], 'small');
    expect(map['soundEnabled'], isFalse);
  });

  test('value equality compares all fields', () {
    final same = AppSettings(
      selectedLanguage: 'ru',
      selectedTheme: 'sky',
      selectedFontSize: 'small',
      soundEnabled: false,
    );
    final differentLanguage = AppSettings(
      selectedLanguage: 'en',
      selectedTheme: 'sky',
      selectedFontSize: 'small',
      soundEnabled: false,
    );

    expect(baseSettings, same);
    expect(baseSettings.hashCode, same.hashCode);
    expect(baseSettings, isNot(differentLanguage));
    expect(baseSettings, isNot('not-settings'));
  });
}
