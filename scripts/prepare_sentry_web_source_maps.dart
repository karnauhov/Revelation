import 'dart:convert';
import 'dart:io';

Future<void> main(List<String> args) async {
  final options = PrepareSentryWebSourceMapsOptions.fromArgs(args);
  final summary = await prepareSentryWebSourceMaps(options);

  stdout.writeln(
    'Prepared ${summary.updatedFiles} source map(s); '
    'resolved ${summary.resolvedSources} source(s).',
  );

  if (summary.ignorableMissingSources.isNotEmpty) {
    stderr.writeln(
      'Ignored missing source content for '
      '${summary.ignorableMissingSources.length} source(s):',
    );
    for (final missing in summary.ignorableMissingSources.take(20)) {
      stderr.writeln('  ${missing.sourceMapPath}: ${missing.source}');
    }
    if (summary.ignorableMissingSources.length > 20) {
      stderr.writeln(
        '  ...and ${summary.ignorableMissingSources.length - 20} more ignored source(s).',
      );
    }
  }

  if (summary.missingSources.isNotEmpty) {
    stderr.writeln(
      'Missing source content for ${summary.missingSources.length} source(s):',
    );
    for (final missing in summary.missingSources.take(20)) {
      stderr.writeln('  ${missing.sourceMapPath}: ${missing.source}');
    }
    if (summary.missingSources.length > 20) {
      stderr.writeln(
        '  ...and ${summary.missingSources.length - 20} more missing source(s).',
      );
    }

    if (!options.allowMissing) {
      exitCode = 1;
    }
  }
}

class PrepareSentryWebSourceMapsOptions {
  PrepareSentryWebSourceMapsOptions({
    required this.webBuildDir,
    required this.packageConfigFile,
    Directory? dartSdkDir,
    this.allowMissing = false,
  }) : dartSdkDir = dartSdkDir ?? _defaultDartSdkDir();

  factory PrepareSentryWebSourceMapsOptions.fromArgs(List<String> args) {
    var webBuildDir = Directory('build/web');
    var packageConfigFile = File('.dart_tool/package_config.json');
    Directory? dartSdkDir;
    var allowMissing = false;

    String readValue(String name, int index) {
      final inlinePrefix = '$name=';
      final current = args[index];
      if (current.startsWith(inlinePrefix)) {
        return current.substring(inlinePrefix.length);
      }
      if (index + 1 >= args.length) {
        throw ArgumentError('Missing value for $name');
      }
      return args[index + 1];
    }

    for (var i = 0; i < args.length; i++) {
      final arg = args[i];
      if (arg == '--allow-missing') {
        allowMissing = true;
      } else if (arg == '--web-build-dir' ||
          arg.startsWith('--web-build-dir=')) {
        webBuildDir = Directory(readValue('--web-build-dir', i));
        if (arg == '--web-build-dir') i++;
      } else if (arg == '--package-config' ||
          arg.startsWith('--package-config=')) {
        packageConfigFile = File(readValue('--package-config', i));
        if (arg == '--package-config') i++;
      } else if (arg == '--dart-sdk-dir' || arg.startsWith('--dart-sdk-dir=')) {
        dartSdkDir = Directory(readValue('--dart-sdk-dir', i));
        if (arg == '--dart-sdk-dir') i++;
      } else {
        throw ArgumentError('Unknown argument: $arg');
      }
    }

    return PrepareSentryWebSourceMapsOptions(
      webBuildDir: webBuildDir,
      packageConfigFile: packageConfigFile,
      dartSdkDir: dartSdkDir,
      allowMissing: allowMissing,
    );
  }

  final Directory webBuildDir;
  final File packageConfigFile;
  final Directory dartSdkDir;
  final bool allowMissing;
}

class PrepareSentryWebSourceMapsSummary {
  const PrepareSentryWebSourceMapsSummary({
    required this.updatedFiles,
    required this.resolvedSources,
    required this.missingSources,
    required this.ignorableMissingSources,
  });

  final int updatedFiles;
  final int resolvedSources;
  final List<MissingSourceContent> missingSources;
  final List<MissingSourceContent> ignorableMissingSources;
}

class MissingSourceContent {
  const MissingSourceContent({
    required this.sourceMapPath,
    required this.source,
  });

  final String sourceMapPath;
  final String source;
}

class _PackageLocation {
  const _PackageLocation({required this.rootUri, required this.packageUri});

  final Uri rootUri;
  final Uri packageUri;
}

