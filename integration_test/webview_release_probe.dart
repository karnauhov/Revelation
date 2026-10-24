// Local release probe for native WebView/R8 compatibility; never publish this target.
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';

import 'smoke/webview_test_data.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(title: const Text('REV142 · WebView release')),
        body: SafeArea(
          child: InAppWebView(
            initialSettings: InAppWebViewSettings(javaScriptEnabled: true),
            initialData: InAppWebViewInitialData(
              data: rev142WebViewHtml,
              baseUrl: WebUri('https://localhost/'),
            ),
          ),
        ),
      ),
    ),
  );
}
