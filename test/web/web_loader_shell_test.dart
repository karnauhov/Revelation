import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('web shell shows branded loader before Flutter bootstraps', () {
    final indexHtml = File('web/index.html').readAsStringSync();
    final bootstrapScript = File('web/flutter_bootstrap.js').readAsStringSync();

    expect(indexHtml, contains('id="app-loader"'));
    expect(indexHtml, contains('startup_splash_banner.jpg'));
    expect(indexHtml, contains('id="app-loader-progress-fill"'));
    expect(indexHtml, contains('id="app-loader-version"'));
    expect(indexHtml, contains('body.app-loaded #app-loader'));

    expect(
      bootstrapScript,
      contains("const loaderManifestUrl = 'loader_manifest.json';"),
    );
    expect(
      bootstrapScript,
      contains("fetch('version.json', { cache: 'no-store' })"),
    );
    expect(
      bootstrapScript,
      contains(
        'parseServiceWorkerVersion(`{{flutter_service_worker_version}}`)',
      ),
    );
    expect(bootstrapScript, contains("const serviceWorkerVersion ="));
    expect(bootstrapScript, contains("serviceWorkerUrl:"));
    expect(bootstrapScript, contains("revelation_files_cache_sw.js?v="));
    expect(bootstrapScript, contains("computeExpectedTotalBytes()"));
    expect(
      bootstrapScript,
      contains("document.querySelector(flutterReadySelector)"),
    );
    expect(
      bootstrapScript,
      contains("onEntrypointLoaded: async (engineInitializer) =>"),
    );
    expect(bootstrapScript, contains('en: {'));
    expect(bootstrapScript, contains('es: {'));
    expect(bootstrapScript, contains('ru: {'));
    expect(bootstrapScript, contains('uk: {'));

    final imageCacheServiceWorker = File(
      'web/revelation_files_cache_sw.js',
    ).readAsStringSync();
    expect(
      imageCacheServiceWorker,
      contains(
        "const RUNTIME_IMAGE_CACHE = 'revelation-runtime-image-cache-v2';",
      ),
    );
    expect(imageCacheServiceWorker, contains('function cacheFirst(request)'));
    expect(
      imageCacheServiceWorker,
      contains(
        "const ALLOWED_SUPABASE_HOST = 'adfdfxnzxmzyoioedwuy.supabase.co';",
      ),
    );
    expect(
      imageCacheServiceWorker,
      contains("const SUPABASE_OBJECT_PATH_PREFIX = '/storage/v1/object/';"),
    );
    expect(
      imageCacheServiceWorker,
      contains(
        "const ALLOWED_SUPABASE_FOLDERS = ['images/', 'primary_sources/'];",
      ),
    );
    expect(
      imageCacheServiceWorker,
      contains("objectPath.startsWith(folderPrefix)"),
    );
    expect(
      imageCacheServiceWorker,
      contains(r"objectPath.startsWith(`public/${folderPrefix}`)"),
    );
  });
}
