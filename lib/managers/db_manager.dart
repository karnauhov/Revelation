import 'package:revelation/db/db_common.dart';
import 'package:revelation/db/db_localized.dart';
import 'package:revelation/db/connect/shared.dart';

class DBManager {
  static final DBManager _instance = DBManager._internal();
  DBManager._internal();

  factory DBManager() {
    return _instance;
  }

  String _dbLanguage = 'en';
  late CommonDB _commonDB;
  late LocalizedDB _localizedDB;
  late List<GreekWord> _greekWords;
  late List<GreekDesc> _greekDescs;

  List<GreekWord> get greekWords => _greekWords;
  List<GreekDesc> get greekDescs => _greekDescs;

  Future<void> init(String language) async {
    _dbLanguage = language;
    _commonDB = getCommonDB();
    _localizedDB = getLocalizedDB(_dbLanguage);
    _greekWords = await _commonDB.select(_commonDB.greekWords).get();
    _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
  }

  Future<void> updateLanguage(String newLanguage) async {
    if (_dbLanguage != newLanguage) {
      await _localizedDB.close();
      _dbLanguage = newLanguage;
      _localizedDB = getLocalizedDB(_dbLanguage);
      _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
    }
  }

  // Future<void> importWordsFromFile(String filePath) async {
  //   final file = File(filePath);
  //   final lines = await file.readAsLines();
  //   for (var line in lines) {
  //     final parts = line.split('|');
  //     if (parts.length == 2) {
  //       try {
  //         final id = int.parse(parts[0]);
  //         final word = parts[1];
  //         await _commonDB
  //             .into(_commonDB.greekWords)
  //             .insert(GreekWordsCompanion.insert(id: Value(id), word: word));
  //         print('Inserted $id: $word');
  //       } catch (e) {
  //         print('Error parsing line: $line');
  //       }
  //     }
  //   }
  // }
}
