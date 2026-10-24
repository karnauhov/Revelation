import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import '../../test/test_harness/bible_parallel_reading_scenario.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  for (final language in ['en', 'uk']) {
    testWidgets(
      'parallel reading smoke: defaults, preferences and links ($language)',
      (tester) async {
        await exerciseParallelBibleReading(tester, language);
      },
    );
  }
}
