import 'dart:io';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';

Future<String> collectSystemAndAppInfo({BuildContext? context}) async {
  final buf = StringBuffer();
  final deviceInfo = DeviceInfoPlugin();
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

  // DEVICE INFO (device_info_plus)
  try {
    buf.write("\r\n=======DEVICE INFO=======\r\n");
    if (kIsWeb) {
      final web = await deviceInfo.webBrowserInfo;
      safeWrite('web_userAgent', web.userAgent);
      safeWrite('web_platform', web.platform);
      safeWrite('web_vendor', web.vendor);
      safeWrite('web_language', web.language);
      safeWrite('web_languages', web.languages);
      safeWrite('web_hardwareConcurrency', web.hardwareConcurrency);
      safeWrite('web_maxTouchPoints', web.maxTouchPoints);
      safeWrite('web_product', web.product);
    } else if (Platform.isAndroid) {
      final a = await deviceInfo.androidInfo;
      try {
        final map = a.data;
        map.forEach((k, v) => safeWrite('android.$k', v));
      } catch (_) {
        safeWrite('android.model', a.model);
        safeWrite('android.manufacturer', a.manufacturer);
        safeWrite('android.version.sdkInt', a.version.sdkInt);
        safeWrite('android.version.release', a.version.release);
        safeWrite('android.isPhysicalDevice', a.isPhysicalDevice);
      }
    } else if (Platform.isIOS) {
      final i = await deviceInfo.iosInfo;
      try {
        final map = i.data;
        map.forEach((k, v) => safeWrite('ios.$k', v));
      } catch (_) {
        safeWrite('ios.name', i.name);
        safeWrite('ios.systemName', i.systemName);
        safeWrite('ios.systemVersion', i.systemVersion);
        safeWrite('ios.model', i.model);
        safeWrite('ios.identifierForVendor', i.identifierForVendor);
        safeWrite('ios.utsname.sysname', i.utsname.sysname);
      }
    } else if (Platform.isMacOS) {
      final m = await deviceInfo.macOsInfo;
      try {
        final map = m.data;
        map.forEach((k, v) => safeWrite('macos.$k', v));
      } catch (_) {
        safeWrite('macos.computerName', m.computerName);
        safeWrite('macos.arch', m.arch);
        safeWrite('macos.kernelVersion', m.kernelVersion);
      }
    } else if (Platform.isWindows) {
      final w = await deviceInfo.windowsInfo;
      try {
        final map = w.data;
        map.forEach((k, v) => safeWrite('windows.$k', v));
      } catch (_) {
        safeWrite('windows.computerName', w.computerName);
        safeWrite('windows.numberOfCores', w.numberOfCores);
        safeWrite('windows.systemMemoryInMegabytes', w.systemMemoryInMegabytes);
      }
    } else if (Platform.isLinux) {
      final l = await deviceInfo.linuxInfo;
      try {
        final map = l.data;
        map.forEach((k, v) => safeWrite('linux.$k', v));
      } catch (_) {
        safeWrite('linux.name', l.name);
        safeWrite('linux.version', l.version);
        safeWrite('linux.id', l.id);
      }
    } else {
      safeWrite('deviceInfo', 'unknown platform');
    }
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
