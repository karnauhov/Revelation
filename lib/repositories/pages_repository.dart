import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/pages_settings.dart';

class PagesRepository {
  static const String _pagesKey = 'revelation_pages';

  Future<PagesSettings> getPages() async {
    final prefs = await SharedPreferences.getInstance();
    final String? jsonString = prefs.getString(_pagesKey);
    if (jsonString == null) {
      return PagesSettings(pages: {});
    }
    final Map<String, dynamic> jsonMap = jsonDecode(jsonString);
    return PagesSettings.fromMap(jsonMap);
  }

  Future<void> savePages(PagesSettings settings) async {
    final prefs = await SharedPreferences.getInstance();
    final String jsonString = jsonEncode(settings.toMap());
    await prefs.setString(_pagesKey, jsonString);
  }
}
