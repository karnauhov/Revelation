import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'dependent.dart' as dep;
import 'package:revelation/core/logging/common_logger.dart';

const MethodChannel _desktopWindowChannel = MethodChannel('revelation/window');
String? _lastDesktopWindowTitle;

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

bool isDesktopWindowChannelSupported() {
  if (kIsWeb) {
    return false;
  }
  return defaultTargetPlatform == TargetPlatform.windows ||
      defaultTargetPlatform == TargetPlatform.linux;
}

bool isLocalWeb() {
  return isLocalWebWith();
}

bool isLocalWebWith({bool? isWebOverride, Uri? uriOverride}) {
  final runningOnWeb = isWebOverride ?? kIsWeb;
  if (!runningOnWeb) {
    return false;
  }
  final host = (uriOverride ?? Uri.base).host;
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
  return getSystemLanguageWith();
}

String getSystemLanguageWith({
  bool? isWebOverride,
  String? localeNameOverride,
  String Function()? platformLanguageProvider,
}) {
  var language = 'en';
  try {
    final runningOnWeb = isWebOverride ?? isWeb();
    if (runningOnWeb) {
      language = (platformLanguageProvider ?? dep.getPlatformLanguage)();
    } else {
      final localeName = localeNameOverride ?? Platform.localeName;
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

Future<bool> setDesktopWindowTitle(String title) async {
  if (!isDesktopWindowChannelSupported()) {
    return false;
  }
  if (_lastDesktopWindowTitle == title) {
    return true;
  }
  try {
    await _desktopWindowChannel.invokeMethod<void>(
      'setWindowTitle',
      <String, String>{'title': title},
    );
    _lastDesktopWindowTitle = title;
    return true;
  } catch (e) {
    log.debug(e);
    return false;
  }
}

Future<bool> closeDesktopWindow() async {
  if (!isDesktopWindowChannelSupported()) {
    return false;
  }
  try {
    await _desktopWindowChannel.invokeMethod<void>('closeWindow');
    return true;
  } catch (e) {
    log.debug(e);
    return false;
  }
}
