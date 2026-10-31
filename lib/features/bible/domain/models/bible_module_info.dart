class BibleModuleInfo {
  const BibleModuleInfo({
    required this.fileName,
    required this.code,
    required this.moduleId,
    required this.title,
    required this.description,
    required this.language,
    required this.canon,
    required this.versification,
    required this.license,
    required this.sourceSummary,
    this.hasStrongNumbers = false,
    this.schemaVersion,
    this.dataVersion,
    this.date,
  });

  final String fileName;
  final String code;
  final String moduleId;
  final String title;
  final String description;
  final String language;
  final String canon;
  final String versification;
  final String license;
  final String sourceSummary;

  /// Whether the module contains Strong tokens in any verse, not just this chapter.
  final bool hasStrongNumbers;
  final int? schemaVersion;
  final int? dataVersion;
  final DateTime? date;

  String get displayTitle => code.trim().isEmpty ? title : code;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleModuleInfo &&
            other.fileName == fileName &&
            other.code == code &&
            other.moduleId == moduleId &&
            other.title == title &&
            other.description == description &&
            other.language == language &&
            other.canon == canon &&
            other.versification == versification &&
            other.license == license &&
            other.sourceSummary == sourceSummary &&
            other.hasStrongNumbers == hasStrongNumbers &&
            other.schemaVersion == schemaVersion &&
            other.dataVersion == dataVersion &&
            other.date == date;
  }

  @override
  int get hashCode => Object.hash(
    fileName,
    code,
    moduleId,
    title,
    description,
    language,
    canon,
    versification,
    license,
    sourceSummary,
    hasStrongNumbers,
    schemaVersion,
    dataVersion,
    date,
  );
}
