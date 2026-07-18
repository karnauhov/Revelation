import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('SharedPreferencesBiblePreferencesStore', () {
    test('loads legacy single module as an open module list', () async {
      SharedPreferences.setMockInitialValues(<String, Object>{
        SharedPreferencesBiblePreferencesStore.lastModuleFileKey:
            'bible_lxx_tr.sqlite',
      });

      const store = SharedPreferencesBiblePreferencesStore();

      expect(await store.loadLastModuleFiles(), ['bible_lxx_tr.sqlite']);
    });

    test(
      'saves open module list and keeps single module fallback in sync',
      () async {
        SharedPreferences.setMockInitialValues(<String, Object>{});
        const store = SharedPreferencesBiblePreferencesStore();

        await store.saveLastModuleFiles([
          'bible_lxx_tr.sqlite',
          'bible_alt.sqlite',
        ]);

        expect(await store.loadLastModuleFile(), 'bible_lxx_tr.sqlite');
        expect(await store.loadLastModuleFiles(), [
          'bible_lxx_tr.sqlite',
          'bible_alt.sqlite',
        ]);
      },
    );

    test('stores last search query separately for each module', () async {
      SharedPreferences.setMockInitialValues(<String, Object>{});
      const store = SharedPreferencesBiblePreferencesStore();

      await store.saveLastSearchQuery(
        moduleFile: 'bible_lxx_tr.sqlite',
        query: 'logos',
      );
      await store.saveLastSearchQuery(
        moduleFile: 'bible_alt.sqlite',
        query: 'grace',
      );

      expect(await store.loadLastSearchQuery('bible_lxx_tr.sqlite'), 'logos');
      expect(await store.loadLastSearchQuery('bible_alt.sqlite'), 'grace');
    });

    test('normalizes search history values on save', () async {
      SharedPreferences.setMockInitialValues(<String, Object>{});
      const store = SharedPreferencesBiblePreferencesStore();

      await store.saveSearchHistory(['  logos  ', '', 'grace']);

      expect(await store.loadSearchHistory(), ['logos', 'grace']);
    });
  });
}
