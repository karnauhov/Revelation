import 'dart:convert';

import 'package:flutter/services.dart';

class BibleBookAbbreviationCatalog {
  BibleBookAbbreviationCatalog._(this._bookIdsByAlias);

  static const String assetPath = 'assets/data/bible_book_abbreviations.json';

  final Map<String, int> _bookIdsByAlias;

  static Future<BibleBookAbbreviationCatalog> loadFromAssets({
    AssetBundle? bundle,
  }) async {
    final assetBundle = bundle ?? rootBundle;
    final jsonText = await assetBundle.loadString(assetPath);
    return BibleBookAbbreviationCatalog.fromJson(
      json.decode(jsonText) as Map<String, Object?>,
    );
  }

  factory BibleBookAbbreviationCatalog.fromJson(Map<String, Object?> json) {
    final books = _requiredList(json, 'books');
    final bookIdsByAlias = <String, int>{};

    for (final bookJson in books) {
      final book = _asMap(bookJson);
      final bookId = _requiredInt(book, 'id');
      final code = _requiredString(book, 'code');
      _addAlias(bookIdsByAlias, code, bookId);

      final aliasesByLocale = _requiredMap(book, 'aliases');
      for (final aliasesEntry in aliasesByLocale.entries) {
        final aliases = _asList(aliasesEntry.value);
        for (final alias in aliases) {
          if (alias is String) {
            _addAlias(bookIdsByAlias, alias, bookId);
          }
        }
      }
    }

    return BibleBookAbbreviationCatalog._(
      Map<String, int>.unmodifiable(bookIdsByAlias),
    );
  }

  int? bookIdForAlias(String alias) {
    return _bookIdsByAlias[normalizeBibleBookAlias(alias)];
  }
}

String normalizeBibleBookAlias(String value) {
  final lower = value.trim().toLowerCase();
  final buffer = StringBuffer();
  for (final rune in lower.runes) {
    final char = String.fromCharCode(rune);
    if (_isIgnoredAliasChar(char)) {
      continue;
    }
    buffer.write(_normalizeAliasChar(char));
  }
  return buffer.toString();
}

void _addAlias(Map<String, int> aliases, String alias, int bookId) {
  final normalized = normalizeBibleBookAlias(alias);
  if (normalized.isEmpty) {
    return;
  }
  aliases.putIfAbsent(normalized, () => bookId);
}

bool _isIgnoredAliasChar(String char) {
  return char.trim().isEmpty ||
      char == '.' ||
      char == ',' ||
      char == ':' ||
      char == ';' ||
      char == '-' ||
      char == '_' ||
      char == '\'' ||
      char == '’' ||
      char == '`';
}

String _normalizeAliasChar(String char) {
  switch (char) {
    case 'ё':
      return 'е';
    case 'á':
    case 'à':
    case 'ä':
      return 'a';
    case 'é':
    case 'è':
    case 'ë':
      return 'e';
    case 'í':
    case 'ì':
    case 'ï':
      return 'i';
    case 'ó':
    case 'ò':
    case 'ö':
      return 'o';
    case 'ú':
    case 'ù':
    case 'ü':
      return 'u';
    default:
      return char;
  }
}

Map<String, Object?> _requiredMap(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return value.cast<String, Object?>();
  }
  throw FormatException('Missing map field: $key');
}

List<Object?> _requiredList(Map<String, Object?> json, String key) {
  return _asList(json[key]);
}

List<Object?> _asList(Object? value) {
  if (value is List<Object?>) {
    return value;
  }
  if (value is List) {
    return value.cast<Object?>();
  }
  throw const FormatException('Expected list field');
}

int _requiredInt(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is int && value > 0) {
    return value;
  }
  throw FormatException('Invalid positive integer field: $key');
}

String _requiredString(Map<String, Object?> json, String key) {
  final value = json[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw FormatException('Missing string field: $key');
}

Map<String, Object?> _asMap(Object? value) {
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return value.cast<String, Object?>();
  }
  throw const FormatException('Expected object in Bible book aliases');
}
