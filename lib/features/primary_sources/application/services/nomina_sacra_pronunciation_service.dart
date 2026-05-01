import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:unorm_dart/unorm_dart.dart' as unorm;

class NominaSacraPronunciationService {
  NominaSacraPronunciationService({
    Map<String, String>? pronunciationSourcesByVariant,
  }) : _pronunciationSourcesByVariant = Map<String, String>.unmodifiable(
         _normalizeEntries(
           pronunciationSourcesByVariant ?? _defaultPronunciationSources,
         ),
       );

  static const String assetPath =
      'assets/data/nomina_sacra_pronunciations.json';

  static Map<String, String> _defaultPronunciationSources = const {};

  final Map<String, String> _pronunciationSourcesByVariant;

  static Future<void> loadDefaultConfig({AssetBundle? bundle}) async {
    final rawJson = await (bundle ?? rootBundle).loadString(assetPath);
    _defaultPronunciationSources = parseConfig(rawJson);
  }

  static Map<String, String> parseConfig(String rawJson) {
    final decoded = jsonDecode(rawJson);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('Expected a JSON object.');
    }

    final rawLemmas = decoded['lemmas'];
    if (rawLemmas is! List<dynamic>) {
      throw const FormatException('Expected lemmas array.');
    }

    final pronunciationSources = <String, String>{};
    for (var lemmaIndex = 0; lemmaIndex < rawLemmas.length; lemmaIndex++) {
      final lemma = rawLemmas[lemmaIndex];
      if (lemma is! Map<String, dynamic>) {
        throw FormatException('Lemma at index $lemmaIndex must be an object.');
      }

      final rawLemmaName = lemma['lemma'];
      if (rawLemmaName is! String || rawLemmaName.trim().isEmpty) {
        throw FormatException(
          'Lemma at index $lemmaIndex must define a non-empty lemma.',
        );
      }

      final rawForms = lemma['forms'];
      if (rawForms is! List<dynamic> || rawForms.isEmpty) {
        throw FormatException(
          'Lemma "${rawLemmaName.trim()}" must define non-empty forms.',
        );
      }

      final lemmaPronunciationSources = <String>{};
      for (var formIndex = 0; formIndex < rawForms.length; formIndex++) {
        final form = rawForms[formIndex];
        if (form is! Map<String, dynamic>) {
          throw FormatException(
            'Form at index $formIndex for "${rawLemmaName.trim()}" '
            'must be an object.',
          );
        }

        final rawPronunciationSource = form['pronunciationSource'];
        if (rawPronunciationSource is! String ||
            rawPronunciationSource.trim().isEmpty) {
          throw FormatException(
            'Form at index $formIndex for "${rawLemmaName.trim()}" '
            'must define pronunciationSource.',
          );
        }
        final pronunciationSource = rawPronunciationSource.trim();
        if (!lemmaPronunciationSources.add(pronunciationSource)) {
          throw FormatException(
            'Duplicate pronunciationSource "$pronunciationSource" for '
            '"${rawLemmaName.trim()}"; merge its variants into one form.',
          );
        }

        final rawVariants = form['variants'];
        if (rawVariants is! List<dynamic> || rawVariants.isEmpty) {
          throw FormatException(
            'Form "$pronunciationSource" must define non-empty variants.',
          );
        }

        for (final rawVariant in rawVariants) {
          if (rawVariant is! String) {
            throw FormatException(
              'Variant for "$pronunciationSource" must be a string.',
            );
          }
          if (_containsCombiningOverline(rawVariant)) {
            throw FormatException(
              'Variant "$rawVariant" must not contain combining overlines.',
            );
          }

          final variant = normalizeVariant(rawVariant);
          if (variant.isEmpty) {
            throw FormatException(
              'Variant for "$pronunciationSource" must contain letters.',
            );
          }

          final existing = pronunciationSources[variant];
          if (existing != null && existing != pronunciationSource) {
            throw FormatException(
              'Variant "$rawVariant" maps to both "$existing" and '
              '"$pronunciationSource".',
            );
          }
          pronunciationSources[variant] = pronunciationSource;
        }
      }
    }

    return Map<String, String>.unmodifiable(pronunciationSources);
  }

  static String normalizeVariant(String value) {
    final normalized = unorm.nfd(value.trim());
    final letters = StringBuffer();
    for (final rune in normalized.runes) {
      if (_isCombiningDiacritic(rune)) {
        continue;
      }

      final character = String.fromCharCode(rune);
      if (_letterRegex.hasMatch(character)) {
        letters.write(character);
      }
    }
    return letters.toString().toUpperCase();
  }

  String? resolvePronunciationSource(String text) {
    final variant = normalizeVariant(text);
    if (variant.isEmpty) {
      return null;
    }
    return _pronunciationSourcesByVariant[variant];
  }

  static Map<String, String> _normalizeEntries(Map<String, String> entries) {
    final normalized = <String, String>{};
    for (final entry in entries.entries) {
      final key = normalizeVariant(entry.key);
      final value = entry.value.trim();
      if (key.isNotEmpty && value.isNotEmpty) {
        normalized[key] = value;
      }
    }
    return normalized;
  }

  static final RegExp _letterRegex = RegExp(r'\p{L}', unicode: true);

  static bool _isCombiningDiacritic(int code) {
    return code >= 0x0300 && code <= 0x036F;
  }

  static bool _containsCombiningOverline(String value) {
    return unorm.nfd(value).runes.contains(0x0305);
  }
}
