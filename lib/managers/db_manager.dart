import 'package:drift/drift.dart';
import 'package:revelation/db/db_common.dart';
import 'package:revelation/db/db_localized.dart';
import 'package:revelation/db/connect/shared.dart';
import 'package:revelation/utils/common.dart';

class DBManager {
  static final DBManager _instance = DBManager._internal();
  DBManager._internal();

  factory DBManager() {
    return _instance;
  }

  String _dbLanguage = 'en';
  bool _isInitialized = false;
  bool _hasLocalizedDb = false;
  late CommonDB _commonDB;
  late LocalizedDB _localizedDB;
  late List<GreekWord> _greekWords;
  late List<GreekDesc> _greekDescs;
  late List<TopicText> _topicTexts;
  late List<Topic> _topics;

  List<GreekWord> get greekWords => _greekWords;
  List<GreekDesc> get greekDescs => _greekDescs;
  List<TopicText> get topicTexts => _topicTexts;
  List<Topic> get topics => _topics;
  String get langDB => _dbLanguage;
  bool get isInitialized => _isInitialized;

  Future<void> init(String language) async {
    _dbLanguage = language;
    _commonDB = getCommonDB();
    _localizedDB = getLocalizedDB(_dbLanguage);
    _hasLocalizedDb = true;
    _greekWords = await _commonDB.select(_commonDB.greekWords).get();
    _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
    _topicTexts = await _localizedDB.select(_localizedDB.topicTexts).get();
    _topics = await getTopics();
    _isInitialized = true;
    log.info("DB is initialized (${language})");
  }

  Future<void> updateLanguage(String newLanguage) async {
    if (!_isInitialized) {
      return;
    }
    if (_dbLanguage != newLanguage) {
      await _localizedDB.close();
      _dbLanguage = newLanguage;
      _localizedDB = getLocalizedDB(_dbLanguage);
      _hasLocalizedDb = true;
      _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
      _topicTexts = await _localizedDB.select(_localizedDB.topicTexts).get();
      _topics = await getTopics();
      log.info("The DB is reinitialized for the new language: ${newLanguage}");
    }
  }

  Future<List<Topic>> getTopics({bool onlyVisible = true}) async {
    if (!_hasLocalizedDb) {
      return [];
    }
    final query = _localizedDB.select(_localizedDB.topics)
      ..orderBy([
        (t) => OrderingTerm(expression: t.sortOrder, mode: OrderingMode.asc),
        (t) => OrderingTerm(expression: t.route, mode: OrderingMode.asc),
      ]);
    if (onlyVisible) {
      query.where((t) => t.isVisible.equals(true));
    }
    return query.get();
  }

  Future<String> getTopicMarkdown(String route) async {
    if (!_isInitialized || route.isEmpty) {
      return "";
    }
    final query = _localizedDB.select(_localizedDB.topicTexts)
      ..where((t) => t.route.equals(route));
    final topic = await query.getSingleOrNull();
    return topic?.markdown ?? "";
  }

  Future<CommonResource?> getCommonResource(String key) async {
    if (!_isInitialized || key.isEmpty) {
      return null;
    }
    final query = _commonDB.select(_commonDB.commonResources)
      ..where((r) => r.key.equals(key));
    return query.getSingleOrNull();
  }

  Future<Uint8List?> getCommonResourceData(String key) async {
    final resource = await getCommonResource(key);
    return resource?.data;
  }
}
