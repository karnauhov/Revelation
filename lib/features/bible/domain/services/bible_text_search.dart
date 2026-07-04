import 'package:revelation/features/bible/domain/models/bible_search_result.dart';

final RegExp bibleStrongTokenPattern = RegExp(
  r'^[GH]\d+$',
  caseSensitive: false,
);

String plainBibleText(String text) {
  final tokens = text.trim().split(RegExp(r'\s+'));
  if (tokens.length == 1 && tokens.first.isEmpty) {
    return '';
  }
  return tokens
      .where((token) => !bibleStrongTokenPattern.hasMatch(token))
      .join(' ')
      .trim();
}

String normalizeBibleSearchQuery(String query) {
  return query.trim().split(RegExp(r'\s+')).join(' ');
}

String normalizeBibleSearchText(String text) {
  return normalizeBibleSearchQuery(_normalizeBibleSearchText(text).text);
}

List<BibleTextMatch> findBibleTextMatches(String text, String query) {
  final normalizedQuery = normalizeBibleSearchText(query);
  final normalizedText = _normalizeBibleSearchText(text);
  if (normalizedText.text.isEmpty || normalizedQuery.isEmpty) {
    return const <BibleTextMatch>[];
  }

  final haystack = normalizedText.text;
  final needle = normalizedQuery;
  final matches = <BibleTextMatch>[];
  var searchOffset = 0;
  while (searchOffset < haystack.length) {
    final matchIndex = haystack.indexOf(needle, searchOffset);
    if (matchIndex < 0) {
      break;
    }
    final matchEnd = matchIndex + needle.length;
    matches.add(
      BibleTextMatch(
        start: normalizedText.originalStarts[matchIndex],
        end: normalizedText.originalEnds[matchEnd - 1],
      ),
    );
    searchOffset = matchEnd;
  }
  return List<BibleTextMatch>.unmodifiable(matches);
}

_NormalizedSearchText _normalizeBibleSearchText(String text) {
  if (text.isEmpty) {
    return const _NormalizedSearchText(
      text: '',
      originalStarts: <int>[],
      originalEnds: <int>[],
    );
  }

  final buffer = StringBuffer();
  final originalStarts = <int>[];
  final originalEnds = <int>[];
  var offset = 0;
  for (final rune in text.runes) {
    final char = String.fromCharCode(rune);
    final charEnd = offset + char.length;
    final folded = _foldSearchCharacter(char);
    var wroteFoldedCharacter = false;
    for (final foldedRune in folded.runes) {
      if (_isCombiningMark(foldedRune)) {
        continue;
      }
      buffer.writeCharCode(foldedRune);
      originalStarts.add(offset);
      originalEnds.add(charEnd);
      wroteFoldedCharacter = true;
    }
    if (!wroteFoldedCharacter &&
        _isCombiningMark(rune) &&
        originalEnds.isNotEmpty) {
      originalEnds[originalEnds.length - 1] = charEnd;
    }
    offset = charEnd;
  }

  return _NormalizedSearchText(
    text: buffer.toString(),
    originalStarts: List<int>.unmodifiable(originalStarts),
    originalEnds: List<int>.unmodifiable(originalEnds),
  );
}

String _foldSearchCharacter(String char) {
  final buffer = StringBuffer();
  for (final rune in char.toLowerCase().runes) {
    if (_isCombiningMark(rune)) {
      continue;
    }
    final replacement = _greekSearchFoldByRune[rune];
    if (replacement != null) {
      buffer.write(replacement);
    } else {
      buffer.writeCharCode(rune);
    }
  }
  return buffer.toString();
}

bool _isCombiningMark(int rune) {
  return (rune >= 0x0300 && rune <= 0x036F) ||
      (rune >= 0x0591 && rune <= 0x05BD) ||
      rune == 0x05BF ||
      (rune >= 0x05C1 && rune <= 0x05C2) ||
      (rune >= 0x05C4 && rune <= 0x05C5) ||
      rune == 0x05C7 ||
      (rune >= 0x1AB0 && rune <= 0x1AFF) ||
      (rune >= 0x1DC0 && rune <= 0x1DFF) ||
      (rune >= 0x20D0 && rune <= 0x20FF) ||
      (rune >= 0xFE20 && rune <= 0xFE2F);
}

class _NormalizedSearchText {
  const _NormalizedSearchText({
    required this.text,
    required this.originalStarts,
    required this.originalEnds,
  });

  final String text;
  final List<int> originalStarts;
  final List<int> originalEnds;
}

