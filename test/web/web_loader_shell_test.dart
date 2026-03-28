import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('web shell shows branded loader before Flutter bootstraps', () {
    final indexHtml = File('web/index.html').readAsStringSync();
    final bootstrapScript = File('web/flutter_bootstrap.js').readAsStringSync();

    expect(indexHtml, contains('id="app-loader"'));
    expect(indexHtml, contains('startup_splash_banner.jpg'));
    expect(indexHtml, contains('id="app-loader-progress-fill"'));
    expect(indexHtml, contains('body.app-loaded #app-loader'));

    expect(bootstrapScript, contains("serviceWorkerVersion: String("));
    expect(
      bootstrapScript,
      contains(
        r"""'{{flutter_service_worker_version}}'.replace(/^"|"$/g, '')""",
      ),
    );
    expect(
      bootstrapScript,
      contains("document.querySelector(flutterReadySelector)"),
    );
    expect(
      bootstrapScript,
      contains("onEntrypointLoaded: async function (engineInitializer)"),
    );
    expect(bootstrapScript, contains('en: {'));
    expect(bootstrapScript, contains('es: {'));
    expect(bootstrapScript, contains('ru: {'));
    expect(bootstrapScript, contains('uk: {'));
  });
}
