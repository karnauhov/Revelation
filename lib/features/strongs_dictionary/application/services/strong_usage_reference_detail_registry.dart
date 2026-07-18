class StrongUsageReferenceDetail {
  const StrongUsageReferenceDetail({
    required this.surface,
    required this.count,
    required this.referencesMarkdown,
  });

  final String surface;
  final int count;
  final String referencesMarkdown;
}

class StrongUsageReferenceDetailRegistry {
  StrongUsageReferenceDetailRegistry._();

  static final StrongUsageReferenceDetailRegistry instance =
      StrongUsageReferenceDetailRegistry._();
  static const int _maxEntries = 2048;

  final Map<String, StrongUsageReferenceDetail> _detailsById =
      <String, StrongUsageReferenceDetail>{};
  int _nextId = 0;

  String register(StrongUsageReferenceDetail detail) {
    final id = (++_nextId).toRadixString(36);
    _detailsById[id] = detail;
    if (_detailsById.length > _maxEntries) {
      _detailsById.remove(_detailsById.keys.first);
    }
    return id;
  }

  StrongUsageReferenceDetail? find(String id) => _detailsById[id.trim()];

  void clearForTesting() {
    _detailsById.clear();
    _nextId = 0;
  }
}