const Map<int, String> _greekSearchFoldByRune = <int, String>{
  0x0386: '\u{3B1}',
  0x0388: '\u{3B5}',
  0x0389: '\u{3B7}',
  0x038A: '\u{3B9}',
  0x038C: '\u{3BF}',
  0x038E: '\u{3C5}',
  0x038F: '\u{3C9}',
  0x0390: '\u{3B9}',
  0x03AA: '\u{3B9}',
  0x03AB: '\u{3C5}',
  0x03AC: '\u{3B1}',
  0x03AD: '\u{3B5}',
  0x03AE: '\u{3B7}',
  0x03AF: '\u{3B9}',
  0x03B0: '\u{3C5}',
  0x03C2: '\u{3C3}',
  0x03CA: '\u{3B9}',
  0x03CB: '\u{3C5}',
  0x03CC: '\u{3BF}',
  0x03CD: '\u{3C5}',
  0x03CE: '\u{3C9}',
  0x03D3: '\u{3D2}',
  0x03D4: '\u{3D2}',
  0x1F00: '\u{3B1}',
  0x1F01: '\u{3B1}',
  0x1F02: '\u{3B1}',
  0x1F03: '\u{3B1}',
  0x1F04: '\u{3B1}',
  0x1F05: '\u{3B1}',
  0x1F06: '\u{3B1}',
  0x1F07: '\u{3B1}',
  0x1F08: '\u{3B1}',
  0x1F09: '\u{3B1}',
  0x1F0A: '\u{3B1}',
  0x1F0B: '\u{3B1}',
  0x1F0C: '\u{3B1}',
  0x1F0D: '\u{3B1}',
  0x1F0E: '\u{3B1}',
  0x1F0F: '\u{3B1}',
  0x1F10: '\u{3B5}',
  0x1F11: '\u{3B5}',
  0x1F12: '\u{3B5}',
  0x1F13: '\u{3B5}',
  0x1F14: '\u{3B5}',
  0x1F15: '\u{3B5}',
  0x1F18: '\u{3B5}',
  0x1F19: '\u{3B5}',
  0x1F1A: '\u{3B5}',
  0x1F1B: '\u{3B5}',
  0x1F1C: '\u{3B5}',
  0x1F1D: '\u{3B5}',
  0x1F20: '\u{3B7}',
  0x1F21: '\u{3B7}',
  0x1F22: '\u{3B7}',
  0x1F23: '\u{3B7}',
  0x1F24: '\u{3B7}',
  0x1F25: '\u{3B7}',
  0x1F26: '\u{3B7}',
  0x1F27: '\u{3B7}',
  0x1F28: '\u{3B7}',
  0x1F29: '\u{3B7}',
  0x1F2A: '\u{3B7}',
  0x1F2B: '\u{3B7}',
  0x1F2C: '\u{3B7}',
  0x1F2D: '\u{3B7}',
  0x1F2E: '\u{3B7}',
  0x1F2F: '\u{3B7}',
  0x1F30: '\u{3B9}',
  0x1F31: '\u{3B9}',
  0x1F32: '\u{3B9}',
  0x1F33: '\u{3B9}',
  0x1F34: '\u{3B9}',
  0x1F35: '\u{3B9}',
  0x1F36: '\u{3B9}',
  0x1F37: '\u{3B9}',
  0x1F38: '\u{3B9}',
  0x1F39: '\u{3B9}',
  0x1F3A: '\u{3B9}',
  0x1F3B: '\u{3B9}',
  0x1F3C: '\u{3B9}',
  0x1F3D: '\u{3B9}',
  0x1F3E: '\u{3B9}',
  0x1F3F: '\u{3B9}',
  0x1F40: '\u{3BF}',
  0x1F41: '\u{3BF}',
  0x1F42: '\u{3BF}',
  0x1F43: '\u{3BF}',
  0x1F44: '\u{3BF}',
  0x1F45: '\u{3BF}',
  0x1F48: '\u{3BF}',
  0x1F49: '\u{3BF}',
  0x1F4A: '\u{3BF}',
  0x1F4B: '\u{3BF}',
  0x1F4C: '\u{3BF}',
  0x1F4D: '\u{3BF}',
  0x1F50: '\u{3C5}',
  0x1F51: '\u{3C5}',
  0x1F52: '\u{3C5}',
  0x1F53: '\u{3C5}',
  0x1F54: '\u{3C5}',
  0x1F55: '\u{3C5}',
  0x1F56: '\u{3C5}',
  0x1F57: '\u{3C5}',
  0x1F59: '\u{3C5}',
  0x1F5B: '\u{3C5}',
  0x1F5D: '\u{3C5}',
  0x1F5F: '\u{3C5}',
  0x1F60: '\u{3C9}',
  0x1F61: '\u{3C9}',
  0x1F62: '\u{3C9}',
  0x1F63: '\u{3C9}',
  0x1F64: '\u{3C9}',
  0x1F65: '\u{3C9}',
  0x1F66: '\u{3C9}',
  0x1F67: '\u{3C9}',
  0x1F68: '\u{3C9}',
  0x1F69: '\u{3C9}',
  0x1F6A: '\u{3C9}',
  0x1F6B: '\u{3C9}',
  0x1F6C: '\u{3C9}',
  0x1F6D: '\u{3C9}',
  0x1F6E: '\u{3C9}',
  0x1F6F: '\u{3C9}',
  0x1F70: '\u{3B1}',
  0x1F71: '\u{3B1}',
  0x1F72: '\u{3B5}',
  0x1F73: '\u{3B5}',
  0x1F74: '\u{3B7}',
  0x1F75: '\u{3B7}',
  0x1F76: '\u{3B9}',
  0x1F77: '\u{3B9}',
  0x1F78: '\u{3BF}',
  0x1F79: '\u{3BF}',
  0x1F7A: '\u{3C5}',
  0x1F7B: '\u{3C5}',
  0x1F7C: '\u{3C9}',
  0x1F7D: '\u{3C9}',
  0x1F80: '\u{3B1}',
  0x1F81: '\u{3B1}',
  0x1F82: '\u{3B1}',
  0x1F83: '\u{3B1}',
  0x1F84: '\u{3B1}',
  0x1F85: '\u{3B1}',
  0x1F86: '\u{3B1}',
  0x1F87: '\u{3B1}',
  0x1F88: '\u{3B1}',
  0x1F89: '\u{3B1}',
  0x1F8A: '\u{3B1}',
  0x1F8B: '\u{3B1}',
  0x1F8C: '\u{3B1}',
  0x1F8D: '\u{3B1}',
  0x1F8E: '\u{3B1}',
  0x1F8F: '\u{3B1}',
  0x1F90: '\u{3B7}',
  0x1F91: '\u{3B7}',
  0x1F92: '\u{3B7}',
  0x1F93: '\u{3B7}',
  0x1F94: '\u{3B7}',
  0x1F95: '\u{3B7}',
  0x1F96: '\u{3B7}',
  0x1F97: '\u{3B7}',
  0x1F98: '\u{3B7}',
  0x1F99: '\u{3B7}',
  0x1F9A: '\u{3B7}',
  0x1F9B: '\u{3B7}',
  0x1F9C: '\u{3B7}',
  0x1F9D: '\u{3B7}',
  0x1F9E: '\u{3B7}',
  0x1F9F: '\u{3B7}',
  0x1FA0: '\u{3C9}',
  0x1FA1: '\u{3C9}',
  0x1FA2: '\u{3C9}',
  0x1FA3: '\u{3C9}',
  0x1FA4: '\u{3C9}',
  0x1FA5: '\u{3C9}',
  0x1FA6: '\u{3C9}',
  0x1FA7: '\u{3C9}',
  0x1FA8: '\u{3C9}',
  0x1FA9: '\u{3C9}',
  0x1FAA: '\u{3C9}',
  0x1FAB: '\u{3C9}',
  0x1FAC: '\u{3C9}',
  0x1FAD: '\u{3C9}',
  0x1FAE: '\u{3C9}',
  0x1FAF: '\u{3C9}',
  0x1FB0: '\u{3B1}',
  0x1FB1: '\u{3B1}',
  0x1FB2: '\u{3B1}',
  0x1FB3: '\u{3B1}',
  0x1FB4: '\u{3B1}',
  0x1FB6: '\u{3B1}',
  0x1FB7: '\u{3B1}',
  0x1FB8: '\u{3B1}',
  0x1FB9: '\u{3B1}',
  0x1FBA: '\u{3B1}',
  0x1FBB: '\u{3B1}',
  0x1FBC: '\u{3B1}',
  0x1FBE: '\u{3B9}',
  0x1FC2: '\u{3B7}',
  0x1FC3: '\u{3B7}',
  0x1FC4: '\u{3B7}',
  0x1FC6: '\u{3B7}',
  0x1FC7: '\u{3B7}',
  0x1FC8: '\u{3B5}',
  0x1FC9: '\u{3B5}',
  0x1FCA: '\u{3B7}',
  0x1FCB: '\u{3B7}',
  0x1FCC: '\u{3B7}',
  0x1FD0: '\u{3B9}',
  0x1FD1: '\u{3B9}',
  0x1FD2: '\u{3B9}',
  0x1FD3: '\u{3B9}',
  0x1FD6: '\u{3B9}',
  0x1FD7: '\u{3B9}',
  0x1FD8: '\u{3B9}',
  0x1FD9: '\u{3B9}',
  0x1FDA: '\u{3B9}',
  0x1FDB: '\u{3B9}',
  0x1FE0: '\u{3C5}',
  0x1FE1: '\u{3C5}',
  0x1FE2: '\u{3C5}',
  0x1FE3: '\u{3C5}',
  0x1FE4: '\u{3C1}',
  0x1FE5: '\u{3C1}',
  0x1FE6: '\u{3C5}',
  0x1FE7: '\u{3C5}',
  0x1FE8: '\u{3C5}',
  0x1FE9: '\u{3C5}',
  0x1FEA: '\u{3C5}',
  0x1FEB: '\u{3C5}',
  0x1FEC: '\u{3C1}',
  0x1FF2: '\u{3C9}',
  0x1FF3: '\u{3C9}',
  0x1FF4: '\u{3C9}',
  0x1FF6: '\u{3C9}',
  0x1FF7: '\u{3C9}',
  0x1FF8: '\u{3BF}',
  0x1FF9: '\u{3BF}',
  0x1FFA: '\u{3C9}',
  0x1FFB: '\u{3C9}',
  0x1FFC: '\u{3C9}',
};
