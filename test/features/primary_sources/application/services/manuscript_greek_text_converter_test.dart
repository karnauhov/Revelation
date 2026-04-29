import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/manuscript_greek_text_converter.dart';

void main() {
  test('parseConfig reads letter replacements', () {
    final replacements = ManuscriptGreekTextConverter.parseConfig(
      '{"letterReplacements":{"Α":"Α","Β":"Ⲃ","Μ":"Μ","Ψ":"ⲯ"}}',
    );

    expect(replacements, <String, String>{
      'Α': 'Α',
      'Β': 'Ⲃ',
      'Μ': 'Μ',
      'Ψ': 'ⲯ',
    });
  });

  test('convert replaces configured Greek manuscript letters only', () {
    final converter = ManuscriptGreekTextConverter(
      letterReplacements: const <String, String>{
        'Α': 'Α',
        'Β': 'Ⲃ',
        'Γ': 'Ⲅ',
        'Μ': 'Μ',
        'Ψ': 'ⲯ',
        'Ω': 'Ⲱ',
      },
    );

    expect(converter.convert('ΑΒΓΜΨΩ.'), 'ΑⲂⲄΜⲯⲰ.');
  });

  test('parseConfig rejects malformed replacements', () {
    expect(
      () => ManuscriptGreekTextConverter.parseConfig(
        '{"letterReplacements":{"Β":"BC"}}',
      ),
      throwsFormatException,
    );
  });
}
