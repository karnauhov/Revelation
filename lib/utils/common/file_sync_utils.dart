import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:revelation/utils/app_constants.dart';

import 'common_logger.dart';

Future<String> getAppFolder() async {
  final directory = await getApplicationDocumentsDirectory();
  return '${directory.path}/${AppConstants.folder}';
}

Future<bool> isUpdateNeeded(String folder, String fileName) async {
  try {
    final loc = await getLastUpdateFileLocal(folder, fileName);
    final serv = await ServerManager().getLastUpdateFileFromServer(
      folder,
      fileName,
    );
    return loc == null ||
        loc.millisecondsSinceEpoch < serv!.millisecondsSinceEpoch;
  } catch (e) {
    log.error('Checking is update needed error: $e');
  }
  return false;
}

Future<String> updateLocalFile(String folder, String filePath) async {
  final appFolder = await getAppFolder();
  final file = File(p.join(appFolder, folder, filePath));

  try {
    final Uint8List? fileBytes = await ServerManager().downloadDB(
      folder,
      filePath,
    );
    if (fileBytes != null) {
      if (file.existsSync()) {
        file.delete();
      }
      await file.create(recursive: true);
      await file.writeAsBytes(fileBytes);
    }
  } catch (e) {
    log.error('Update local file error: $e');
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

