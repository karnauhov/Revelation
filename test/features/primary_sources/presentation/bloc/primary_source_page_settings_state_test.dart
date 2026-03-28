import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_state.dart';

void main() {
  test('defaults represent expected baseline contract', () {
    const state = PrimarySourcePageSettingsState.defaults;

    expect(state.rawSettings, isEmpty);
    expect(state.isNegative, isFalse);
    expect(state.isMonochrome, isFalse);
    expect(state.brightness, 0);
    expect(state.contrast, 100);
    expect(state.showWordSeparators, isFalse);
    expect(state.showStrongNumbers, isFalse);
    expect(state.showVerseNumbers, isTrue);
  });

  test('copyWith updates only requested fields', () {
    const initial = PrimarySourcePageSettingsState.defaults;

    final updated = initial.copyWith(
      rawSettings: 'raw',
      isNegative: true,
      brightness: 15,
      showStrongNumbers: true,
    );

    expect(updated.rawSettings, 'raw');
    expect(updated.isNegative, isTrue);
    expect(updated.isMonochrome, isFalse);
    expect(updated.brightness, 15);
    expect(updated.contrast, 100);
    expect(updated.showWordSeparators, isFalse);
    expect(updated.showStrongNumbers, isTrue);
    expect(updated.showVerseNumbers, isTrue);
  });

  test('value equality compares all fields', () {
    final a = PrimarySourcePageSettingsState.defaults.copyWith(
      rawSettings: 'one',
      isNegative: true,
      isMonochrome: true,
      brightness: 10,
      contrast: 90,
      showWordSeparators: true,
      showStrongNumbers: true,
      showVerseNumbers: false,
    );
    final b = PrimarySourcePageSettingsState.defaults.copyWith(
      rawSettings: 'one',
      isNegative: true,
      isMonochrome: true,
      brightness: 10,
      contrast: 90,
      showWordSeparators: true,
      showStrongNumbers: true,
      showVerseNumbers: false,
    );
    final c = b.copyWith(contrast: 89);

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}
