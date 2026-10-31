@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../test_harness/bible_strong_availability_scenario.dart';
import '../../../../test_harness/fakes/fake_parallel_bible_repository.dart';

void main() {
  for (final width in [375.0, 1700.0]) {
    testWidgets('Strong controls follow each module at width $width', (
      tester,
    ) async {
      SharedPreferences.setMockInitialValues({});
      final map = (await tester.runAsync(() async {
        await const SharedPreferencesBiblePreferencesStore()
            .saveLastModuleFiles([FakeParallelBibleRepository.original]);
        return BibleVerseMap.loadFromAssets();
      }))!;
      await exerciseBibleStrongAvailability(
        tester,
        FakeParallelBibleRepository(map),
        width,
      );
    });
  }
}
