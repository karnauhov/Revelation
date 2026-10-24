import 'dart:async';
import 'dart:js_interop';

import 'package:drift/wasm.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/web.dart';
import 'package:revelation/infra/db/connectors/web_database_open_lock.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:web/web.dart' as web;

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  binding.reportData = <String, dynamic>{};

  testWidgets('concurrent storage probes never report worker errors', (
    tester,
  ) async {
    await tester.runAsync(() async {
      for (var round = 0; round < 15; round++) {
        final probes = await Future.wait([
          for (final name in ['common', 'localized', 'bible'])
            withWebDatabaseOpenLock(
              () => WasmDatabase.probe(
                sqlite3Uri: Uri.parse('sqlite3.wasm'),
                driftWorkerUri: Uri.parse('drift_worker.js'),
                databaseName: 'rev122_probe_$name',
              ),
            ),
        ]);
        for (final probe in probes) {
          expect(
            probe.missingFeatures,
            isNot(contains(MissingBrowserFeature.workerError)),
          );
          expect(probe.availableStorages, isNotEmpty);
        }
      }
      binding.reportData!['storageProbeRequests'] = 45;
      binding.reportData!['workerErrors'] = 0;
    });
  });

  testWidgets('opening waits for a browser lock and releases failed requests', (
    tester,
  ) async {
    await tester.runAsync(() async {
      final acquired = Completer<void>();
      final release = Completer<void>();
      addTearDown(() {
        if (!release.isCompleted) release.complete();
      });
      final held = web.window.navigator.locks
          .request(
            webDatabaseOpenLockName,
            ((web.Lock? _) {
              acquired.complete();
              return release.future.toJS;
            }).toJS,
          )
          .toDart;
      await acquired.future;
      var called = false;
      final failure = StateError('failed while locked');
      final failed = withWebDatabaseOpenLock<int>(() async {
        called = true;
        throw failure;
      });
      final failureCheck = expectLater(failed, throwsA(same(failure)));
      await Future<void>.delayed(const Duration(milliseconds: 100));
      expect(called, isFalse);
      release.complete();
      await held;
      await failureCheck;
      expect(await withWebDatabaseOpenLock(() async => 42), 42);
      binding.reportData!['sharedLockAndFailureRecovery'] = true;
    });
  });

  testWidgets('common and localized databases open together and reopen', (
    tester,
  ) async {
    await tester.runAsync(() async {
      await GetIt.I.reset();
      GetIt.I.registerSingleton<Talker>(
        Talker(settings: TalkerSettings(useConsoleLogs: false)),
      );
      SharedPreferences.setMockInitialValues({});
      for (var round = 0; round < 2; round++) {
        final common = getCommonDB();
        final english = getLocalizedDB('en');
        final ukrainian = getLocalizedDB('uk');
        try {
          await Future.wait([
            _checkMetadata(common),
            _checkLocalizedMetadata(english),
            _checkLocalizedMetadata(ukrainian),
          ]);
        } finally {
          await Future.wait([
            common.close(),
            english.close(),
            ukrainian.close(),
          ]);
        }
      }
      await GetIt.I.reset();
      binding.reportData!['commonLocalizedDatabaseOpens'] = 6;
    });
  });
}

Future<void> _checkMetadata(CommonDB db) async {
  final row = await db
      .customSelect('SELECT COUNT(*) AS total FROM db_metadata')
      .getSingle();
  expect(row.read<int>('total'), greaterThan(0));
}

Future<void> _checkLocalizedMetadata(LocalizedDB db) async {
  final row = await db
      .customSelect('SELECT COUNT(*) AS total FROM db_metadata')
      .getSingle();
  expect(row.read<int>('total'), greaterThan(0));
}
