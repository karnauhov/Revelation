import 'package:intl/intl.dart';
import 'package:web/web.dart';
import 'package:revelation/utils/webgl_interop.dart';

String getPlatformLanguage() {
  return Intl.shortLocale(document.defaultView!.navigator.language);
}

bool isMobileBrowser() {
  final ua = window.navigator.userAgent;
  if (RegExp(r'Mobi|Android|iPhone|iPad|iPod|IEMobile').hasMatch(ua)) {
    return true;
  }

  final touches = window.navigator.maxTouchPoints;
  return (touches) > 0;
}

String getUserAgent() {
  return window.navigator.userAgent;
}

Future<int> fetchMaxTextureSize() async {
  int result = await WebGLInterop.fetchMaxTextureSize();
  return result;
}
