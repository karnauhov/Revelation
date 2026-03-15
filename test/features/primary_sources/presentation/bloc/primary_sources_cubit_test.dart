import 'dart:async';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(Talker());
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  test('loadPrimarySources emits loading and grouped success state', () async {
    final repository = _ControlledPrimarySourcesRepository();
    final cubit = PrimarySourcesCubit(repository);
    addTearDown(cubit.close);

    unawaited(cubit.loadPrimarySources());
    await _flushAsync();

    expect(cubit.state.isLoading, isTrue);
    expect(cubit.state.hasError, isFalse);
    expect(cubit.state.full, isEmpty);
    expect(cubit.state.significant, isEmpty);
    expect(cubit.state.fragments, isEmpty);

    repository.completeRequest(
      0,
      AppSuccess<PrimarySourcesLoadResult>(
        PrimarySourcesLoadResult(
          fullPrimarySources: [_buildSource('full')],
          significantPrimarySources: [_buildSource('significant')],
          fragmentsPrimarySources: [_buildSource('fragment')],
        ),
      ),
    );
    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.hasError, isFalse);
    expect(cubit.state.full.map((source) => source.id), <String>['full']);
    expect(cubit.state.significant.map((source) => source.id), <String>[
      'significant',
    ]);
    expect(cubit.state.fragments.map((source) => source.id), <String>[
      'fragment',
    ]);
  });

  test(
    'loadPrimarySources emits failure state for repository failure result',
    () async {
      final repository = _ControlledPrimarySourcesRepository();
      final cubit = PrimarySourcesCubit(repository);
      addTearDown(cubit.close);

      unawaited(cubit.loadPrimarySources());
      await _flushAsync();

      repository.completeRequest(
        0,
        const AppFailureResult<PrimarySourcesLoadResult>(
          AppFailure.dataSource('forced data failure'),
        ),
      );
      await _flushAsync();

      expect(cubit.state.isLoading, isFalse);
      expect(cubit.state.hasError, isTrue);
      expect(cubit.state.failure, isNotNull);
      expect(cubit.state.failure!.type, AppFailureType.dataSource);
      expect(cubit.state.failure!.message, 'forced data failure');
      expect(cubit.state.full, isEmpty);
      expect(cubit.state.significant, isEmpty);
      expect(cubit.state.fragments, isEmpty);
    },
  );

  test(
    'loadPrimarySources emits unknown failure when repository throws',
    () async {
      final cubit = PrimarySourcesCubit(_ThrowingPrimarySourcesRepository());
      addTearDown(cubit.close);

      await cubit.loadPrimarySources();

      expect(cubit.state.isLoading, isFalse);
      expect(cubit.state.hasError, isTrue);
      expect(cubit.state.failure, isNotNull);
      expect(cubit.state.failure!.type, AppFailureType.unknown);
      expect(
        cubit.state.failure!.message,
        'Unexpected error while loading primary sources.',
      );
    },
  );

  test('loadPrimarySources ignores stale result from older request', () async {
    final repository = _ControlledPrimarySourcesRepository();
    final cubit = PrimarySourcesCubit(repository);
    addTearDown(cubit.close);

    unawaited(cubit.loadPrimarySources());
    await _flushAsync();
    unawaited(cubit.loadPrimarySources());
    await _flushAsync();

    expect(repository.pendingRequestsCount, 2);
    expect(cubit.state.isLoading, isTrue);

    repository.completeRequest(
      0,
      AppSuccess<PrimarySourcesLoadResult>(
        PrimarySourcesLoadResult(
          fullPrimarySources: [_buildSource('stale')],
          significantPrimarySources: const [],
          fragmentsPrimarySources: const [],
        ),
      ),
    );
    await _flushAsync();

    expect(cubit.state.isLoading, isTrue);
    expect(cubit.state.full, isEmpty);

    repository.completeRequest(
      1,
      AppSuccess<PrimarySourcesLoadResult>(
        PrimarySourcesLoadResult(
          fullPrimarySources: [_buildSource('fresh')],
          significantPrimarySources: const [],
          fragmentsPrimarySources: const [],
        ),
      ),
    );
    await _flushAsync();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.full.length, 1);
    expect(cubit.state.full.first.id, 'fresh');
  });
}

Future<void> _flushAsync() async {
  await Future<void>.delayed(Duration.zero);
  await Future<void>.delayed(Duration.zero);
}

PrimarySource _buildSource(String id) {
  return PrimarySource(
    id: id,
    title: id,
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    attributes: const [],
    permissionsReceived: false,
  );
}

class _ControlledPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _ControlledPrimarySourcesRepository()
    : super(dataSource: _EmptyPrimarySourcesDataSource());

  final List<Completer<AppResult<PrimarySourcesLoadResult>>> _requests = [];

  int get pendingRequestsCount => _requests.length;

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() {
    final completer = Completer<AppResult<PrimarySourcesLoadResult>>();
    _requests.add(completer);
    return completer.future;
  }

  void completeRequest(int index, AppResult<PrimarySourcesLoadResult> result) {
    _requests[index].complete(result);
  }
}

class _ThrowingPrimarySourcesRepository extends PrimarySourcesDbRepository {
  _ThrowingPrimarySourcesRepository()
    : super(dataSource: _EmptyPrimarySourcesDataSource());

  @override
  Future<AppResult<PrimarySourcesLoadResult>> loadGroupedSourcesResult() {
    throw StateError('forced throw');
  }
}

class _EmptyPrimarySourcesDataSource implements PrimarySourcesDataSource {
  @override
  bool get isInitialized => true;

  @override
  List<common_db.PrimarySource> get primarySourceRows => const [];

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      const [];

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows => const [];

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows => const [];

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      const [];

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows => const [];

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows => const [];

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows => const [];

  @override
  Future<Uint8List?> getCommonResourceData(String key) async {
    return null;
  }
}
