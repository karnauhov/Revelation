import 'package:unorm_dart/unorm_dart.dart' as unorm;

class PronunciationService {
  static final PronunciationService _instance =
      PronunciationService._internal();
  PronunciationService._internal();

  factory PronunciationService() {
    return _instance;
  }

  // Academic baseline for transliteration rules used below:
  // SBL style table (as reproduced by UBS/TBT), including:
  // - gamma-nasal rule (g -> n before γ/κ/ξ/χ),
  // - upsilon treatment in diphthongs,
  // - rough-breathing handling.
  // Source: https://translation.bible/publications/the-bible-translator/tbt-style-guide/
  // (Section 8.2, based on The SBL Handbook of Style, 2nd ed.).

  // Koine phonology background (for historical context) and bibliography
  // to Gignac 1976, Teodorsson 1977, Horrocks 2014:
  // https://www.koinegreek.com/koine-pronunciation

  static const String _roughBreathing = '̔';
  static const String _diaeresis = '̈';
  final String _breathingMark = '\'';

  // Vowel inventory used for diphthong detection and rough-breathing rules.
  final Set<String> _greekVowels = {
    'α',
    'ε',
    'η',
    'ι',
    'ο',
    'υ',
    'ω',
    'Α',
    'Ε',
    'Η',
    'Ι',
    'Ο',
    'Υ',
    'Ω',
  };

  // First element candidates for diphthongs treated by this transliteration.
  final Set<String> _diphthongFirst = {
    'α',
    'ε',
    'ο',
    'υ',
    'η',
    'Α',
    'Ε',
    'Ο',
    'Υ',
    'Η',
  };

  // SBL gamma-nasal contexts (γγ, γκ, γξ, γχ), plus title-case forms.
  final Set<String> _specialConsonants = {
    'γγ',
    'γκ',
    'γξ',
    'γχ',
    'Γγ',
    'Γκ',
    'Γξ',
    'Γχ',
  };

  String convert(String greekWord, String locale) {
    switch (locale) {
      case 'en':
      case 'es':
        return _convert(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinSpecialConsonantMap,
        );
      case 'ru':
        return _convert(
          greekWord,
          _cyrillicLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicSpecialConsonantMap,
        );
      case 'uk':
        return _convert(
          greekWord,
          _ukrainianLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicSpecialConsonantMap,
        );
      default:
        return _convert(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinSpecialConsonantMap,
        );
    }
  }

  String _convert(
    String greekWord,
    Map<String, String> letterMap,
    Map<String, String> diphthongMap,
    Map<String, String> specialConsonantMap,
  ) {
    final word = unorm.nfd(greekWord);
    final result = StringBuffer();
    int i = 0;

    while (i < word.length) {
      final char = word[i];
      if (char == ' ') {
        result.write(' ');
        i++;
        continue;
      }

      if (i + 1 < word.length) {
        final potentialSpecial = char + word[i + 1];
        if (_specialConsonants.contains(potentialSpecial)) {
          result.write(specialConsonantMap[potentialSpecial]!);
          i += 2;
          continue;
        }
      }

      final baseLetter = char;
      final firstDiacritics = _collectCombiningDiacritics(word, i + 1);
      final afterFirstDiacriticsIndex = i + 1 + firstDiacritics.length;
      final nextBaseIndex = _getNextBaseIndex(word, afterFirstDiacriticsIndex);
      final nextBase = nextBaseIndex == -1 ? '' : word[nextBaseIndex];
      final diphthong = baseLetter + nextBase;
      final secondDiacritics = nextBaseIndex == -1
          ? const <String>[]
          : _collectCombiningDiacritics(word, nextBaseIndex + 1);

      final hasRoughBreathing =
          firstDiacritics.contains(_roughBreathing) ||
          secondDiacritics.contains(_roughBreathing);
      final secondHasDiaeresis = secondDiacritics.contains(_diaeresis);

      final isMappedDiphthong =
          _diphthongFirst.contains(baseLetter) &&
          _greekVowels.contains(nextBase) &&
          diphthongMap.containsKey(diphthong) &&
          !secondHasDiaeresis;

      if (isMappedDiphthong) {
        var mapped = diphthongMap[diphthong]!;
        // Rough breathing is written on the second element of initial diphthongs
        // in polytonic Greek, but transliterates before the full diphthong.
        if (hasRoughBreathing) {
          mapped = _breathingMark + mapped;
        }
        result.write(mapped);
        i = _skipCombiningDiacritics(word, nextBaseIndex + 1);
        continue;
      }

      var mapped = letterMap[baseLetter] ?? baseLetter;
      if ((baseLetter.toLowerCase() == 'ρ' ||
              _greekVowels.contains(baseLetter.toLowerCase())) &&
          firstDiacritics.contains(_roughBreathing)) {
        mapped = _breathingMark + mapped;
      }
      result.write(mapped);
      i = afterFirstDiacriticsIndex;
    }

    return result.toString();
  }

