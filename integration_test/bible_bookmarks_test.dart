import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

import 'support/bible_bookmarks_scenario.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Bible bookmarks across translations and reader reopening', (
    tester,
  ) async {
    if (!kIsWeb) {
      // The native runner can use the same app identifier as an existing install.
      final previous = SharedPreferencesAsyncPlatform.instance;
      SharedPreferencesAsyncPlatform.instance =
          InMemorySharedPreferencesAsync.empty();
      addTearDown(() => SharedPreferencesAsyncPlatform.instance = previous);
    }
    // On Web, the driver starts with its own isolated browser profile.
    try {
      await exerciseBibleBookmarks(tester);
    } catch (error, stack) {
      binding.reportData = {
        'error': error.toString(),
        'stack': stack.toString(),
      };
      rethrow;
    }
  });
}
