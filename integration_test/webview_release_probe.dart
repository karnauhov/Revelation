// Local release probe for native WebView compatibility; never publish this target.
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:revelation/core/platform/platform_utils.dart';

import 'smoke/webview_test_data.dart';

const _waitingTitle = 'Revelation WebView probe - starting';
const _readyTitle = 'Revelation WebView probe - JavaScript verified';
const _coldTitle = 'Revelation WebView probe - no WebView';

Future<void> main(List<String> args) async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  final windows = !kIsWeb && defaultTargetPlatform == TargetPlatform.windows;
  final cold = windows && args.contains('--without-webview');
  if (windows) {
    await setDesktopWindowTitle(cold ? _coldTitle : _waitingTitle);
  }
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(title: const Text('REV142 · WebView release')),
        body: SafeArea(
          child: cold
              ? const Center(child: Text(_coldTitle))
              : InAppWebView(
                  initialSettings: InAppWebViewSettings(
                    javaScriptEnabled: true,
                  ),
                  initialData: InAppWebViewInitialData(
                    data: rev142WebViewHtml,
                    baseUrl: WebUri('https://localhost/'),
                  ),
                  onLoadStop: windows
                      ? (controller, _) async {
                          final text = await controller.evaluateJavascript(
                            source:
                                'document.getElementById("status").textContent',
                          );
                          if (text == webViewReadyText) {
                            await setDesktopWindowTitle(_readyTitle);
                          }
                        }
                      : null,
                ),
        ),
      ),
    ),
  );
}
