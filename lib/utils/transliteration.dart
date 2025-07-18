class Transliteration {
  static final Transliteration _instance = Transliteration._internal();
  Transliteration._internal();

  factory Transliteration() {
    return _instance;
  }

  final Set<String> _greekVowels = {'α', 'ε', 'η', 'ι', 'ο', 'υ', 'ω'};
  final Set<String> _diphthongFirst = {'α', 'ε', 'ο', 'υ', 'η'};

  String transliterate(String greekWord, String locale) {
    String result = "";
    switch (locale) {
      case 'en':
      case 'es':
        result = _transliterate(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinBreathingMark,
        );
        break;
      case 'ru':
        result = _transliterate(
          greekWord,
          _cyrillicLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicBreathingMark,
        );
        break;
      case 'uk':
        result = _transliterate(
          greekWord,
          _ukrainianLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicBreathingMark,
        );
        break;
      default:
        result = _transliterate(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinBreathingMark,
        );
        break;
    }
    return result;
  }

  String _transliterate(
    String greekWord,
    Map<String, String> letterMap,
    Map<String, String> diphthongMap,
    String breathingMark,
  ) {
    String result = '';
    int i = 0;

    while (i < greekWord.length) {
      String char = greekWord[i];

      if (char == ' ') {
        result += ' ';
        i++;
        continue;
      }

      List<String> diacritics = [];
      int j = i + 1;
      while (j < greekWord.length &&
          _isCombiningDiacritic(greekWord[j].codeUnitAt(0))) {
        diacritics.add(greekWord[j]);
        j++;
      }

      String nextBase = _getNextBaseLetter(greekWord, j);
      String diphthong = char + nextBase;

      if (_diphthongFirst.contains(char) &&
          _greekVowels.contains(nextBase) &&
          diphthongMap.containsKey(diphthong)) {
        String mapped = diphthongMap[diphthong]!;
        if (diacritics.contains('\u0314')) {
          mapped = breathingMark + mapped;
        }
        result += mapped;
        i = j;
        while (i < greekWord.length &&
            _isCombiningDiacritic(greekWord[i].codeUnitAt(0))) {
          i++;
        }
        i++;
      } else {
        String base = letterMap[char] ?? char;
        if (_greekVowels.contains(char) && diacritics.contains('\u0314')) {
          base = breathingMark + base;
        }
        result += base;
        i = j;
      }
    }
    return result;
  }

  bool _isCombiningDiacritic(int code) {
    return code >= 0x0300 && code <= 0x036F;
  }

  String _getNextBaseLetter(String s, int start) {
    for (int j = start; j < s.length; j++) {
      String c = s[j];
      if (!_isCombiningDiacritic(c.codeUnitAt(0))) {
        return c;
      }
    }
    return '';
  }

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
  };
  final Map<String, String> _latinDiphthongMap = {
    'αι': 'ai',
    'ει': 'ei',
    'οι': 'oi',
    'ου': 'ou',
    'υι': 'ui',
    'αυ': 'au',
    'ευ': 'eu',
    'ηυ': 'eu',
  };
  final String _latinBreathingMark = 'h';

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
  };
  final Map<String, String> _cyrillicDiphthongMap = {
    'αι': 'ай',
    'ει': 'ей',
    'οι': 'ой',
    'ου': 'у',
    'υι': 'уй',
    'αυ': 'ав',
    'ευ': 'ев',
    'ηυ': 'ев',
  };
  final String _cyrillicBreathingMark = '\'';

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
  };
}
