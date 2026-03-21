@Tags(['widget'])
import 'dart:typed_data';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:device_info_plus_platform_interface/device_info_plus_platform_interface.dart';
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
    final info = await collectSystemAndAppInfo(context: context);

    expect(info, contains('=======PLATFORM / DART======='));
    expect(info, contains('=======PACKAGE / APP======='));
    expect(info, contains('appName: Test App'));
    expect(info, contains('packageName: dev.test.app'));
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

    final info = await collectSystemAndAppInfo();

    expect(info, contains('DeviceInfoError'));
    expect(info, contains('=======PACKAGE / APP======='));
  });
}
