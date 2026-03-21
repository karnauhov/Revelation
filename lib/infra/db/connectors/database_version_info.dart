class DatabaseVersionInfo {
  const DatabaseVersionInfo({
    required this.schemaVersion,
    required this.dataVersion,
    required this.date,
  });

  final int schemaVersion;
  final int dataVersion;
  final DateTime date;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is DatabaseVersionInfo &&
            runtimeType == other.runtimeType &&
            schemaVersion == other.schemaVersion &&
            dataVersion == other.dataVersion &&
            date == other.date;
  }

  @override
  int get hashCode => Object.hash(schemaVersion, dataVersion, date);
}
