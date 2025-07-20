import 'package:unorm_dart/unorm_dart.dart' as unorm;

class Transliteration {
  static final Transliteration _instance = Transliteration._internal();
  Transliteration._internal();

  factory Transliteration() {
    return _instance;
  }

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

  String transliterate(String greekWord, String locale) {
    String result = "";
    switch (locale) {
      case 'en':
      case 'es':
        result = _transliterate(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinSpecialConsonantMap,
        );
        break;
      case 'ru':
        result = _transliterate(
          greekWord,
          _cyrillicLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicSpecialConsonantMap,
        );
        break;
      case 'uk':
        result = _transliterate(
          greekWord,
          _ukrainianLetterMap,
          _cyrillicDiphthongMap,
          _cyrillicSpecialConsonantMap,
        );
        break;
      default:
        result = _transliterate(
          greekWord,
          _latinLetterMap,
          _latinDiphthongMap,
          _latinSpecialConsonantMap,
        );
        break;
    }
    return result;
  }

  String _transliterate(
    String greekWord,
    Map<String, String> letterMap,
    Map<String, String> diphthongMap,
    Map<String, String> specialConsonantMap,
  ) {
    final word = unorm.nfd(greekWord);
    String result = '';
    int i = 0;

    while (i < word.length) {
      String char = word[i];

      if (char == ' ') {
        result += ' ';
        i++;
        continue;
      }

      if (i + 1 < word.length) {
        String potentialSpecial = char + word[i + 1];
        if (_specialConsonants.contains(potentialSpecial)) {
          result += specialConsonantMap[potentialSpecial]!;
          i += 2;
          continue;
        }
      }

      List<String> diacritics = [];
      int j = i + 1;
      while (j < word.length && _isCombiningDiacritic(word[j].codeUnitAt(0))) {
        diacritics.add(word[j]);
        j++;
      }

      String baseLetter = char;
      String nextBase = _getNextBaseLetter(word, j);
      String diphthong = baseLetter + nextBase;

      if (_diphthongFirst.contains(baseLetter) &&
          _greekVowels.contains(nextBase) &&
          diphthongMap.containsKey(diphthong)) {
        String mapped = diphthongMap[diphthong]!;
        if (diacritics.contains('\u0314')) {
          mapped = _breathingMark + mapped;
        }
        result += mapped;
        i = j;
        i++;
        while (i < word.length &&
            _isCombiningDiacritic(word[i].codeUnitAt(0))) {
          i++;
        }
      } else {
        String mapped = letterMap[baseLetter] ?? baseLetter;
        if ((baseLetter.toLowerCase() == 'ρ' ||
                _greekVowels.contains(baseLetter.toLowerCase())) &&
            diacritics.contains('\u0314')) {
          mapped = _breathingMark + mapped;
        }
        result += mapped;
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

  final String _breathingMark = '\'';
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
  final Map<String, String> _cyrillicSpecialConsonantMap = {
    'γγ': 'нг',
    'γκ': 'нг',
    'γξ': 'нкс',
    'γχ': 'нх',
    'Γγ': 'Нг',
    'Γк': 'Нг',
    'Γξ': 'Нкс',
    'Γχ': 'Нх',
  };

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
    'о': 'о',
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
    'О': 'О',
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
