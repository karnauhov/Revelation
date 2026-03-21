import 'dart:io';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';

enum DiagnosticsDevicePlatform {
  web,
  android,
  ios,
  macos,
  windows,
  linux,
  unknown,
}

DiagnosticsDevicePlatform resolveDiagnosticsDevicePlatform() {
  if (kIsWeb) {
    return DiagnosticsDevicePlatform.web;
  }
  if (Platform.isAndroid) {
    return DiagnosticsDevicePlatform.android;
  }
  if (Platform.isIOS) {
    return DiagnosticsDevicePlatform.ios;
  }
  if (Platform.isMacOS) {
    return DiagnosticsDevicePlatform.macos;
  }
  if (Platform.isWindows) {
    return DiagnosticsDevicePlatform.windows;
  }
  if (Platform.isLinux) {
    return DiagnosticsDevicePlatform.linux;
  }
  return DiagnosticsDevicePlatform.unknown;
}

Future<String> collectSystemAndAppInfo({
  BuildContext? context,
  String? dbFilesSection,
  DeviceInfoPlugin? deviceInfoPlugin,
  DiagnosticsDevicePlatform? devicePlatformOverride,
}) async {
  final buf = StringBuffer();
  final deviceInfo = deviceInfoPlugin ?? DeviceInfoPlugin();
  void safeWrite(String key, Object? value) {
    buf.writeln('$key: ${value ?? "null"}');
  }

  // PLATFORM / DART
  try {
    buf.write("=======PLATFORM / DART=======\r\n");
    safeWrite('IsWeb', kIsWeb);
    safeWrite('Platform.operatingSystem', Platform.operatingSystem);
    safeWrite(
      'Platform.operatingSystemVersion',
      Platform.operatingSystemVersion,
    );
    safeWrite('dartVersion', Platform.version);
    safeWrite('isAndroid', Platform.isAndroid);
    safeWrite('isIOS', Platform.isIOS);
    safeWrite('isMacOS', Platform.isMacOS);
    safeWrite('isWindows', Platform.isWindows);
    safeWrite('isLinux', Platform.isLinux);
  } catch (e) {
    safeWrite('PlatformInfoError', e);
  }

  // PACKAGE / APP
  try {
    buf.write("\r\n=======PACKAGE / APP=======\r\n");
    final pkg = await PackageInfo.fromPlatform();
    safeWrite('appName', pkg.appName);
    safeWrite('packageName', pkg.packageName);
    safeWrite('version', pkg.version);
    safeWrite('buildNumber', pkg.buildNumber);
    safeWrite('buildSignature', pkg.buildSignature);
  } catch (e) {
    safeWrite('PackageInfoError', e);
  }

  // DATA / DB FILES
  if (dbFilesSection != null && dbFilesSection.trim().isNotEmpty) {
    buf.write("\r\n=======DATA / DB FILES=======\r\n");
    buf.write(dbFilesSection.trimRight());
    buf.write("\r\n");
  }

  // DEVICE INFO (device_info_plus)
  try {
    buf.write("\r\n=======DEVICE INFO=======\r\n");
    final devicePlatform =
        devicePlatformOverride ?? resolveDiagnosticsDevicePlatform();
    await _writeDeviceInfoForPlatform(
      deviceInfo: deviceInfo,
      platform: devicePlatform,
      safeWrite: safeWrite,
    );
  } catch (e) {
    safeWrite('DeviceInfoError', e);
  }

  // SCREEN / DISPLAY
  try {
    buf.write("\r\n=======SCREEN / DISPLAY=======\r\n");
    if (context != null) {
      // ignore: use_build_context_synchronously
      final mq = MediaQuery.of(context);
      safeWrite('screen.logicalWidth', mq.size.width);
      safeWrite('screen.logicalHeight', mq.size.height);
      safeWrite('screen.devicePixelRatio', mq.devicePixelRatio);
      safeWrite('screen.orientation', mq.orientation.toString());
    } else {
      final dispatcher = PlatformDispatcher.instance;
      final view = dispatcher.implicitView;
      if (view != null) {
        safeWrite('screen.physicalWidth', view.physicalSize.width);
        safeWrite('screen.physicalHeight', view.physicalSize.height);
        safeWrite('screen.devicePixelRatio', view.devicePixelRatio);
      } else {
        safeWrite('screenInfo', 'implicitView is not available');
      }
    }
  } catch (e) {
    safeWrite('ScreenInfoError', e);
  }

  // LOCALE / TIMEZONE
  try {
    buf.write("\r\n=======LOCALE / TIMEZONE=======\r\n");
    String? locale;
    if (context != null) {
      // ignore: use_build_context_synchronously
      locale = Localizations.localeOf(context).toString();
    } else {
      locale = PlatformDispatcher.instance.locale.toString();
    }
    safeWrite('locale', locale);
    safeWrite('timeZoneName', DateTime.now().timeZoneName);
    safeWrite('timeZoneOffset', DateTime.now().timeZoneOffset.toString());
  } catch (e) {
    safeWrite('LocaleOrTimezoneError', e);
  }

  // ENVIRONMENT (Debug / Release)
  try {
    buf.write("\r\n=======ENVIRONMENT=======\r\n");
    var isDebug = false;
    assert(() {
      isDebug = true;
      return true;
    }());
    safeWrite('buildMode.isDebug', isDebug);
  } catch (e) {
    safeWrite('BuildModeError', e);
  }

  return buf.toString();
}

