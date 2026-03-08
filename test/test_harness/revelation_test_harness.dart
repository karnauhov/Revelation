import 'fakes/fake_env.dart';
import 'fakes/fake_logger.dart';
import 'fakes/fake_remote.dart';

class RevelationTestHarness {
  RevelationTestHarness({
    FakeLogger? logger,
    FakeEnv? env,
    FakeRemoteStorage? remote,
  }) : logger = logger ?? FakeLogger(),
       env = env ?? FakeEnv(),
       remote = remote ?? FakeRemoteStorage();

  final FakeLogger logger;
  final FakeEnv env;
  final FakeRemoteStorage remote;

  void seedSupabase({required String url, required String key}) {
    env.write('SUPABASE_URL', url);
    env.write('SUPABASE_KEY', key);
  }
}
