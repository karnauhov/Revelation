@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../../../test_harness/bible_parallel_reading_scenario.dart';

void main() {
  for (final language in ['en', 'uk']) {
    for (final size in [const Size(420, 900), const Size(1280, 800)]) {
      testWidgets(
        'parallel defaults, saved single pane and reference links: $language $size',
        (tester) async {
          await tester.binding.setSurfaceSize(size);
          addTearDown(() => tester.binding.setSurfaceSize(null));
          await exerciseParallelBibleReading(tester, language);
        },
      );
    }
  }
}