Future<void> _writeDeviceInfoForPlatform({
  required DeviceInfoPlugin deviceInfo,
  required DiagnosticsDevicePlatform platform,
  required void Function(String key, Object? value) safeWrite,
}) async {
  switch (platform) {
    case DiagnosticsDevicePlatform.web:
      final web = await deviceInfo.webBrowserInfo;
      safeWrite('web_browserName', web.browserName.name);
      safeWrite('web_platform', web.platform);
      safeWrite('web_language', web.language);
      break;
    case DiagnosticsDevicePlatform.android:
      final a = await deviceInfo.androidInfo;
      safeWrite('android.model', a.model);
      safeWrite('android.manufacturer', a.manufacturer);
      safeWrite('android.brand', a.brand);
      safeWrite('android.version.sdkInt', a.version.sdkInt);
      safeWrite('android.version.release', a.version.release);
      safeWrite('android.isPhysicalDevice', a.isPhysicalDevice);
      break;
    case DiagnosticsDevicePlatform.ios:
      final i = await deviceInfo.iosInfo;
      safeWrite('ios.systemName', i.systemName);
      safeWrite('ios.systemVersion', i.systemVersion);
      safeWrite('ios.model', i.model);
      safeWrite('ios.localizedModel', i.localizedModel);
      safeWrite('ios.isPhysicalDevice', i.isPhysicalDevice);
      safeWrite('ios.utsname.machine', i.utsname.machine);
      break;
    case DiagnosticsDevicePlatform.macos:
      final m = await deviceInfo.macOsInfo;
      safeWrite('macos.arch', m.arch);
      safeWrite('macos.model', m.model);
      safeWrite('macos.kernelVersion', m.kernelVersion);
      safeWrite('macos.osRelease', m.osRelease);
      safeWrite('macos.activeCPUs', m.activeCPUs);
      safeWrite('macos.memorySize', m.memorySize);
      break;
    case DiagnosticsDevicePlatform.windows:
      final w = await deviceInfo.windowsInfo;
      safeWrite('windows.numberOfCores', w.numberOfCores);
      safeWrite('windows.systemMemoryInMegabytes', w.systemMemoryInMegabytes);
      safeWrite('windows.majorVersion', w.majorVersion);
      safeWrite('windows.minorVersion', w.minorVersion);
      safeWrite('windows.buildNumber', w.buildNumber);
      safeWrite('windows.displayVersion', w.displayVersion);
      safeWrite('windows.productName', w.productName);
      safeWrite('windows.editionId', w.editionId);
      break;
    case DiagnosticsDevicePlatform.linux:
      final l = await deviceInfo.linuxInfo;
      safeWrite('linux.name', l.name);
      safeWrite('linux.version', l.version);
      safeWrite('linux.id', l.id);
      break;
    case DiagnosticsDevicePlatform.unknown:
      safeWrite('deviceInfo', 'unknown platform');
      break;
  }
}
