import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';

void main() {
  test('load fills version, build number and changelog on success', () async {
    final cubit = AboutCubit(
      autoLoad: false,
      packageInfoLoader: () async =>
          _buildPackageInfo(version: '1.2.3', buildNumber: '45'),
      changelogLoader: () async => '# Changelog',
    );
    addTearDown(cubit.close);

    await cubit.load();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNull);
    expect(cubit.state.appVersion, '1.2.3');
    expect(cubit.state.buildNumber, '45');
    expect(cubit.state.changelog, '# Changelog');
  });

  test(
    'load emits dataSource failure when package info loading fails',
    () async {
      final cubit = AboutCubit(
        autoLoad: false,
        packageInfoLoader: () async => throw StateError('forced failure'),
        changelogLoader: () async => '# Changelog',
      );
      addTearDown(cubit.close);

      await cubit.load();

      expect(cubit.state.isLoading, isFalse);
      expect(
        cubit.state.failure,
        const AppFailure.dataSource('Unable to load about screen data.'),
      );
    },
  );

  test('expansion flags update independently', () async {
    final cubit = AboutCubit(
      autoLoad: false,
      packageInfoLoader: () async =>
          _buildPackageInfo(version: '0.0.0', buildNumber: '0'),
      changelogLoader: () async => '',
    );
    addTearDown(cubit.close);

    cubit.setChangelogExpanded(true);
    cubit.setAcknowledgementsExpanded(true);
    cubit.setRecommendedExpanded(true);

    expect(cubit.state.isChangelogExpanded, isTrue);
    expect(cubit.state.isAcknowledgementsExpanded, isTrue);
    expect(cubit.state.isRecommendedExpanded, isTrue);
  });

  test(
    'load returns safely when cubit is closed before await completes',
    () async {
      final packageInfoCompleter = Completer<PackageInfo>();
      var changelogLoaderCalled = false;
      final cubit = AboutCubit(
        autoLoad: false,
        packageInfoLoader: () => packageInfoCompleter.future,
        changelogLoader: () async {
          changelogLoaderCalled = true;
          return '# Changelog';
        },
      );

      final loadFuture = cubit.load();
      await Future<void>.delayed(Duration.zero);
      await cubit.close();

      packageInfoCompleter.complete(
        _buildPackageInfo(version: '1.2.3', buildNumber: '45'),
      );
      await loadFuture;

      expect(cubit.isClosed, isTrue);
      expect(changelogLoaderCalled, isFalse);
    },
  );
}

PackageInfo _buildPackageInfo({
  required String version,
  required String buildNumber,
}) {
  return PackageInfo(
    appName: 'Revelation',
    packageName: 'revelation.app',
    version: version,
    buildNumber: buildNumber,
  );
}
