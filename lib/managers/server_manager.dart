import 'dart:typed_data';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ServerManager {
  static final ServerManager _instance = ServerManager._internal();
  ServerManager._internal();

  factory ServerManager() {
    return _instance;
  }

  Future<bool> init() async {
    String supabaseUrl = const String.fromEnvironment('SUPABASE_URL');
    String supabaseKey = const String.fromEnvironment('SUPABASE_KEY');
    if (supabaseUrl.isEmpty || supabaseKey.isEmpty) {
      log.error("Supabase URL or key not found");
      return false;
    } else {
      await Supabase.initialize(url: supabaseUrl, anonKey: supabaseKey);
      log.info("Supabase is initialized");
      return true;
    }
  }

  Future<Uint8List?> downloadDB(String repository, String fileName) async {
    try {
      final Uint8List? fileBytes = await _downloadFile(repository, fileName);
      return fileBytes;
    } catch (e) {
      log.error('DB downloading error: $e');
      return null;
    }
  }

  Future<Uint8List?> downloadImage(String page, bool isMobileWeb) async {
    try {
      final divider = page.indexOf("/");
      final repository = page.substring(0, divider);
      final image = page.substring(divider + 1);

      // Fix image url for mobile browser
      String modifiedImage;
      if (isMobileWeb) {
        final lastDotIndex = image.lastIndexOf('.');
        if (lastDotIndex != -1) {
          modifiedImage =
              '${image.substring(0, lastDotIndex)}${AppConstants.mobileBrowserSuffix}${image.substring(lastDotIndex)}';
        } else {
          modifiedImage = '$image${AppConstants.mobileBrowserSuffix}';
        }
      } else {
        modifiedImage = image;
      }
      final Uint8List? fileBytes = await _downloadFile(
        repository,
        modifiedImage,
      );
      return fileBytes;
    } catch (e) {
      log.error('Image downloading error: $e');
      return null;
    }
  }

  Future<DateTime?> getLastUpdateFileFromServer(
    String repository,
    String filePath,
  ) async {
    try {
      final supabase = Supabase.instance.client;
      _removeWrongHeader(supabase);
      final fileObject = await supabase.storage.from(repository).info(filePath);
      return DateTime.parse(fileObject.lastModified!);
    } catch (e) {
      log.error('Getting file info from server error: $e');
      return null;
    }
  }

  Future<Uint8List?> _downloadFile(String repository, String filePath) async {
    try {
      final supabase = Supabase.instance.client;
      _removeWrongHeader(supabase);
      final Uint8List fileBytes = await supabase.storage
          .from(repository)
          .download(filePath);
      log.info('File $repository/$filePath has been downloaded.');
      return fileBytes;
    } catch (e) {
      log.error('File downloading error: $e');
      return null;
    }
  }

  void _removeWrongHeader(SupabaseClient supabase) {
    // There’s a bug in the headers when they contain Cyrillic (or other non‑Latin) characters
    if (supabase.storage.headers.containsKey(
      "X-Supabase-Client-Platform-Version",
    )) {
      supabase.storage.headers.remove("X-Supabase-Client-Platform-Version");
    }
  }
}
