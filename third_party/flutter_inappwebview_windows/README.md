# Windows WebView compatibility snapshot

This directory contains the runtime files from [flutter_inappwebview_windows 0.6.0](https://pub.dev/packages/flutter_inappwebview_windows/versions/0.6.0), distributed under its [Apache-2.0 license](LICENSE). The published archive SHA-256 is `8b4d3a46078a2cdc636c4a3d10d10f2a16882f6be607962dbfff8874d1642055`.

The Revelation patch for REV318 adds a native shutdown entry point. The application destroys its Flutter controller before calling it. The plugin then releases its DirectComposition and graphics resources, requests shutdown of the WinRT dispatcher queue, and drains pending messages while COM is still initialized. Asynchronous callbacks for a destroyed embedded WebView manager or WebView environment discard their results safely. Earlier versions left shared WinRT objects to static destruction at DLL unload, which can fault in `coremessaging.dll` during process exit.

Run the [Windows process regression](../../integration_test/windows_webview_shutdown.ps1) before removing this override. Replace it when the stable upstream implementation supports a verified clean shutdown. See [upstream issue #2733](https://github.com/pichillilorenzo/flutter_inappwebview/issues/2733).
