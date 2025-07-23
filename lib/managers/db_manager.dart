// import 'dart:convert';
// import 'dart:io';
// import 'package:drift/drift.dart';
// import 'package:http/http.dart' as http;
// import 'package:path/path.dart' as path;
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
  String get langDB => _dbLanguage;

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

  // Future<void> importCategoriesFromFile(String filePath) async {
  //   final file = File(filePath);
  //   if (!await file.exists()) {
  //     throw Exception('File not found: \$filePath');
  //   }
  //   final lines = await file.readAsLines();

  //   await _commonDB.transaction(() async {
  //     for (var line in lines) {
  //       line = line.trim();
  //       if (line.isEmpty) continue;

  //       final hashIndex = line.indexOf('#');
  //       if (hashIndex <= 0) continue;

  //       final idPart = line.substring(0, hashIndex);
  //       final categoryPart = line.substring(hashIndex + 1);

  //       final id = int.tryParse(idPart);
  //       if (id == null) continue;

  //       await (_commonDB.update(_commonDB.greekWords)
  //             ..where((tbl) => tbl.id.equals(id)))
  //           .write(GreekWordsCompanion(category: Value(categoryPart)));
  //       print(idPart + "; " + categoryPart);
  //     }
  //   });
  // }

  // List<String> getUniqueValuesAfterHash(String filePath) {
  //   final file = File(filePath);

  //   if (!file.existsSync()) {
  //     print('File not found: $filePath');
  //     return [];
  //   }

  //   final lines = file.readAsLinesSync();
  //   final uniqueValues = <String>{};

  //   for (var line in lines) {
  //     final parts = line.split('#');
  //     if (parts.length > 1) {
  //       final value = parts.last.trim();
  //       if (value.isNotEmpty) {
  //         uniqueValues.add(value);
  //       }
  //     }
  //   }

  //   final sortedList = uniqueValues.toList()..sort();
  //   return sortedList;
  // }

  // String stripTags(String html) {
  //   final regExp = RegExp(r'<[^>]*>', multiLine: true, caseSensitive: false);
  //   return html.replaceAll(regExp, '');
  // }

  // Future<void> fetchAndParse() async {
  //   // Create directory for HTML files if it doesn't exist
  //   final htmlDir = Directory('C:/Users/karna/Downloads/html_files');
  //   if (!await htmlDir.exists()) {
  //     await htmlDir.create();
  //   }

  //   // Open output.txt for writing
  //   final file = File('C:/Users/karna/Downloads/output.txt').openWrite();

  //   // Loop through numbers 1 to 5624
  //   for (int number = 2106; number <= 5624; number++) {
  //     // Handle missing numbers
  //     if (number == 2717 || (number >= 3203 && number <= 3302)) {
  //       final line = '$number#';
  //       file.write('$line\n');
  //       print(line);
  //       continue;
  //     }

  //     // Define path for HTML file
  //     final htmlFilePath = path.join(htmlDir.path, '$number.html');
  //     final htmlFile = File(htmlFilePath);
  //     String html;

  //     // Check if HTML file already exists locally
  //     if (await htmlFile.exists()) {
  //       html = await htmlFile.readAsString();
  //     } else {
  //       // Fetch HTML from URL if file doesn't exist
  //       final url = 'https://biblehub.com/greek/$number.htm';
  //       try {
  //         final response = await http.get(Uri.parse(url));
  //         if (response.statusCode == 200) {
  //           html = response.body;
  //           await htmlFile.writeAsString(html); // Save HTML to file
  //         } else {
  //           print('Failed to fetch $url: ${response.statusCode}');
  //           continue;
  //         }
  //       } catch (e) {
  //         print('Error fetching $url: $e');
  //         continue;
  //       }
  //     }

  //     // Parse HTML to extract Part of Speech
  //     final startMarker = 'Part of Speech: </span>';
  //     final endMarker = '<br>';
  //     final startIndex = html.indexOf(startMarker);
  //     if (startIndex != -1) {
  //       final valueStart = startIndex + startMarker.length;
  //       final endIndex = html.indexOf(endMarker, valueStart);
  //       if (endIndex != -1) {
  //         final substring = html.substring(valueStart, endIndex);
  //         final value = stripTags(substring).trim();
  //         final line = '$number#$value';
  //         file.write('$line\n');
  //         print(line);
  //       } else {
  //         print('End marker not found for $number');
  //       }
  //     } else {
  //       print('Start marker not found for $number');
  //     }

  //     // Add delay to avoid overloading the server
  //     await Future.delayed(Duration(seconds: 1));
  //     await file.flush();
  //   }

  //   // Close the output file
  //   await file.flush();
  //   file.close();
  // }

  // Future<void> importDictionaryFromFile(String filePath) async {
  //   final file = File(filePath);
  //   final content = await file.readAsString();

  //   final regex = RegExp(
  //     r'var strongsGreekDictionary = (\{.*\});',
  //     dotAll: true,
  //   );
  //   final match = regex.firstMatch(content);
  //   if (match != null) {
  //     final jsonString = match.group(1)!;
  //     final dictionary = json.decode(jsonString) as Map<String, dynamic>;
  //     for (var entry in dictionary.entries) {
  //       final key = entry.key;
  //       final value = entry.value as Map<String, dynamic>;
  //       final id = int.parse(key.substring(1));
  //       final translit = value['translit'] as String? ?? '';
  //       final strongsDef = value['strongs_def'] as String? ?? '';

  //       final updatedRows =
  //           await (_commonDB.update(_commonDB.greekWords)
  //                 ..where((tbl) => tbl.id.equals(id)))
  //               .write(GreekWordsCompanion(translit: Value(translit)));
  //       if (updatedRows == 0) {
  //         print('Warning: No record found for id $id');
  //       }

  //       await _localizedDB
  //           .into(_localizedDB.greekDescs)
  //           .insert(
  //             GreekDescsCompanion.insert(id: Value(id), desc: strongsDef),
  //           );
  //     }
  //   } else {
  //     print('Error parsing file');
  //   }
  // }

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
