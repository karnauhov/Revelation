@Tags(['widget'])
import 'dart:io';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:device_info_plus_platform_interface/device_info_plus_platform_interface.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus_platform_interface/package_info_data.dart';
import 'package:package_info_plus_platform_interface/package_info_platform_interface.dart';
import 'package:revelation/core/diagnostics/diagnostics_utils.dart';

import '../../test_harness/widget_test_harness.dart';

class _FakeDeviceInfoPlatform extends DeviceInfoPlatform {
  _FakeDeviceInfoPlatform(this.info) : super();

  final BaseDeviceInfo info;

  @override
  Future<BaseDeviceInfo> deviceInfo() async => info;
}

class _FakePackageInfoPlatform extends PackageInfoPlatform {
  _FakePackageInfoPlatform(this.data) : super();

  final PackageInfoData data;

  @override
  Future<PackageInfoData> getAll({String? baseUrl}) async => data;
}

class _ThrowingDeviceInfoPlatform extends DeviceInfoPlatform {
  _ThrowingDeviceInfoPlatform() : super();

  @override
  Future<BaseDeviceInfo> deviceInfo() async {
    throw Exception('device info failed');
  }
}

class _ThrowingPackageInfoPlatform extends PackageInfoPlatform {
  _ThrowingPackageInfoPlatform() : super();

  @override
  Future<PackageInfoData> getAll({String? baseUrl}) async {
    throw Exception('package info failed');
  }
}

