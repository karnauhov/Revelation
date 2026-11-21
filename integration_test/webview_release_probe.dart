// Local process probe for Windows WebView and audio shutdown.
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:revelation/core/platform/platform_utils.dart';

import 'smoke/webview_test_data.dart';

const _waitingTitle = 'Revelation WebView probe - starting';
const _readyTitle = 'Revelation WebView probe - JavaScript verified';
const _coldTitle = 'Revelation WebView probe - no WebView';
const _audioTitle = 'Revelation Windows probe - native audio requested';

Future<void> main(List<String> args) async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  final windows = !kIsWeb && defaultTargetPlatform == TargetPlatform.windows;
  final cold = windows && args.contains('--without-webview');
  final playAudio = cold && args.contains('--play-audio');
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
  if (playAudio) {
    await WidgetsBinding.instance.endOfFrame;
    const audio = MethodChannel('revelation/audio');
    await audio.invokeMethod<void>('prepareAssets', {
      'assets': {'click': 'assets/sounds/click.mp3'},
    });
    await audio.invokeMethod<void>('play', {'soundName': 'click'});
    await setDesktopWindowTitle(_audioTitle);
  }
}
