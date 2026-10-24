# Android WebView compatibility snapshot

This is the runtime portion of `flutter_inappwebview_android` **1.1.3**, the stable Android implementation used by `flutter_inappwebview` 6.1.5. It is third-party code by the upstream authors, not a Revelation-authored package.

Source: [exact upstream package](https://github.com/pichillilorenzo/flutter_inappwebview/tree/v6.1.5/flutter_inappwebview_android), [published archive](https://pub.dev/api/archives/flutter_inappwebview_android-1.1.3.tar.gz).
Archive SHA-256: `62557c15a5c2db5d195cb3892aab74fcaec266d7b86d59a6f0027abd672cddba`.

The package's `android/`, `lib/`, `pubspec.yaml`, and unmodified [Apache-2.0 license](LICENSE) are retained. Examples, upstream tests, and unrelated release documentation are not needed to build the dependency.

Revelation change (REV142): the debug and release ProGuard defaults in [`android/build.gradle`](android/build.gradle) use `proguard-android-optimize.txt`. AGP 9 rejects the former `proguard-android.txt` because it disables optimization. A comment in the modified file identifies this change. No native or Dart behavior is changed; formatting may follow the package's declared Dart language version. Consumer rules remain intact, and the AGP prohibition is not disabled.

The root `pubspec.yaml` selects this snapshot through a path override. Acknowledgements link to the exact upstream package and its package-local license. The app analyzer excludes externally owned sources just as it excluded this dependency in the pub cache; app code and its existing quality gates remain covered.

Validation uses the local Android startup smoke (including a local HTML WebView) and the [release probe](../../integration_test/webview_release_probe.dart). See the [testing strategy](../../docs/en/testing/strategy.en.md). Replace the override with a compatible stable upstream release once available; recheck the license, native startup, local HTML/JavaScript, and release shrinking before removing this snapshot.
