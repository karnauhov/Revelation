import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(Talker());
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  test('downloadImage returns null for malformed page', () async {
    final manager = ServerManager();

    final result = await manager.downloadImage('no-slash', false);

    expect(result, isNull);
  });

  test('downloadDB returns null when supabase is not initialized', () async {
    final manager = ServerManager();

    final result = await manager.downloadDB('repo', 'file.sqlite');

    expect(result, isNull);
  });

  test('getLastUpdateFileFromServer returns null when not initialized',
      () async {
    final manager = ServerManager();

    final result = await manager.getLastUpdateFileFromServer('repo', 'file');

    expect(result, isNull);
  });
}