class _SourceResolver {
  _SourceResolver({required this.packageConfigFile, required this.dartSdkDir});

  final File packageConfigFile;
  final Directory dartSdkDir;

  late final Map<String, _PackageLocation> _packages = _readPackageConfig();
  late final Directory _projectRootDir = packageConfigFile.parent.parent;
  late final Uri? _flutterRootUri = _readFlutterRootUri();

  Future<String?> readSourceContent({
    required String source,
    required File sourceMapFile,
  }) async {
    final sourceUri = Uri.tryParse(source);
    if (sourceUri == null) {
      return null;
    }

    final candidates = <File>[
      ..._resolvePackageCandidates(sourceUri),
      ..._resolveDartSdkCandidates(sourceUri),
      ..._resolveRelativeCandidates(sourceUri, sourceMapFile),
    ];

    final seen = <String>{};
    for (final candidate in candidates) {
      final normalizedPath = candidate.absolute.path;
      if (!seen.add(normalizedPath) || !await candidate.exists()) {
        continue;
      }
      return candidate.readAsString();
    }

    return null;
  }

  Map<String, _PackageLocation> _readPackageConfig() {
    final configUri = packageConfigFile.absolute.uri;
    final configDirUri = configUri.resolve('.');
    final decoded =
        jsonDecode(packageConfigFile.readAsStringSync())
            as Map<String, Object?>;
    final packages = decoded['packages'];
    if (packages is! List<Object?>) {
      return const {};
    }

    final result = <String, _PackageLocation>{};
    for (final rawPackage in packages) {
      if (rawPackage is! Map) {
        continue;
      }
      final package = rawPackage.cast<Object?, Object?>();
      final name = package['name'];
      final rootUriValue = package['rootUri'];
      if (name is! String || rootUriValue is! String) {
        continue;
      }

      final rootUri = _ensureDirectoryUri(
        _resolveConfigUri(configDirUri, rootUriValue),
      );
      final packageUriValue = package['packageUri'];
      final packageUri = rootUri.resolve(
        packageUriValue is String ? packageUriValue : 'lib/',
      );
      result[name] = _PackageLocation(rootUri: rootUri, packageUri: packageUri);
    }
    return result;
  }

  Uri _resolveConfigUri(Uri configDirUri, String value) {
    final uri = Uri.parse(value);
    if (uri.hasScheme) {
      return uri;
    }
    return configDirUri.resolveUri(uri);
  }

  Uri _ensureDirectoryUri(Uri uri) {
    if (uri.path.endsWith('/')) {
      return uri;
    }
    return uri.replace(path: '${uri.path}/');
  }

  Iterable<File> _resolvePackageCandidates(Uri sourceUri) sync* {
    if (sourceUri.scheme != 'package' || sourceUri.pathSegments.isEmpty) {
      return;
    }

    final packageName = sourceUri.pathSegments.first;
    final location = _packages[packageName];
    if (location == null) {
      return;
    }

    final relativePath = sourceUri.pathSegments.skip(1).join('/');
    yield File.fromUri(location.packageUri.resolve(relativePath));

    // Some generated worker source maps reference package-root web/ files.
    yield File.fromUri(location.rootUri.resolve(relativePath));
  }

  Iterable<File> _resolveDartSdkCandidates(Uri sourceUri) sync* {
    if (sourceUri.scheme != 'org-dartlang-sdk') {
      return;
    }

    final relativePath = sourceUri.pathSegments.join('/');
    yield File.fromUri(dartSdkDir.absolute.uri.resolve(relativePath));

    if (sourceUri.pathSegments.isNotEmpty &&
        sourceUri.pathSegments.first == 'dart-sdk') {
      final sdkRelativePath = sourceUri.pathSegments.skip(1).join('/');
      yield File.fromUri(dartSdkDir.absolute.uri.resolve(sdkRelativePath));
    }

    final flutterRootUri = _flutterRootUri;
    if (flutterRootUri != null) {
      yield File.fromUri(
        flutterRootUri.resolve('bin/cache/flutter_web_sdk/$relativePath'),
      );
      yield File.fromUri(
        flutterRootUri.resolve('bin/cache/pkg/sky_engine/$relativePath'),
      );
    }
  }

  Iterable<File> _resolveRelativeCandidates(
    Uri sourceUri,
    File sourceMapFile,
  ) sync* {
    if (sourceUri.hasScheme) {
      return;
    }

    for (final baseUri in _relativeSourceBaseUris(sourceMapFile)) {
      yield File.fromUri(baseUri.resolveUri(sourceUri));
    }
  }

