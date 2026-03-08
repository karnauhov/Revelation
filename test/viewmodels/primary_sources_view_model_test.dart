import 'dart:async';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_sources_view_model.dart';

void main() {
  test('loadPrimarySources ignores stale result from older request', () async {
    final repository = _ControlledPrimarySourcesRepository();
    final viewModel = PrimarySourcesViewModel(repository);

    unawaited(viewModel.loadPrimarySources());
    await _flushAsync();
    unawaited(viewModel.loadPrimarySources());
    await _flushAsync();

    expect(repository.pendingRequestsCount, 2);
    expect(viewModel.isLoading, isTrue);

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

    expect(viewModel.isLoading, isTrue);
    expect(viewModel.fullPrimarySources, isEmpty);

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

    expect(viewModel.isLoading, isFalse);
    expect(viewModel.fullPrimarySources.length, 1);
    expect(viewModel.fullPrimarySources.first.id, 'fresh');
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
    link1Title: '',
    link1Url: '',
    link2Title: '',
    link2Url: '',
    link3Title: '',
    link3Url: '',
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
