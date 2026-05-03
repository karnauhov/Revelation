import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/web_db_version_sync_plan.dart';

void main() {
  test('does not reset or commit when remote version is unknown', () {
    final plan = planWebDbVersionSync(
      remoteVersionToken: null,
      localVersionToken: 'manifest:schema:4|data:2',
    );

    expect(plan.versionToken, isNull);
    expect(plan.shouldResetLocalDatabase, isFalse);
    expect(plan.shouldCommitVersionAfterOpen, isFalse);
  });

  test('keeps existing local database when version token matches', () {
    final plan = planWebDbVersionSync(
      remoteVersionToken: 'manifest:schema:4|data:2',
      localVersionToken: 'manifest:schema:4|data:2',
    );

    expect(plan.versionToken, 'manifest:schema:4|data:2');
    expect(plan.shouldResetLocalDatabase, isFalse);
    expect(plan.shouldCommitVersionAfterOpen, isFalse);
  });

  test('resets database and defers version commit for changed token', () {
    final plan = planWebDbVersionSync(
      remoteVersionToken: 'manifest:schema:4|data:3',
      localVersionToken: 'manifest:schema:4|data:2',
    );

    expect(plan.versionToken, 'manifest:schema:4|data:3');
    expect(plan.shouldResetLocalDatabase, isTrue);
    expect(plan.shouldCommitVersionAfterOpen, isTrue);
  });

  test('force reset recreates database even when version token matches', () {
    final plan = planWebDbVersionSync(
      remoteVersionToken: 'manifest:schema:4|data:3',
      localVersionToken: 'manifest:schema:4|data:3',
      forceResetLocalDatabase: true,
    );

    expect(plan.versionToken, 'manifest:schema:4|data:3');
    expect(plan.shouldResetLocalDatabase, isTrue);
    expect(plan.shouldCommitVersionAfterOpen, isTrue);
  });

  test('force reset is ignored when remote version is unknown', () {
    final plan = planWebDbVersionSync(
      remoteVersionToken: null,
      localVersionToken: 'manifest:schema:4|data:3',
      forceResetLocalDatabase: true,
    );

    expect(plan.versionToken, isNull);
    expect(plan.shouldResetLocalDatabase, isFalse);
    expect(plan.shouldCommitVersionAfterOpen, isFalse);
  });
}
