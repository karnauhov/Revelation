import 'dart:convert';

import 'package:flutter/services.dart';

class ManuscriptGreekTextConverter {
  ManuscriptGreekTextConverter({Map<String, String>? letterReplacements})
    : _letterReplacements = Map<String, String>.unmodifiable(
        letterReplacements ?? _defaultLetterReplacements,
      );

  static const String assetPath =
      'assets/data/manuscript_greek_letter_replacements.json';

  static Map<String, String> _defaultLetterReplacements = const {};

  final Map<String, String> _letterReplacements;

  static Future<void> loadDefaultConfig({AssetBundle? bundle}) async {
    final rawJson = await (bundle ?? rootBundle).loadString(assetPath);
    _defaultLetterReplacements = parseConfig(rawJson);
  }

  static Map<String, String> parseConfig(String rawJson) {
    final decoded = jsonDecode(rawJson);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('Expected a JSON object.');
    }

    final rawReplacements = decoded['letterReplacements'];
    if (rawReplacements is! Map<String, dynamic>) {
      throw const FormatException('Expected letterReplacements object.');
    }

    final replacements = <String, String>{};
    for (final entry in rawReplacements.entries) {
      final from = entry.key;
      final to = entry.value;
      if (to is! String) {
        throw FormatException('Replacement for "$from" must be a string.');
      }
      if (_runeCount(from) != 1 || _runeCount(to) != 1) {
        throw FormatException(
          'Replacement "$from" -> "$to" must use single characters.',
        );
      }
      replacements[from] = to;
    }

    return Map<String, String>.unmodifiable(replacements);
  }

  String convert(String text) {
    if (text.isEmpty || _letterReplacements.isEmpty) {
      return text;
    }

    final buffer = StringBuffer();
    for (final rune in text.runes) {
      final character = String.fromCharCode(rune);
      buffer.write(_letterReplacements[character] ?? character);
    }
    return buffer.toString();
  }

  static int _runeCount(String value) {
    var count = 0;
    for (final _ in value.runes) {
      count++;
    }
    return count;
  }
}
