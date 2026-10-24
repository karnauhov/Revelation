/// An opening failure after the local application folder has been resolved.
class LocalFolderOpenException implements Exception {
  const LocalFolderOpenException({
    required this.folderPath,
    required this.cause,
  });

  final String folderPath;
  final Object cause;

  @override
  String toString() => 'Unable to open local app folder: $folderPath ($cause)';
}