Future<DateTime?> _fixedAppBuildTimestampLoader() async {
  return DateTime.utc(2026, 3, 29, 14, 15, 16);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late DeviceInfoPlatform originalDevicePlatform;
  late PackageInfoPlatform originalPackagePlatform;

  final windowsInfo = WindowsDeviceInfo(
    computerName: 'TEST-PC',
    numberOfCores: 8,
    systemMemoryInMegabytes: 4096,
    userName: 'tester',
    majorVersion: 10,
    minorVersion: 0,
    buildNumber: 19045,
    platformId: 2,
    csdVersion: '',
    servicePackMajor: 0,
    servicePackMinor: 0,
    suitMask: 0,
    productType: 1,
    reserved: 0,
    buildLab: 'lab',
    buildLabEx: 'labex',
    digitalProductId: Uint8List(0),
    displayVersion: '22H2',
    editionId: 'Pro',
    installDate: DateTime(2020, 1, 1),
    productId: '00000-00000-0000-AAAAA',
    productName: 'Windows',
    registeredOwner: 'Owner',
    releaseId: '1903',
    deviceId: 'device-id',
  );

  setUp(() {
    originalDevicePlatform = DeviceInfoPlatform.instance;
    originalPackagePlatform = PackageInfoPlatform.instance;
    DeviceInfoPlatform.instance = _FakeDeviceInfoPlatform(windowsInfo);
  });

  tearDown(() {
    DeviceInfoPlatform.instance = originalDevicePlatform;
    PackageInfoPlatform.instance = originalPackagePlatform;
  });

  test('resolveDiagnosticsDevicePlatform matches current runtime platform', () {
    final resolved = resolveDiagnosticsDevicePlatform();

    if (kIsWeb) {
      expect(resolved, DiagnosticsDevicePlatform.web);
      return;
    }

    if (Platform.isAndroid) {
      expect(resolved, DiagnosticsDevicePlatform.android);
      return;
    }
    if (Platform.isIOS) {
      expect(resolved, DiagnosticsDevicePlatform.ios);
      return;
    }
    if (Platform.isMacOS) {
      expect(resolved, DiagnosticsDevicePlatform.macos);
      return;
    }
    if (Platform.isWindows) {
      expect(resolved, DiagnosticsDevicePlatform.windows);
      return;
    }
    if (Platform.isLinux) {
      expect(resolved, DiagnosticsDevicePlatform.linux);
      return;
    }

    expect(resolved, DiagnosticsDevicePlatform.unknown);
  });

  testWidgets('collectSystemAndAppInfo reports package info errors', (_) async {
    DeviceInfoPlatform.instance = _FakeDeviceInfoPlatform(windowsInfo);
    PackageInfoPlatform.instance = _ThrowingPackageInfoPlatform();

    final info = await collectSystemAndAppInfo(
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, contains('PackageInfoError'));
    expect(info, contains('=======PLATFORM / DART======='));
    expect(info, contains('=======DEVICE INFO======='));
  });

  testWidgets('collectSystemAndAppInfo includes app and screen data', (
    tester,
  ) async {
    PackageInfoPlatform.instance = _FakePackageInfoPlatform(
      PackageInfoData(
        appName: 'Test App',
        packageName: 'dev.test.app',
        version: '1.2.3',
        buildNumber: '42',
        buildSignature: 'abc',
      ),
    );

    final context = await pumpLocalizedContext(
      tester,
      locale: const Locale('en'),
    );
    final info = await collectSystemAndAppInfo(
      context: context,
      devicePlatformOverride: DiagnosticsDevicePlatform.windows,
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, contains('=======PLATFORM / DART======='));
    expect(info, contains('=======PACKAGE / APP======='));
    expect(info, contains('appName: Test App'));
    expect(info, contains('packageName: dev.test.app'));
    expect(info, contains('appBuildTimestamp: 2026-03-29T14:15:16.000Z'));
    expect(info, contains('=======DEVICE INFO======='));
    expect(info, contains('windows.numberOfCores: 8'));
    expect(info, contains('windows.productName: Windows'));
    expect(info, isNot(contains('windows.userName:')));
    expect(info, isNot(contains('windows.registeredOwner:')));
    expect(info, isNot(contains('windows.productId:')));
    expect(info, isNot(contains('windows.digitalProductId:')));
    expect(info, isNot(contains('windows.deviceId:')));
    expect(info, contains('=======SCREEN / DISPLAY======='));
    expect(info, contains('screen.logicalWidth'));
    expect(info, contains('=======LOCALE / TIMEZONE======='));
    expect(info, contains('locale: en'));
    expect(info, contains('=======ENVIRONMENT======='));
  });

  testWidgets('collectSystemAndAppInfo appends DB files section', (_) async {
    PackageInfoPlatform.instance = _FakePackageInfoPlatform(
      PackageInfoData(
        appName: 'Test App',
        packageName: 'dev.test.app',
        version: '1.2.3',
        buildNumber: '42',
        buildSignature: 'abc',
      ),
    );

    final info = await collectSystemAndAppInfo(
      dbFilesSection:
          'revelation.sqlite: schema_version=4; data_version=1; date=2026-03-21T00:00:00Z; size=1.0 MB (1048576 bytes)',
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, contains('=======PACKAGE / APP======='));
    expect(info, contains('=======DATA / DB FILES======='));
    expect(
      info,
      contains(
        'revelation.sqlite: schema_version=4; data_version=1; date=2026-03-21T00:00:00Z; size=1.0 MB (1048576 bytes)',
      ),
    );
  });

  testWidgets('collectSystemAndAppInfo skips empty DB files section', (
    _,
  ) async {
    PackageInfoPlatform.instance = _FakePackageInfoPlatform(
      PackageInfoData(
        appName: 'Test App',
        packageName: 'dev.test.app',
        version: '1.2.3',
        buildNumber: '42',
        buildSignature: 'abc',
      ),
    );

    final info = await collectSystemAndAppInfo(
      dbFilesSection: '   \r\n   ',
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, isNot(contains('=======DATA / DB FILES=======')));
  });

  testWidgets(
    'collectSystemAndAppInfo trims db section right side and keeps section order',
    (_) async {
      PackageInfoPlatform.instance = _FakePackageInfoPlatform(
        PackageInfoData(
          appName: 'Test App',
          packageName: 'dev.test.app',
          version: '1.2.3',
          buildNumber: '42',
          buildSignature: 'abc',
        ),
      );

      final info = await collectSystemAndAppInfo(
        dbFilesSection: '  revelation.sqlite: ok   \r\n',
        appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
      );

      final packageSection = info.indexOf('=======PACKAGE / APP=======');
      final dbSection = info.indexOf('=======DATA / DB FILES=======');
      final deviceSection = info.indexOf('=======DEVICE INFO=======');

      expect(packageSection, greaterThanOrEqualTo(0));
      expect(dbSection, greaterThan(packageSection));
      expect(deviceSection, greaterThan(dbSection));
      expect(
        info,
        contains('  revelation.sqlite: ok\r\n\r\n=======DEVICE INFO======='),
      );
      expect(info, isNot(contains('revelation.sqlite: ok   \r\n')));
    },
  );

  testWidgets('collectSystemAndAppInfo reports device info errors', (_) async {
    DeviceInfoPlatform.instance = _ThrowingDeviceInfoPlatform();
    PackageInfoPlatform.instance = _FakePackageInfoPlatform(
      PackageInfoData(
        appName: 'Cached App',
        packageName: 'dev.cached.app',
        version: '9.9.9',
        buildNumber: '99',
        buildSignature: 'cached',
      ),
    );

    final info = await collectSystemAndAppInfo(
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, contains('DeviceInfoError'));
    expect(info, contains('=======PACKAGE / APP======='));
  });

  testWidgets('collectSystemAndAppInfo without context uses dispatcher data', (
    _,
  ) async {
    PackageInfoPlatform.instance = _FakePackageInfoPlatform(
      PackageInfoData(
        appName: 'Test App',
        packageName: 'dev.test.app',
        version: '1.2.3',
        buildNumber: '42',
        buildSignature: 'abc',
      ),
    );

    final info = await collectSystemAndAppInfo(
      appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
    );

    expect(info, contains('=======SCREEN / DISPLAY======='));
    expect(
      info,
      anyOf(
        contains('screen.physicalWidth'),
        contains('screenInfo: implicitView is not available'),
      ),
    );
    expect(info, contains('=======LOCALE / TIMEZONE======='));
    expect(info, contains('locale:'));
  });

  testWidgets(
    'collectSystemAndAppInfo reports screen and locale errors for deactivated context',
    (tester) async {
      PackageInfoPlatform.instance = _FakePackageInfoPlatform(
        PackageInfoData(
          appName: 'Test App',
          packageName: 'dev.test.app',
          version: '1.2.3',
          buildNumber: '42',
          buildSignature: 'abc',
        ),
      );

      final staleContext = await pumpLocalizedContext(
        tester,
        locale: const Locale('en'),
      );
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();

      final info = await collectSystemAndAppInfo(
        context: staleContext,
        appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
      );

      expect(info, contains('ScreenInfoError'));
      expect(info, contains('LocaleOrTimezoneError'));
      expect(info, contains('=======ENVIRONMENT======='));
    },
  );

  testWidgets(
    'collectSystemAndAppInfo supports android/ios/macos/linux/web branches',
    (_) async {
      PackageInfoPlatform.instance = _FakePackageInfoPlatform(
        PackageInfoData(
          appName: 'Test App',
          packageName: 'dev.test.app',
          version: '1.2.3',
          buildNumber: '42',
          buildSignature: 'abc',
        ),
      );

      final plugin = DeviceInfoPlugin.setMockInitialValues(
        androidDeviceInfo: AndroidDeviceInfo.setMockInitialValues(
          version: AndroidBuildVersion.setMockInitialValues(
            codename: 'REL',
            incremental: '123',
            previewSdkInt: 0,
            release: '14',
            sdkInt: 34,
          ),
          board: 'board',
          bootloader: 'boot',
          brand: 'brand',
          device: 'device',
          display: 'display',
          fingerprint: 'fingerprint',
          hardware: 'hardware',
          host: 'host',
          id: 'id',
          manufacturer: 'manufacturer',
          model: 'pixel',
          product: 'product',
          name: 'name',
          supported32BitAbis: const <String>[],
          supported64BitAbis: const <String>[],
          supportedAbis: const <String>[],
          tags: 'tags',
          type: 'user',
          isPhysicalDevice: true,
          freeDiskSize: 1,
          totalDiskSize: 2,
          systemFeatures: const <String>[],
          isLowRamDevice: false,
          physicalRamSize: 3,
          availableRamSize: 2,
        ),
        iosDeviceInfo: IosDeviceInfo.setMockInitialValues(
          name: 'iPhone',
          systemName: 'iOS',
          systemVersion: '17.0',
          model: 'iPhone',
          modelName: 'iPhone 15',
          localizedModel: 'iPhone',
          freeDiskSize: 1,
          totalDiskSize: 2,
          identifierForVendor: 'id',
          isPhysicalDevice: true,
          isiOSAppOnMac: false,
          physicalRamSize: 3,
          availableRamSize: 2,
          utsname: IosUtsname.setMockInitialValues(
            sysname: 'Darwin',
            nodename: 'node',
            release: 'release',
            version: 'version',
            machine: 'iPhone16,1',
          ),
        ),
        macOsDeviceInfo: MacOsDeviceInfo.setMockInitialValues(
          computerName: 'Mac',
          hostName: 'host',
          arch: 'arm64',
          model: 'Mac16,1',
          modelName: 'MacBook',
          kernelVersion: 'kernel',
          osRelease: '15.0',
          majorVersion: 15,
          minorVersion: 0,
          patchVersion: 1,
          activeCPUs: 8,
          memorySize: 8192,
          cpuFrequency: 1,
          systemGUID: 'guid',
        ),
        linuxDeviceInfo: LinuxDeviceInfo(
          name: 'Ubuntu',
          version: '24.04',
          id: 'ubuntu',
          prettyName: 'Ubuntu 24.04',
          machineId: 'machine',
        ),
        webBrowserInfo: WebBrowserInfo(
          appCodeName: 'Mozilla',
          appName: 'Netscape',
          appVersion: '5.0',
          deviceMemory: 8,
          language: 'en',
          languages: const <String>['en'],
          platform: 'Win32',
          product: 'Gecko',
          productSub: '20030107',
          userAgent:
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
          vendor: 'Google Inc.',
          vendorSub: '',
          maxTouchPoints: 0,
          hardwareConcurrency: 8,
        ),
        windowsDeviceInfo: windowsInfo,
      );

      final checks = <DiagnosticsDevicePlatform, String>{
        DiagnosticsDevicePlatform.android: 'android.model: pixel',
        DiagnosticsDevicePlatform.ios: 'ios.systemName: iOS',
        DiagnosticsDevicePlatform.macos: 'macos.arch: arm64',
        DiagnosticsDevicePlatform.linux: 'linux.name: Ubuntu',
        DiagnosticsDevicePlatform.web: 'web_platform: Win32',
        DiagnosticsDevicePlatform.unknown: 'deviceInfo: unknown platform',
      };

      for (final entry in checks.entries) {
        final info = await collectSystemAndAppInfo(
          deviceInfoPlugin: plugin,
          devicePlatformOverride: entry.key,
          appBuildTimestampLoader: _fixedAppBuildTimestampLoader,
        );
        expect(info, contains(entry.value));
      }
    },
  );
}
