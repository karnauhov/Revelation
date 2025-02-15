import 'package:intl/intl.dart';
import 'package:web/web.dart';

String getPlatformLanguage() {
  return Intl.shortLocale(document.defaultView!.navigator.language);
}
