import 'package:unorm_dart/unorm_dart.dart' as unorm;

String normalizeStrongDictionarySearchText(String value) {
  final decomposed = unorm.nfd(value.trim().toLowerCase());
  final buffer = StringBuffer();
  var previousWasWhitespace = false;

  for (final rune in decomposed.runes) {
    if (_isCombiningDiacritic(rune)) {
      continue;
    }

    final character = String.fromCharCode(rune);
    if (character.trim().isEmpty) {
      if (!previousWasWhitespace && buffer.isNotEmpty) {
        buffer.write(' ');
      }
      previousWasWhitespace = true;
      continue;
    }

    buffer.write(character);
    previousWasWhitespace = false;
  }

  return buffer.toString().trim();
}

bool _isCombiningDiacritic(int code) {
  return (code >= 0x0300 && code <= 0x036f) ||
      (code >= 0x1ab0 && code <= 0x1aff) ||
      (code >= 0x1dc0 && code <= 0x1dff) ||
      (code >= 0x20d0 && code <= 0x20ff) ||
      (code >= 0xfe20 && code <= 0xfe2f);
}
