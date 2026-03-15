import 'package:flutter_test/flutter_test.dart';
import 'revelation_test_harness.dart';

void main() {
  group('RevelationTestHarness', () {
    test('seeds supabase values in fake env', () {
      final harness = RevelationTestHarness();

      harness.seedSupabase(url: 'https://example.supabase.co', key: 'anon-key');

      expect(harness.env.read('SUPABASE_URL'), 'https://example.supabase.co');
      expect(harness.env.read('SUPABASE_KEY'), 'anon-key');
    });

    test('stores and returns fake remote bytes', () async {
      final harness = RevelationTestHarness();

      harness.remote.addFile('db', 'test.sqlite', <int>[1, 2, 3]);
      final bytes = await harness.remote.download('db', 'test.sqlite');

      expect(bytes?.toList(), <int>[1, 2, 3]);
      expect(harness.remote.contains('db', 'test.sqlite'), isTrue);
    });
  });
}
