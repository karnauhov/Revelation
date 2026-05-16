import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import '../../scripts/prepare_sentry_web_source_maps.dart';

void main() {
  test(
    'adds sourcesContent for package, package root, sdk, and app sources',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'prepare_sentry_web_source_maps_test_',
      );
      addTearDown(() => tempDir.delete(recursive: true));

      final repoDir = Directory.fromUri(tempDir.uri.resolve('repo/'))
        ..createSync(recursive: true);
      final dartToolDir = Directory.fromUri(repoDir.uri.resolve('.dart_tool/'))
        ..createSync(recursive: true);
      final packageDir = Directory.fromUri(tempDir.uri.resolve('pkg/'))
        ..createSync(recursive: true);
      final sdkDir = Directory.fromUri(tempDir.uri.resolve('dart-sdk/'))
        ..createSync(recursive: true);
      final webBuildDir = Directory.fromUri(repoDir.uri.resolve('build/web/'))
        ..createSync(recursive: true);

      final packageConfigFile =
          File.fromUri(dartToolDir.uri.resolve('package_config.json'))
            ..writeAsStringSync(
              jsonEncode({
                'configVersion': 2,
                'packages': [
                  {
                    'name': 'example_pkg',
                    'rootUri': '../../pkg',
                    'packageUri': 'lib/',
                  },
                ],
              }),
            );

      File.fromUri(packageDir.uri.resolve('lib/src/library.dart'))
        ..createSync(recursive: true)
        ..writeAsStringSync('library source');
      File.fromUri(packageDir.uri.resolve('web/worker.dart'))
        ..createSync(recursive: true)
        ..writeAsStringSync('worker source');
      File.fromUri(sdkDir.uri.resolve('lib/core/errors.dart'))
        ..createSync(recursive: true)
        ..writeAsStringSync('sdk source');
      File.fromUri(repoDir.uri.resolve('lib/main.dart'))
        ..createSync(recursive: true)
        ..writeAsStringSync('app source');

      final sourceMapFile =
          File.fromUri(webBuildDir.uri.resolve('main.dart.js.map'))
            ..writeAsStringSync(
              jsonEncode({
                'version': 3,
                'file': 'main.dart.js',
                'sources': [
                  'package:example_pkg/src/library.dart',
                  'package:example_pkg/web/worker.dart',
                  'org-dartlang-sdk:///lib/core/errors.dart',
                  '../../lib/main.dart',
                ],
                'names': [],
                'mappings': '',
              }),
            );

      final summary = await prepareSentryWebSourceMaps(
        PrepareSentryWebSourceMapsOptions(
          webBuildDir: webBuildDir,
          packageConfigFile: packageConfigFile,
          dartSdkDir: sdkDir,
        ),
      );

      expect(summary.updatedFiles, 1);
      expect(summary.resolvedSources, 4);
      expect(summary.missingSources, isEmpty);

      final updated = jsonDecode(await sourceMapFile.readAsString()) as Map;
      expect(updated['sourcesContent'], [
        'library source',
        'worker source',
        'sdk source',
        'app source',
      ]);
    },
  );

  test('records missing sources as null content', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'prepare_sentry_web_source_maps_missing_test_',
    );
    addTearDown(() => tempDir.delete(recursive: true));

    final repoDir = Directory.fromUri(tempDir.uri.resolve('repo/'))
      ..createSync(recursive: true);
    final dartToolDir = Directory.fromUri(repoDir.uri.resolve('.dart_tool/'))
      ..createSync(recursive: true);
    final webBuildDir = Directory.fromUri(repoDir.uri.resolve('build/web/'))
      ..createSync(recursive: true);
    final sdkDir = Directory.fromUri(tempDir.uri.resolve('dart-sdk/'))
      ..createSync(recursive: true);

    final packageConfigFile =
        File.fromUri(dartToolDir.uri.resolve('package_config.json'))
          ..writeAsStringSync(
            jsonEncode({'configVersion': 2, 'packages': <Object?>[]}),
          );

    final sourceMapFile =
        File.fromUri(webBuildDir.uri.resolve('drift_worker.js.map'))
          ..writeAsStringSync(
            jsonEncode({
              'version': 3,
              'file': 'drift_worker.js',
              'sources': ['package:missing_pkg/src/file.dart'],
              'names': [],
              'mappings': '',
            }),
          );

    final summary = await prepareSentryWebSourceMaps(
      PrepareSentryWebSourceMapsOptions(
        webBuildDir: webBuildDir,
        packageConfigFile: packageConfigFile,
        dartSdkDir: sdkDir,
      ),
    );

    expect(summary.updatedFiles, 1);
    expect(summary.resolvedSources, 0);
    expect(summary.missingSources, hasLength(1));
    expect(
      summary.missingSources.single.source,
      'package:missing_pkg/src/file.dart',
    );

    final updated = jsonDecode(await sourceMapFile.readAsString()) as Map;
    expect(updated['sourcesContent'], [null]);
  });
}
