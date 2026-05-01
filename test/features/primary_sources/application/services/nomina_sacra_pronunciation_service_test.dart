import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/nomina_sacra_pronunciation_service.dart';
import 'package:revelation/features/primary_sources/application/services/pronunciation_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('parseConfig reads lemma groups and normalizes lookup input', () {
    final sources = NominaSacraPronunciationService.parseConfig('''
{
  "lemmas": [
    {
      "lemma": "Ἰησοῦς",
      "forms": [
        {
          "variants": ["ισ", " [ΙΣ] "],
          "pronunciationSource": "Ἰησοῦς"
        }
      ]
    },
    {
      "lemma": "Πατήρ",
      "forms": [
        {
          "variants": ["ΠΡΪ"],
          "pronunciationSource": "Πατρί"
        }
      ]
    }
  ]
}
''');

    expect(sources['ΙΣ'], 'Ἰησοῦς');
    expect(sources['ΠΡΙ'], 'Πατρί');

    final service = NominaSacraPronunciationService(
      pronunciationSourcesByVariant: sources,
    );
    expect(service.resolvePronunciationSource('Ι̅Σ.'), 'Ἰησοῦς');
    expect(service.resolvePronunciationSource('πρϊ'), 'Πατρί');
  });

  test('parseConfig rejects conflicting normalized variants', () {
    expect(
      () => NominaSacraPronunciationService.parseConfig('''
{
  "lemmas": [
    {
      "lemma": "Ἰησοῦς",
      "forms": [
        {
          "variants": ["ΙΣ"],
          "pronunciationSource": "Ἰησοῦς"
        }
      ]
    },
    {
      "lemma": "Ἰσραήλ",
      "forms": [
        {
          "variants": ["ΙΣ"],
          "pronunciationSource": "Ἰσραήλ"
        }
      ]
    }
  ]
}
'''),
      throwsFormatException,
    );
  });

  test('parseConfig rejects unmerged forms with same pronunciationSource', () {
    expect(
      () => NominaSacraPronunciationService.parseConfig('''
{
  "lemmas": [
    {
      "lemma": "Χριστός",
      "forms": [
        {
          "variants": ["ΧΣ"],
          "pronunciationSource": "Χριστός"
        },
        {
          "variants": ["ΧΡ"],
          "pronunciationSource": "Χριστός"
        }
      ]
    }
  ]
}
'''),
      throwsFormatException,
    );
  });

  test('parseConfig rejects overlined variants in the asset schema', () {
    expect(
      () => NominaSacraPronunciationService.parseConfig('''
{
  "lemmas": [
    {
      "lemma": "Ἰησοῦς",
      "forms": [
        {
          "variants": ["Ι̅Σ"],
          "pronunciationSource": "Ἰησοῦς"
        }
      ]
    }
  ]
}
'''),
      throwsFormatException,
    );
  });

  test(
    'asset dictionary is grouped by lemma with merged form variants',
    () async {
      final rawJson = await rootBundle.loadString(
        NominaSacraPronunciationService.assetPath,
      );
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      final lemmas = decoded['lemmas'] as List<dynamic>;

      expect(lemmas, isNotEmpty);
      for (final rawLemma in lemmas) {
        final lemma = rawLemma as Map<String, dynamic>;
        expect(lemma['lemma'], isA<String>());
        final pronunciationSources = <String>{};
        for (final rawForm in lemma['forms'] as List<dynamic>) {
          final form = rawForm as Map<String, dynamic>;
          final pronunciationSource = form['pronunciationSource'] as String;
          expect(
            pronunciationSources.add(pronunciationSource),
            isTrue,
            reason:
                'Duplicate pronunciationSource must be merged under '
                '${lemma['lemma']}.',
          );
          for (final variant in form['variants'] as List<dynamic>) {
            expect(variant, isA<String>());
            expect(
              (variant as String).contains('\u0305'),
              isFalse,
              reason: 'Variants must not store visual overlines.',
            );
          }
        }
      }
    },
  );

  test('asset dictionary resolves researched nomina sacra variants', () async {
    await NominaSacraPronunciationService.loadDefaultConfig();
    final service = NominaSacraPronunciationService();

    expect(service.resolvePronunciationSource('Θ̅Σ'), 'Θεός');
    expect(service.resolvePronunciationSource('ΚΥ'), 'Κυρίου');
    expect(service.resolvePronunciationSource('Ι̅Σ'), 'Ἰησοῦς');
    expect(service.resolvePronunciationSource('ΧΥ'), 'Χριστοῦ');
    expect(service.resolvePronunciationSource('ΥΣ'), 'Υἱός');
    expect(service.resolvePronunciationSource('Π̅Ν̅Σ'), 'Πνεύματος');
    expect(service.resolvePronunciationSource('π̅τ̅ρ̅'), 'Πατήρ');
    expect(service.resolvePronunciationSource('ΔΑΔ'), 'Δαυείδ');
    expect(service.resolvePronunciationSource('ΣΤΥ'), 'Σταυροῦ');
    expect(service.resolvePronunciationSource('ΜΗΡΣ'), 'Μητρός');
    expect(service.resolvePronunciationSource('ΙΣΡΛ'), 'Ἰσραήλ');
    expect(service.resolvePronunciationSource('ΣΡΣ'), 'Σωτῆρος');
    expect(service.resolvePronunciationSource('ΑΝΟΣ'), 'Ἄνθρωπος');
    expect(service.resolvePronunciationSource('ΙΛΗΜ'), 'Ἱερουσαλήμ');
    expect(service.resolvePronunciationSource('ΟΥΝΟΥΣ'), 'Οὐρανούς');
  });

  test('resolved sources use the shared pronunciation service per locale', () {
    final nominaSacra = NominaSacraPronunciationService(
      pronunciationSourcesByVariant: const <String, String>{'ΘΣ': 'Θεός'},
    );
    final pronunciation = PronunciationService();
    final source = nominaSacra.resolvePronunciationSource('Θ̅Σ')!;

    expect(pronunciation.convert(source.toLowerCase(), 'en'), 'theos');
    expect(pronunciation.convert(source.toLowerCase(), 'es'), 'theos');
    expect(pronunciation.convert(source.toLowerCase(), 'ru'), 'теос');
    expect(pronunciation.convert(source.toLowerCase(), 'uk'), 'теос');
  });
}
