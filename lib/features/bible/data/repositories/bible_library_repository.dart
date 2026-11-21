import 'dart:convert';

import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/bible_module_connector.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:shared_preferences/shared_preferences.dart';

typedef BiblePreview = ({BibleModuleInfo module, List<BibleVerseText> verses});

/// Shared catalog and selection policy. The preference itself stays in AppSettings.
class BibleLibraryRepository {
  BibleLibraryRepository({
    BibleModuleDataSource dataSource = const LocalBibleModuleDataSource(),
    Future<AppSettings> Function()? loadSettings,
    Future<Map<String, WebDbManifestEntry>> Function()? loadManifest,
    Future<List<BibleModuleInfo>> Function()? readInstalled,
  }) : _dataSource = dataSource,
       _loadSettings = loadSettings ?? SettingsRepository().getSettings,
       _loadManifest = loadManifest ?? readBibleModuleManifest,
       _readInstalled = readInstalled;

  static const _cacheKey = 'bible_module_catalog_v1';
  static final _filePattern = RegExp(r'^bible_[A-Za-z0-9_]+\.sqlite$');
  final BibleModuleDataSource _dataSource;
  final Future<AppSettings> Function() _loadSettings;
  final Future<Map<String, WebDbManifestEntry>> Function() _loadManifest;
  final Future<List<BibleModuleInfo>> Function()? _readInstalled;
  List<BibleModuleInfo>? _catalog;
  Future<List<BibleModuleInfo>>? _refresh;
  Future<List<BibleModuleInfo>>? _initial;
  bool _sessionRefreshStarted = false;

  /// The latest in-memory snapshot, including modules discovered offline.
  List<BibleModuleInfo> get cachedModules => _catalog ?? const [];

  Future<List<BibleModuleInfo>> cachedCatalog() async {
    await (_initial ??= _loadCached());
    return _catalog!;
  }

  Future<List<BibleModuleInfo>> loadCatalog({bool refresh = false}) async {
    await cachedCatalog();
    if (refresh || !_sessionRefreshStarted || _catalog!.isEmpty) {
      return _refreshCatalog();
    }
    final inFlight = _refresh;
    return inFlight == null ? _catalog! : await inFlight;
  }

