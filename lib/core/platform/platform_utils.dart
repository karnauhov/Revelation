import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'dependent.dart' as dep;
import 'package:revelation/core/logging/common_logger.dart';

bool isDesktop() {
  return [
        TargetPlatform.windows,
        TargetPlatform.linux,
        TargetPlatform.macOS,
      ].contains(defaultTargetPlatform) &&
      !kIsWeb;
}

bool isMobile() {
  return [
        TargetPlatform.android,
        TargetPlatform.iOS,
      ].contains(defaultTargetPlatform) &&
      !kIsWeb;
}

bool isWeb() {
  return kIsWeb;
}

bool isLocalWeb() {
  if (!kIsWeb) {
    return false;
  }
  final host = Uri.base.host;
  return host == 'localhost' || host == '127.0.0.1';
}

bool isMobileBrowser() {
  return dep.isMobileBrowser();
}

String getUserAgent() {
  return dep.getUserAgent();
}

Future<int> fetchMaxTextureSize() {
  return dep.fetchMaxTextureSize();
}

TargetPlatform getPlatform() {
  return defaultTargetPlatform;
}

String getSystemLanguage() {
  var language = 'en';
  try {
    if (isWeb()) {
      language = dep.getPlatformLanguage();
    } else {
      final localeName = Platform.localeName;
      final parts = localeName.split('_');
      if (parts.length == 1) {
        language = Locale(parts[0]).languageCode;
      } else if (parts.length >= 2) {
        language = Locale(parts[0], parts[1]).languageCode;
      } else {
        language = 'en';
      }
    }
  } catch (e) {
    log.debug(e);
  }
  return language;
}
