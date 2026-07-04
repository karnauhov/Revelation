import 'package:shared_preferences/shared_preferences.dart';

abstract class BiblePreferencesStore {
  Future<String?> loadLastModuleFile();

  Future<void> saveLastModuleFile(String moduleFile);

  Future<List<String>> loadLastModuleFiles();

  Future<void> saveLastModuleFiles(List<String> moduleFiles);

  Future<String?> loadLastSearchQuery(String moduleFile);

  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  });

  Future<List<String>> loadSearchHistory();

  Future<void> saveSearchHistory(List<String> queries);
}

class SharedPreferencesBiblePreferencesStore implements BiblePreferencesStore {
  const SharedPreferencesBiblePreferencesStore();

  static const String lastModuleFileKey = 'bible.last_module_file';
  static const String lastModuleFilesKey = 'bible.last_module_files';
  static const String searchHistoryKey = 'bible.search.history';
  static const String _lastSearchQueryPrefix = 'bible.search.last_query.';

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

  @override
  Future<List<String>> loadLastModuleFiles() async {
    final preferences = await SharedPreferences.getInstance();
    final values = preferences.getStringList(lastModuleFilesKey);
    if (values == null || values.isEmpty) {
      final singleModuleFile = await loadLastModuleFile();
      return singleModuleFile == null ? const <String>[] : [singleModuleFile];
    }
    return List<String>.unmodifiable(
      values.map((value) => value.trim()).where((value) => value.isNotEmpty),
    );
  }

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {
    final normalized = List<String>.unmodifiable(
      moduleFiles
          .map((moduleFile) => moduleFile.trim())
          .where((moduleFile) => moduleFile.isNotEmpty),
    );
    final preferences = await SharedPreferences.getInstance();
    await preferences.setStringList(lastModuleFilesKey, normalized);
    if (normalized.isNotEmpty) {
      await preferences.setString(lastModuleFileKey, normalized.first);
    }
  }

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async {
    final preferences = await SharedPreferences.getInstance();
    final value = preferences
        .getString(_lastSearchQueryKey(moduleFile))
        ?.trim();
    return value == null || value.isEmpty ? null : value;
  }

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {
    final preferences = await SharedPreferences.getInstance();
    final normalized = query.trim();
    final key = _lastSearchQueryKey(moduleFile);
    if (normalized.isEmpty) {
      await preferences.remove(key);
      return;
    }
    await preferences.setString(key, normalized);
  }

  @override
  Future<List<String>> loadSearchHistory() async {
    final preferences = await SharedPreferences.getInstance();
    final values = preferences.getStringList(searchHistoryKey);
    if (values == null || values.isEmpty) {
      return const <String>[];
    }
    return List<String>.unmodifiable(
      values.map((value) => value.trim()).where((value) => value.isNotEmpty),
    );
  }

  @override
  Future<void> saveSearchHistory(List<String> queries) async {
    final normalized = List<String>.unmodifiable(
      queries.map((query) => query.trim()).where((query) => query.isNotEmpty),
    );
    final preferences = await SharedPreferences.getInstance();
    await preferences.setStringList(searchHistoryKey, normalized);
  }

  String _lastSearchQueryKey(String moduleFile) {
    return '$_lastSearchQueryPrefix${moduleFile.trim()}';
  }
}