  Future<List<BibleModuleInfo>> _loadCached() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = jsonDecode(prefs.getString(_cacheKey) ?? '[]') as List;
      _catalog = List.unmodifiable([
        for (final value in raw)
          if (value is Map<String, dynamic> && _validFile(value['file']))
            _fromMap(value['file'] as String, value),
      ]);
    } catch (_) {
      _catalog = const [];
    }
    return _catalog!;
  }

  Future<List<BibleModuleInfo>> _refreshCatalog() {
    _sessionRefreshStarted = true;
    return _refresh ??= _readCatalog().whenComplete(() => _refresh = null);
  }

  Future<List<BibleModuleInfo>> _readCatalog() async {
    final entries = <String, BibleModuleInfo>{};
    final incompatible = <String>{};
    Object? failure;
    try {
      final manifest = await _loadManifest();
      if (manifest.isEmpty) throw StateError('Bible catalog unavailable');
      for (final MapEntry(key: file, value: entry) in manifest.entries) {
        if (!_validFile(file)) continue;
        final version = entry.versionInfo;
        final metadata = entry.bible ?? _legacyMetadata(file);
        if (version.schemaVersion > BibleModuleDB.supportedSchemaVersion ||
            !_compatible(metadata)) {
          incompatible.add(file);
          continue;
        }
        entries[file] = _fromMap(file, {
          ...metadata,
          'schemaVersion': version.schemaVersion,
          'dataVersion': version.dataVersion,
          'date': version.date.toIso8601String(),
        });
      }
    } catch (error) {
      failure = error;
      entries.addAll({for (final info in cachedModules) info.fileName: info});
    }
    List<BibleModuleInfo> installed;
    try {
      installed =
          await (_readInstalled?.call() ??
              _readInstalledModules({...entries.keys, ...incompatible}));
    } catch (_) {
      // An unavailable local storage backend must not discard a valid server catalog.
      installed = const [];
    }
    for (final info in installed) {
      if (_validFile(info.fileName) &&
          !incompatible.contains(info.fileName) &&
          info.language.trim().isNotEmpty &&
          info.canon == 'protestant_66' &&
          info.versification == 'kjv_protestant' &&
          (info.schemaVersion ?? 0) <= BibleModuleDB.supportedSchemaVersion) {
        entries.putIfAbsent(info.fileName, () => info);
      }
    }
    _catalog = List.unmodifiable(
      entries.values.toList()
        ..sort((a, b) => a.displayTitle.compareTo(b.displayTitle)),
    );
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _cacheKey,
      jsonEncode([
        for (final info in _catalog!)
          {
            'file': info.fileName,
            'moduleId': info.moduleId,
            'code': info.code,
            'title': info.title,
            'language': info.language,
            'canon': info.canon,
            'versification': info.versification,
            'role': info.role,
            'schemaVersion': info.schemaVersion,
            'dataVersion': info.dataVersion,
            'date': info.date?.toIso8601String(),
          },
      ]),
    );
    if (failure != null) throw failure;
    return _catalog!;
  }

  Future<String?> preferredModuleFile() async {
    final settings = await _loadSettings();
    return selectModule(await availableCatalog(), settings)?.fileName;
  }

  Future<List<BibleModuleInfo>> availableCatalog() async {
    try {
      return await loadCatalog();
    } catch (_) {
      return cachedModules;
    }
  }

  static BibleModuleInfo? selectModule(
    List<BibleModuleInfo> catalog,
    AppSettings settings,
  ) {
    final translations = catalog.where((module) => module.role != 'original');
    final selected = translations
        .where((module) => module.fileName == settings.defaultBibleModule)
        .firstOrNull;
    if (selected != null) return selected;
    for (final language in [_baseLanguage(settings.selectedLanguage), 'en']) {
      for (final info in translations) {
        if (_baseLanguage(info.language) == language) return info;
      }
    }
    return translations.firstOrNull;
  }

  Future<BiblePreview> loadPreview(
    List<String> verseKeys, {
    String? moduleFile,
  }) async {
    final preferred = moduleFile ?? await preferredModuleFile();
    final catalog = moduleFile == null
        ? await availableCatalog()
        : const <BibleModuleInfo>[];
    final candidates = <String>{
      if (preferred != null) preferred,
      for (final info in catalog)
        if (_baseLanguage(info.language) == 'en' && info.role != 'original')
          info.fileName,
      for (final info in catalog)
        if (info.role != 'original') info.fileName,
    };
    Object? lastError;
    for (final file in candidates) {
      try {
        final database = _dataSource.openModule(file);
        try {
          final verses = await database.readVersesByKeys(verseKeys);
          if (!verses.any((verse) => verse.text.trim().isNotEmpty)) continue;
          // A failed update may leave an older installed revision in use.
          final info = await database.readInfo(
            file,
            includeStrongCapability: false,
          );
          return (
            module: info,
            verses: List<BibleVerseText>.unmodifiable(verses),
          );
        } finally {
          await database.close();
        }
      } catch (error) {
        lastError = error;
      }
    }
    throw StateError('Bible text unavailable: $lastError');
  }

  static bool _validFile(Object? file) =>
      file is String && _filePattern.hasMatch(file);

  static String _baseLanguage(String code) =>
      code.trim().toLowerCase().split(RegExp('[-_]')).first;

  static Future<List<BibleModuleInfo>> _readInstalledModules(
    Set<String> knownFiles,
  ) async {
    final modules = <BibleModuleInfo>[];
    for (final file in await listInstalledBibleModuleFiles(
      exclude: knownFiles,
    )) {
      final executor = openInstalledBibleModuleExecutor(file);
      if (executor == null) continue;
      final database = BibleModuleDB(executor);
      try {
        modules.add(
          await database.readInfo(file, includeStrongCapability: false),
        );
      } catch (_) {
        // Unreadable installed modules are skipped.
      } finally {
        await database.close();
      }
    }
    return modules;
  }

  static bool _compatible(Map<String, dynamic> metadata) =>
      metadata['language'] is String &&
      (metadata['language'] as String).trim().isNotEmpty &&
      (metadata['canon'] == null || metadata['canon'] == 'protestant_66') &&
      (metadata['versification'] == null ||
          metadata['versification'] == 'kjv_protestant');

  static BibleModuleInfo _fromMap(String file, Map<String, dynamic> value) =>
      BibleModuleInfo(
        fileName: file,
        code: value['code'] as String? ?? file,
        moduleId: value['moduleId'] as String? ?? file,
        title: value['title'] as String? ?? file,
        description: '',
        language: value['language'] as String? ?? '',
        canon: value['canon'] as String? ?? '',
        versification: value['versification'] as String? ?? '',
        license: '',
        sourceSummary: '',
        role:
            value['role'] as String? ??
            bibleRoleForLanguage(value['language'] as String? ?? ''),
        schemaVersion: value['schemaVersion'] as int?,
        dataVersion: value['dataVersion'] as int?,
        date: DateTime.tryParse(value['date'] as String? ?? ''),
      );

  // Compatibility for manifests published before catalog metadata was supported.
  static Map<String, String> _legacyMetadata(String file) => switch (file) {
    'bible_kjv.sqlite' => {
      'code': 'KJV',
      'title': 'King James Version',
      'language': 'en',
    },
    'bible_ohienko_1988.sqlite' => {
      'code': 'OH1988',
      'title': 'Огієнко 1988',
      'language': 'uk',
    },
    'bible_lxx_tr.sqlite' => {
      'code': 'LXX/TR',
      'title': 'LXX/TR',
      'language': 'grc',
    },
    _ => {},
  };
}
