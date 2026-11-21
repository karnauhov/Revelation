import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_catalog_cubit.dart';

import '../../../../test_harness/fakes/fake_allusion_repositories.dart';

void main() {
  test('an older refresh cannot replace the current catalog', () async {
    final library = _CatalogLibrary();
    final cubit = BibleCatalogCubit(library);
    addTearDown(cubit.close);
    final first = cubit.load();
    await Future<void>.delayed(Duration.zero);
    final second = cubit.load();
    await Future<void>.delayed(Duration.zero);
    expect(cubit.state.modules, [FakeBibleLibrary.english]);
    expect(cubit.state.loading, isTrue);

    library.requests.last.complete([FakeBibleLibrary.ukrainian]);
    await second;
    library.requests.first.complete([FakeBibleLibrary.english]);
    await first;

    expect(cubit.state.modules, [FakeBibleLibrary.ukrainian]);
    expect(cubit.state.loading, isFalse);
  });

  test('offline refresh keeps newly discovered installed modules', () async {
    final library = _CatalogLibrary();
    final cubit = BibleCatalogCubit(library);
    addTearDown(cubit.close);
    final loading = cubit.load();
    await Future<void>.delayed(Duration.zero);
    library.snapshot = [FakeBibleLibrary.english, FakeBibleLibrary.ukrainian];
    library.requests.single.completeError(StateError('offline'));
    await loading;

    expect(cubit.state.modules, library.snapshot);
    expect(cubit.state.failed, isTrue);
    expect(cubit.state.loading, isFalse);
  });

  test('a cache error leaves loading without retrying the same read', () async {
    final library = _CatalogLibrary()..cacheError = StateError('unavailable');
    final cubit = BibleCatalogCubit(library);
    addTearDown(cubit.close);
    await cubit.load();

    expect(cubit.state.failed, isTrue);
    expect(cubit.state.loading, isFalse);
    expect(library.reads, 1);
    expect(library.requests, isEmpty);
  });

  test('closing during refresh ignores its late failure', () async {
    final library = _CatalogLibrary();
    final cubit = BibleCatalogCubit(library);
    final loading = cubit.load();
    await Future<void>.delayed(Duration.zero);
    final beforeClose = cubit.state;
    await cubit.close();
    library.requests.single.completeError(StateError('offline'));
    await loading;
    expect(cubit.state, beforeClose);
  });
}

class _CatalogLibrary extends BibleLibraryRepository {
  final requests = <Completer<List<BibleModuleInfo>>>[];
  List<BibleModuleInfo> snapshot = [FakeBibleLibrary.english];
  int reads = 0;
  StateError? cacheError;

  @override
  List<BibleModuleInfo> get cachedModules => snapshot;

  @override
  Future<List<BibleModuleInfo>> cachedCatalog() async {
    reads++;
    final error = cacheError;
    if (error != null) throw error;
    return snapshot;
  }

  @override
  Future<List<BibleModuleInfo>> loadCatalog({bool refresh = false}) {
    final result = Completer<List<BibleModuleInfo>>();
    requests.add(result);
    return result.future;
  }
}
