import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/utils/pronunciation.dart';

class _WordCase {
  const _WordCase({
    required this.greekWord,
    required this.enEsPronunciation,
    required this.ruPronunciation,
    required this.ukPronunciation,
  });

  final String greekWord;
  final String enEsPronunciation;
  final String ruPronunciation;
  final String ukPronunciation;
}

const List<_WordCase> _wordCases = [
  _WordCase(
    greekWord: 'ἀγάπη',
    enEsPronunciation: 'agape',
    ruPronunciation: 'агапэ',
    ukPronunciation: 'агапе',
  ),
  _WordCase(
    greekWord: 'ἀδελφός',
    enEsPronunciation: 'adelphos',
    ruPronunciation: 'аделфос',
    ukPronunciation: 'аделфос',
  ),
  _WordCase(
    greekWord: 'αἰών',
    enEsPronunciation: 'aion',
    ruPronunciation: 'айон',
    ukPronunciation: 'айон',
  ),
  _WordCase(
    greekWord: 'ἀρχή',
    enEsPronunciation: 'arche',
    ruPronunciation: 'архэ',
    ukPronunciation: 'архе',
  ),
  _WordCase(
    greekWord: 'αὐτός',
    enEsPronunciation: 'autos',
    ruPronunciation: 'автос',
    ukPronunciation: 'автос',
  ),
  _WordCase(
    greekWord: 'βασιλεία',
    enEsPronunciation: 'basileia',
    ruPronunciation: 'басилейа',
    ukPronunciation: 'басілейа',
  ),
  _WordCase(
    greekWord: 'γῆ',
    enEsPronunciation: 'ge',
    ruPronunciation: 'гэ',
    ukPronunciation: 'ге',
  ),
  _WordCase(
    greekWord: 'διά',
    enEsPronunciation: 'dia',
    ruPronunciation: 'диа',
    ukPronunciation: 'діа',
  ),
  _WordCase(
    greekWord: 'εἰμί',
    enEsPronunciation: 'eimi',
    ruPronunciation: 'ейми',
    ukPronunciation: 'еймі',
  ),
  _WordCase(
    greekWord: 'εἰρήνη',
    enEsPronunciation: 'eirene',
    ruPronunciation: 'ейрэнэ',
    ukPronunciation: 'ейрене',
  ),
  _WordCase(
    greekWord: 'εὐσέβεια',
    enEsPronunciation: 'eusebeia',
    ruPronunciation: 'евсебейа',
    ukPronunciation: 'евсебейа',
  ),
  _WordCase(
    greekWord: 'ζωή',
    enEsPronunciation: 'zoe',
    ruPronunciation: 'зоэ',
    ukPronunciation: 'зое',
  ),
  _WordCase(
    greekWord: 'ἡμέρα',
    enEsPronunciation: "'emera",
    ruPronunciation: "'эмера",
    ukPronunciation: "'емера",
  ),
  _WordCase(
    greekWord: 'θεός',
    enEsPronunciation: 'theos',
    ruPronunciation: 'теос',
    ukPronunciation: 'теос',
  ),
  _WordCase(
    greekWord: 'Ἰησοῦς',
    enEsPronunciation: 'iesous',
    ruPronunciation: 'иэсус',
    ukPronunciation: 'іесус',
  ),
  _WordCase(
    greekWord: 'κύριος',
    enEsPronunciation: 'kyrios',
    ruPronunciation: 'куриос',
    ukPronunciation: 'куріос',
  ),
  _WordCase(
    greekWord: 'λόγος',
    enEsPronunciation: 'logos',
    ruPronunciation: 'логос',
    ukPronunciation: 'логос',
  ),
  _WordCase(
    greekWord: 'μαθητής',
    enEsPronunciation: 'mathetes',
    ruPronunciation: 'матэтэс',
    ukPronunciation: 'матетес',
  ),
  _WordCase(
    greekWord: 'νόμος',
    enEsPronunciation: 'nomos',
    ruPronunciation: 'номос',
    ukPronunciation: 'номос',
  ),
  _WordCase(
    greekWord: 'ξύλον',
    enEsPronunciation: 'xylon',
    ruPronunciation: 'ксулон',
    ukPronunciation: 'ксулон',
  ),
  _WordCase(
    greekWord: 'οἶκος',
    enEsPronunciation: 'oikos',
    ruPronunciation: 'ойкос',
    ukPronunciation: 'ойкос',
  ),
  _WordCase(
    greekWord: 'οὐρανός',
    enEsPronunciation: 'ouranos',
    ruPronunciation: 'уранос',
    ukPronunciation: 'уранос',
  ),
  _WordCase(
    greekWord: 'πίστις',
    enEsPronunciation: 'pistis',
    ruPronunciation: 'пистис',
    ukPronunciation: 'пістіс',
  ),
  _WordCase(
    greekWord: 'ῥῆμα',
    enEsPronunciation: "'rema",
    ruPronunciation: "'рэма",
    ukPronunciation: "'рема",
  ),
  _WordCase(
    greekWord: 'σωτηρία',
    enEsPronunciation: 'soteria',
    ruPronunciation: 'сотэриа',
    ukPronunciation: 'сотеріа',
  ),
  _WordCase(
    greekWord: 'τέκνον',
    enEsPronunciation: 'teknon',
    ruPronunciation: 'текнон',
    ukPronunciation: 'текнон',
  ),
  _WordCase(
    greekWord: 'υἱός',
    enEsPronunciation: "'uios",
    ruPronunciation: "'уйос",
    ukPronunciation: "'уйос",
  ),
  _WordCase(
    greekWord: 'φῶς',
    enEsPronunciation: 'phos',
    ruPronunciation: 'фос',
    ukPronunciation: 'фос',
  ),
  _WordCase(
    greekWord: 'χάρις',
    enEsPronunciation: 'charis',
    ruPronunciation: 'харис',
    ukPronunciation: 'харіс',
  ),
  _WordCase(
    greekWord: 'ψυχή',
    enEsPronunciation: 'psyche',
    ruPronunciation: 'псухэ',
    ukPronunciation: 'псухе',
  ),
  _WordCase(
    greekWord: 'ὦ',
    enEsPronunciation: 'o',
    ruPronunciation: 'о',
    ukPronunciation: 'о',
  ),
  _WordCase(
    greekWord: 'ἄγγελος',
    enEsPronunciation: 'angelos',
    ruPronunciation: 'ангелос',
    ukPronunciation: 'ангелос',
  ),
  _WordCase(
    greekWord: 'ἐγκράτεια',
    enEsPronunciation: 'engrateia',
    ruPronunciation: 'енгратейа',
    ukPronunciation: 'енгратейа',
  ),
  _WordCase(
    greekWord: 'σάλπιγξ',
    enEsPronunciation: 'salpinx',
    ruPronunciation: 'салпинкс',
    ukPronunciation: 'салпінкс',
  ),
  _WordCase(
    greekWord: 'ἔλεγχος',
    enEsPronunciation: 'elenchos',
    ruPronunciation: 'еленхос',
    ukPronunciation: 'еленхос',
  ),
  _WordCase(
    greekWord: 'ηὔξησεν',
    enEsPronunciation: 'euxesen',
    ruPronunciation: 'евксэсен',
    ukPronunciation: 'евксесен',
  ),
];

void main() {
  final pronunciation = Pronunciation();

  group('Word pronunciation by locale', () {
    for (final c in _wordCases) {
      test(c.greekWord, () {
        final greek = c.greekWord.toLowerCase();

        expect(pronunciation.convert(greek, 'en'), c.enEsPronunciation);
        expect(pronunciation.convert(greek, 'es'), c.enEsPronunciation);
        expect(pronunciation.convert(greek, 'ru'), c.ruPronunciation);
        expect(pronunciation.convert(greek, 'uk'), c.ukPronunciation);
      });
    }
  });
}
