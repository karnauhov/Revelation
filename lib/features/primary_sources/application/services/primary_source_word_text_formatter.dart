import 'package:revelation/features/primary_sources/application/services/manuscript_greek_text_converter.dart';
import 'package:revelation/features/primary_sources/application/services/nomina_sacra_pronunciation_service.dart';
import 'package:revelation/shared/models/page_word.dart';

class PrimarySourceWordTextFormatter {
  PrimarySourceWordTextFormatter({
    ManuscriptGreekTextConverter? manuscriptGreekTextConverter,
    NominaSacraPronunciationService? nominaSacraPronunciation,
  }) : _manuscriptGreekTextConverter =
           manuscriptGreekTextConverter ?? ManuscriptGreekTextConverter(),
       _nominaSacraPronunciation =
           nominaSacraPronunciation ?? NominaSacraPronunciationService();

  static const int _combiningOverlineCodePoint = 0x0305;

  final ManuscriptGreekTextConverter _manuscriptGreekTextConverter;
  final NominaSacraPronunciationService _nominaSacraPronunciation;

  String format(PageWord word) {
    return _formatWordTextByIndexes(
      word.text,
      word.notExist,
      overlineLetters: _isNominaSacraWord(word),
    );
  }

  String _formatWordTextByIndexes(
    String word,
    Iterable<int> indices, {
    required bool overlineLetters,
  }) {
    if (word.isEmpty) {
      return word;
    }

    final codePoints = word.runes.toList();
    final length = codePoints.length;
    final normalized = <int>{};

    for (final idx in indices) {
      if (idx >= 0 && idx < length) {
        normalized.add(idx);
      }
    }

    if (normalized.isEmpty && !overlineLetters) {
      return _manuscriptGreekTextConverter.convert(word);
    }

    final buffer = StringBuffer();
    for (var i = 0; i < length; i++) {
      if (overlineLetters && codePoints[i] == _combiningOverlineCodePoint) {
        continue;
      }

      final ch = _manuscriptGreekTextConverter.convert(
        String.fromCharCode(codePoints[i]),
      );
      final displayChar = overlineLetters ? _overlineLetter(ch) : ch;
      if (normalized.contains(i)) {
        buffer.write('\u200E~~');
        buffer.write(displayChar);
        buffer.write('~~');
      } else {
        buffer.write(displayChar);
      }
    }

    return buffer.toString();
  }

  bool _isNominaSacraWord(PageWord word) {
    return word.snPronounce &&
        _nominaSacraPronunciation.resolvePronunciationSource(word.text) != null;
  }

  String _overlineLetter(String character) {
    if (!_containsAnyLetter(character)) {
      return character;
    }
    return '$character${String.fromCharCode(_combiningOverlineCodePoint)}';
  }

  bool _containsAnyLetter(String text) {
    final regExp = RegExp(r'\p{L}', unicode: true);
    return regExp.hasMatch(text);
  }
}
