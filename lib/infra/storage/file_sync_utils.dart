import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:revelation/shared/config/app_constants.dart';

import 'package:revelation/core/logging/common_logger.dart';

typedef LocalFileValidator = bool Function(File file);

const _databaseFolder = 'db';
const _databaseManifestFile = 'manifest.json';

Future<String> getAppFolder() async {
  final directory = await getApplicationDocumentsDirectory();
  return p.join(directory.path, AppConstants.folder);
}

Future<bool> isUpdateNeeded(
  String folder,
  String fileName, {
  bool force = false,
  LocalFileValidator? localFileValidator,
}) async {
  if (force) {
    return true;
  }

  try {
    final localFile = await _getLocalFile(folder, fileName);
    if (!localFile.existsSync()) {
      return true;
    }
    if (localFileValidator != null && !localFileValidator(localFile)) {
      return true;
    }

    final remoteInfo = await ServerManager().getFileInfoFromServer(
      folder,
      fileName,
    );
    if (remoteInfo == null) {
      return false;
    }

    final localStat = localFile.statSync();
    final remoteSize = remoteInfo.sizeBytes;
    if (remoteSize != null && localStat.size != remoteSize) {
      return true;
    }

    return localStat.modified.millisecondsSinceEpoch <
        remoteInfo.updatedAt.millisecondsSinceEpoch;
  } catch (e) {
    log.error('Checking is update needed error: $e');
  }
  return false;
}

Future<String> updateLocalFile(
  String folder,
  String filePath, {
  int? expectedSizeBytes,
  LocalFileValidator? downloadedFileValidator,
  bool refreshDbManifest = true,
}) async {
  final appFolder = await getAppFolder();
  final file = File(p.join(appFolder, folder, filePath));
  final tempFile = File('${file.path}.download');
  var didReplaceFile = false;

  try {
    final Uint8List? fileBytes = await ServerManager().downloadDB(
      folder,
      filePath,
    );
    if (fileBytes != null) {
      if (expectedSizeBytes != null && fileBytes.length != expectedSizeBytes) {
        log.error(
          'Downloaded file size mismatch for $folder/$filePath: '
          '${fileBytes.length} != $expectedSizeBytes',
        );
        return file.path;
      }
      if (tempFile.existsSync()) {
        tempFile.deleteSync();
      }
      await tempFile.create(recursive: true);
      await tempFile.writeAsBytes(fileBytes, flush: true);
      if (downloadedFileValidator != null &&
          !downloadedFileValidator(tempFile)) {
        log.error('Downloaded file validation failed for $folder/$filePath');
        if (tempFile.existsSync()) {
          tempFile.deleteSync();
        }
        return file.path;
      }
      if (file.existsSync()) {
        await file.delete();
      }
      await tempFile.rename(file.path);
      didReplaceFile = true;
    }
  } catch (e) {
    log.error('Update local file error: $e');
    if (tempFile.existsSync()) {
      try {
        tempFile.deleteSync();
      } catch (_) {}
    }
  }

  if (didReplaceFile && refreshDbManifest) {
    await _refreshLocalDbManifestIfNeeded(folder, filePath);
  }

  return file.path;
}

Future<DateTime?> getLastUpdateFileLocal(String folder, String filePath) async {
  try {
    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, folder, filePath));
    if (file.existsSync()) {
      return file.lastModifiedSync();
    } else {
      return null;
    }
  } catch (e) {
    log.error('Getting file info local error: $e');
    return null;
  }
}

Future<File> _getLocalFile(String folder, String filePath) async {
  final appFolder = await getAppFolder();
  return File(p.join(appFolder, folder, filePath));
}

Future<void> _refreshLocalDbManifestIfNeeded(
  String folder,
  String filePath,
) async {
  if (!_shouldRefreshLocalDbManifest(folder, filePath)) {
    return;
  }

  try {
    await updateLocalFile(
      _databaseFolder,
      _databaseManifestFile,
      refreshDbManifest: false,
    );
  } catch (e) {
    log.error('Update local database manifest error: $e');
  }
}

bool _shouldRefreshLocalDbManifest(String folder, String filePath) {
  if (folder != _databaseFolder) {
    return false;
  }
  return p.normalize(filePath).replaceAll('\\', '/') != _databaseManifestFile;
}
