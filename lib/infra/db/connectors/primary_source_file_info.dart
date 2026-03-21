class PrimarySourceFileInfo {
  const PrimarySourceFileInfo({
    required this.relativePath,
    this.sizeBytes,
    this.error,
  });

  final String relativePath;
  final int? sizeBytes;
  final String? error;
}