  List<String> _collectCombiningDiacritics(String s, int start) {
    final diacritics = <String>[];
    int i = start;
    while (i < s.length && _isCombiningDiacritic(s[i].codeUnitAt(0))) {
      diacritics.add(s[i]);
      i++;
    }
    return diacritics;
  }

  int _skipCombiningDiacritics(String s, int start) {
    int i = start;
    while (i < s.length && _isCombiningDiacritic(s[i].codeUnitAt(0))) {
      i++;
    }
    return i;
  }

  bool _isCombiningDiacritic(int code) {
    return code >= 0x0300 && code <= 0x036F;
  }

  int _getNextBaseIndex(String s, int start) {
    for (int j = start; j < s.length; j++) {
      if (!_isCombiningDiacritic(s[j].codeUnitAt(0))) {
        return j;
      }
    }
    return -1;
  }

  // Base alphabet map (Latin transliteration profile).
  final Map<String, String> _latinLetterMap = {
    'α': 'a',
    'β': 'b',
    'γ': 'g',
    'δ': 'd',
    'ε': 'e',
    'ζ': 'z',
    'η': 'e',
    'θ': 'th',
    'ι': 'i',
    'κ': 'k',
    'λ': 'l',
    'μ': 'm',
    'ν': 'n',
    'ξ': 'x',
    'ο': 'o',
    'π': 'p',
    'ρ': 'r',
    'σ': 's',
    'ς': 's',
    'τ': 't',
    'υ': 'y',
    'φ': 'ph',
    'χ': 'ch',
    'ψ': 'ps',
    'ω': 'o',
    'Α': 'A',
    'Β': 'B',
    'Γ': 'G',
    'Δ': 'D',
    'Ε': 'E',
    'Ζ': 'Z',
    'Η': 'E',
    'Θ': 'Th',
    'Ι': 'I',
    'Κ': 'K',
    'Λ': 'L',
    'Μ': 'M',
    'Ν': 'N',
    'Ξ': 'X',
    'Ο': 'O',
    'Π': 'P',
    'Ρ': 'R',
    'Σ': 'S',
    'Τ': 'T',
    'Υ': 'Y',
    'Φ': 'Ph',
    'Χ': 'Ch',
    'Ψ': 'Ps',
    'Ω': 'O',
  };

  // Diphthong table used by 'en'/'es' transliteration output.
  final Map<String, String> _latinDiphthongMap = {
    'αι': 'ai',
    'ει': 'ei',
    'οι': 'oi',
    'ου': 'ou',
    'υι': 'ui',
    'αυ': 'au',
    'ευ': 'eu',
    'ηυ': 'eu',
    'Αι': 'Ai',
    'Ει': 'Ei',
    'Οι': 'Oi',
    'Ου': 'Ou',
    'Υι': 'Ui',
    'Αυ': 'Au',
    'Ευ': 'Eu',
    'Ηυ': 'Eu',
  };

  // Gamma-nasal realizations per SBL transliteration note.
  final Map<String, String> _latinSpecialConsonantMap = {
    'γγ': 'ng',
    'γκ': 'ng',
    'γξ': 'nx',
    'γχ': 'nch',
    'Γγ': 'Ng',
    'Γκ': 'Ng',
    'Γξ': 'Nx',
    'Γχ': 'Nch',
  };