  Iterable<Uri> _relativeSourceBaseUris(File sourceMapFile) sync* {
    yield sourceMapFile.parent.absolute.uri;

    final flutterBuildDir = Directory.fromUri(
      _projectRootDir.absolute.uri.resolve('.dart_tool/flutter_build/'),
    );
    if (!flutterBuildDir.existsSync()) {
      return;
    }

    if (sourceMapFile.uri.pathSegments.isEmpty) {
      return;
    }
    final sourceMapName = sourceMapFile.uri.pathSegments.last;

    for (final entity in flutterBuildDir.listSync()) {
      if (entity is! Directory) {
        continue;
      }

      final matchingSourceMap = File.fromUri(entity.uri.resolve(sourceMapName));
      if (matchingSourceMap.existsSync()) {
        yield entity.absolute.uri;
      }
    }
  }

  Uri? _readFlutterRootUri() {
    final configUri = packageConfigFile.absolute.uri;
    final configDirUri = configUri.resolve('.');
    final decoded =
        jsonDecode(packageConfigFile.readAsStringSync())
            as Map<String, Object?>;
    final flutterRoot = decoded['flutterRoot'];
    if (flutterRoot is String && flutterRoot.isNotEmpty) {
      return _ensureDirectoryUri(_resolveConfigUri(configDirUri, flutterRoot));
    }

    final envFlutterRoot = Platform.environment['FLUTTER_ROOT'];
    if (envFlutterRoot != null && envFlutterRoot.isNotEmpty) {
      return _ensureDirectoryUri(Directory(envFlutterRoot).absolute.uri);
    }

    return null;
  }
}

Future<PrepareSentryWebSourceMapsSummary> prepareSentryWebSourceMaps(
  PrepareSentryWebSourceMapsOptions options,
) async {
  final resolver = _SourceResolver(
    packageConfigFile: options.packageConfigFile,
    dartSdkDir: options.dartSdkDir,
  );
  final missingSources = <MissingSourceContent>[];
  final ignorableMissingSources = <MissingSourceContent>[];
  var updatedFiles = 0;
  var resolvedSources = 0;

  await for (final entity in options.webBuildDir.list(recursive: true)) {
    if (entity is! File || !entity.path.endsWith('.js.map')) {
      continue;
    }

    final decoded = jsonDecode(await entity.readAsString());
    if (decoded is! Map<String, Object?>) {
      continue;
    }

    final sources = decoded['sources'];
    if (sources is! List<Object?>) {
      continue;
    }

    final sourcesContent = <String?>[];
    for (final source in sources) {
      if (source is! String) {
        sourcesContent.add(null);
        continue;
      }

      final content = await resolver.readSourceContent(
        source: source,
        sourceMapFile: entity,
      );
      if (content == null) {
        final missing = MissingSourceContent(
          sourceMapPath: entity.path,
          source: source,
        );
        if (_isIgnorableMissingSource(source)) {
          ignorableMissingSources.add(missing);
        } else {
          missingSources.add(missing);
        }
      } else {
        resolvedSources++;
      }
      sourcesContent.add(content);
    }

    decoded['sourcesContent'] = sourcesContent;
    await entity.writeAsString(jsonEncode(decoded));
    updatedFiles++;
  }

  return PrepareSentryWebSourceMapsSummary(
    updatedFiles: updatedFiles,
    resolvedSources: resolvedSources,
    missingSources: missingSources,
    ignorableMissingSources: ignorableMissingSources,
  );
}

bool _isIgnorableMissingSource(String source) {
  final uri = Uri.tryParse(source);
  if (uri == null) {
    return false;
  }

  // Flutter web source maps can include SDK/engine pseudo-paths that are not
  // present as regular files in CI environments.
  return uri.scheme == 'org-dartlang-sdk';
}

Directory _defaultDartSdkDir() {
  final executable = File(Platform.resolvedExecutable).absolute;
  final candidates = <Directory>[
    executable.parent.parent,
    executable.parent.parent.parent,
    Directory.fromUri(executable.parent.parent.uri.resolve('cache/dart-sdk/')),
  ];

  for (final candidate in candidates) {
    if (File.fromUri(
      candidate.uri.resolve('lib/core/errors.dart'),
    ).existsSync()) {
      return candidate;
    }
  }

  return executable.parent.parent;
}
