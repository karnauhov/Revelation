class LocalDatabaseSyncResult {
  const LocalDatabaseSyncResult({required this.files});

  final List<LocalDatabaseFileSyncResult> files;

  bool get hasUpdates => files.any((file) => file.updated);

  bool get hasSizeMismatch =>
      files.any((file) => file.hasSizeMismatchAfterSync);

  bool get hasValidationFailures =>
      files.any((file) => !file.existsAfterSync || !file.healthyAfterSync);

  bool get isUpToDate =>
      files.isNotEmpty &&
      files.every(
        (file) =>
            !file.updated &&
            file.existsAfterSync &&
            file.healthyAfterSync &&
            !file.hasSizeMismatchAfterSync,
      );
}

class LocalDatabaseFileSyncResult {
  const LocalDatabaseFileSyncResult({
    required this.fileName,
    required this.existedBeforeSync,
    required this.healthyBeforeSync,
    required this.sizeMatchedManifestBeforeSync,
    required this.existsAfterSync,
    required this.healthyAfterSync,
    required this.sizeMatchedManifestAfterSync,
    required this.updated,
    this.expectedSizeBytes,
    this.sizeBytesBeforeSync,
    this.sizeBytesAfterSync,
    this.manifestEntryMissing = false,
  });

  final String fileName;
  final bool existedBeforeSync;
  final bool healthyBeforeSync;
  final bool sizeMatchedManifestBeforeSync;
  final bool existsAfterSync;
  final bool healthyAfterSync;
  final bool sizeMatchedManifestAfterSync;
  final bool updated;
  final int? expectedSizeBytes;
  final int? sizeBytesBeforeSync;
  final int? sizeBytesAfterSync;
  final bool manifestEntryMissing;

  bool get hadSizeMismatchBeforeSync =>
      expectedSizeBytes != null &&
      existedBeforeSync &&
      !sizeMatchedManifestBeforeSync;

  bool get hasSizeMismatchAfterSync =>
      expectedSizeBytes != null && !sizeMatchedManifestAfterSync;
}