  // Cyrillic maps are project-specific readability profiles for UI output.
  // They are not a strict one-to-one academic transliteration standard.
  // Cyrillic transliteration profile for 'ru'.
  final Map<String, String> _cyrillicLetterMap = {
    'α': 'а',
    'β': 'б',
    'γ': 'г',
    'δ': 'д',
    'ε': 'е',
    'ζ': 'з',
    'η': 'э',
    'θ': 'т',
    'ι': 'и',
    'κ': 'к',
    'λ': 'л',
    'μ': 'м',
    'ν': 'н',
    'ξ': 'кс',
    'ο': 'о',
    'π': 'п',
    'ρ': 'р',
    'σ': 'с',
    'ς': 'с',
    'τ': 'т',
    'υ': 'у',
    'φ': 'ф',
    'χ': 'х',
    'ψ': 'пс',
    'ω': 'о',
    'Α': 'А',
    'Β': 'Б',
    'Γ': 'Г',
    'Δ': 'Д',
    'Ε': 'Е',
    'Ζ': 'З',
    'Η': 'Э',
    'Θ': 'Т',
    'Ι': 'И',
    'Κ': 'К',
    'Λ': 'Л',
    'Μ': 'М',
    'Ν': 'Н',
    'Ξ': 'Кс',
    'Ο': 'О',
    'Π': 'П',
    'Ρ': 'Р',
    'Σ': 'С',
    'Τ': 'Т',
    'Υ': 'У',
    'Φ': 'Ф',
    'Χ': 'Х',
    'Ψ': 'Пс',
    'Ω': 'О',
  };

  // Cyrillic diphthong table used by both 'ru' and 'uk' in current UX.
  final Map<String, String> _cyrillicDiphthongMap = {
    'αι': 'ай',
    'ει': 'ей',
    'οι': 'ой',
    'ου': 'у',
    'υι': 'уй',
    'αυ': 'ав',
    'ευ': 'ев',
    'ηυ': 'ев',
    'Αι': 'Ай',
    'Ει': 'Ей',
    'Οι': 'Ой',
    'Ου': 'У',
    'Υι': 'Уй',
    'Αυ': 'Ав',
    'Ευ': 'Ев',
    'Ηυ': 'Ев',
  };

  // Cyrillic gamma-nasal combinations for 'ru'/'uk'.
  final Map<String, String> _cyrillicSpecialConsonantMap = {
    'γγ': 'нг',
    'γκ': 'нг',
    'γξ': 'нкс',
    'γχ': 'нх',
    'Γγ': 'Нг',
    'Γκ': 'Нг',
    'Γξ': 'Нкс',
    'Γχ': 'Нх',
  };

  // Cyrillic transliteration profile for 'uk' locale.
  final Map<String, String> _ukrainianLetterMap = {
    'α': 'а',
    'β': 'б',
    'γ': 'г',
    'δ': 'д',
    'ε': 'е',
    'ζ': 'з',
    'η': 'е',
    'θ': 'т',
    'ι': 'і',
    'κ': 'к',
    'λ': 'л',
    'μ': 'м',
    'ν': 'н',
    'ξ': 'кс',
    'ο': 'о',
    'π': 'п',
    'ρ': 'р',
    'σ': 'с',
    'ς': 'с',
    'τ': 'т',
    'υ': 'у',
    'φ': 'ф',
    'χ': 'х',
    'ψ': 'пс',
    'ω': 'о',
    'Α': 'А',
    'Β': 'Б',
    'Γ': 'Г',
    'Δ': 'Д',
    'Ε': 'Е',
    'Ζ': 'З',
    'Η': 'Е',
    'Θ': 'Т',
    'Ι': 'І',
    'Κ': 'К',
    'Λ': 'Л',
    'Μ': 'М',
    'Ν': 'Н',
    'Ξ': 'Кс',
    'Ο': 'О',
    'Π': 'П',
    'Ρ': 'Р',
    'Σ': 'С',
    'Τ': 'Т',
    'Υ': 'У',
    'Φ': 'Ф',
    'Χ': 'Х',
    'Ψ': 'Пс',
    'Ω': 'О',
  };
}
