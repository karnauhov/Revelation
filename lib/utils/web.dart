// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

String getPlatformLanguage() {
  return html.window.navigator.language;
}
