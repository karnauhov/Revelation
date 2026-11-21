import 'package:sqlite3/common.dart';

const catalogDate = '2026-11-19T00:00:00Z';

void populateCatalogModule(CommonDatabase db, String language, int revision) {
  db.execute('PRAGMA user_version=3');
  db.execute('CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT)');
  db.execute(
    "INSERT INTO db_metadata VALUES ('schema_version','3'),('data_version',?),('date',?)",
    ['$revision', catalogDate],
  );
  db.execute(
    'CREATE TABLE info(code TEXT, module_id TEXT, title TEXT, description TEXT, '
    'language TEXT, canon TEXT, versification TEXT, license TEXT, source_summary TEXT)',
  );
  db.execute(
    "INSERT INTO info VALUES (?,?,?,'',?,'protestant_66','kjv_protestant','','')",
    [language.toUpperCase(), language, 'Test $language', language],
  );
  db.execute('CREATE TABLE verses(verse_key TEXT PRIMARY KEY,text TEXT)');
  db.execute("INSERT INTO verses VALUES ('001',?)", [
    'Test $language $revision',
  ]);
}
