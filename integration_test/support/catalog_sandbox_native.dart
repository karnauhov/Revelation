import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:path_provider_windows/path_provider_windows.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_platform_interface.dart';
import 'package:shared_preferences_windows/shared_preferences_windows.dart';
import 'package:sqlite3/sqlite3.dart';
import 'catalog_sqlite_fixture.dart';

class CatalogSandbox extends PathProviderPlatform {
  CatalogSandbox._(this.folder, this._original);
  final Directory folder;
  final PathProviderPlatform _original;
  final _originalPreferences = SharedPreferencesStorePlatform.instance;
  static Future<CatalogSandbox> create() async {
    final sandbox = CatalogSandbox._(
      await Directory.systemTemp.createTemp('rev113_catalog_'),
      PathProviderPlatform.instance,
    );
    PathProviderPlatform.instance = sandbox;
    sandbox.reopenPreferences();
    return sandbox;
  }

  @override
  Future<String?> getApplicationDocumentsPath() async => folder.path;
  @override
  Future<String?> getApplicationSupportPath() async => folder.path;

  void reopenPreferences() {
    // The Windows preferences plugin instantiates PathProviderWindows directly.
    if (Platform.isWindows) {
      SharedPreferencesStorePlatform.instance = SharedPreferencesWindows()
        ..pathProvider = _TemporaryWindowsSupport(folder.path);
    }
  }

  Future<Uint8List> moduleBytes(String language, int revision) async {
    final file = File(p.join(folder.path, '${language}_$revision.sqlite'));
    final db = sqlite3.open(file.path);
    try {
      populateCatalogModule(db, language, revision);
    } finally {
      db.dispose();
    }
    return file.readAsBytes();
  }

  Future<void> forgetCatalogManifest() async {
    final file = File(p.join(await getAppFolder(), 'db', 'manifest.json'));
    if (await file.exists()) await file.delete();
  }

  Future<void> dispose(List<String> files) async {
    PathProviderPlatform.instance = _original;
    SharedPreferencesStorePlatform.instance = _originalPreferences;
    await folder.delete(recursive: true);
  }
}

class _TemporaryWindowsSupport extends PathProviderWindows {
  _TemporaryWindowsSupport(this.root);
  final String root;
  @override
  Future<String?> getApplicationSupportPath() async => root;
}
