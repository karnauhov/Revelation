import 'package:shared_preferences/shared_preferences.dart';

abstract class BiblePreferencesStore {
  Future<String?> loadLastModuleFile();

  Future<void> saveLastModuleFile(String moduleFile);
}

class SharedPreferencesBiblePreferencesStore implements BiblePreferencesStore {
  const SharedPreferencesBiblePreferencesStore();

  static const String lastModuleFileKey = 'bible.last_module_file';

  @override
  Future<String?> loadLastModuleFile() async {
    final preferences = await SharedPreferences.getInstance();
    final value = preferences.getString(lastModuleFileKey)?.trim();
    return value == null || value.isEmpty ? null : value;
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(lastModuleFileKey, moduleFile);
  }
}
