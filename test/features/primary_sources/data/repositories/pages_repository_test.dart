import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/shared/models/pages_settings.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues(<String, Object>{});
  });

  test('getPages returns empty settings when no data stored', () async {
    final repository = PagesRepository();

    final settings = await repository.getPages();

    expect(settings.pages, isEmpty);
  });

  test('savePages persists and can be read back', () async {
    final repository = PagesRepository();
    final settings = PagesSettings(pages: {'source-1_page-1': 'raw-settings'});

    await repository.savePages(settings);
    final loaded = await repository.getPages();

    expect(loaded.pages['source-1_page-1'], 'raw-settings');
  });
}
