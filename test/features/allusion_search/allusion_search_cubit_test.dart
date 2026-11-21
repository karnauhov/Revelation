import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import '../../test_harness/fakes/fake_allusion_repositories.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap map;
  setUpAll(() async {
    map = await BibleVerseMap.loadFromAssets();
  });

  test(
    'an early search awaits preparation while the source remains editable',
    () async {
      final repo = _DelayedIndex(map);
      final cubit = AllusionSearchCubit(repo, FakeBibleLibrary());
      addTearDown(cubit.close);
      await cubit.ensureLoaded();
      final preparation = cubit.prepareIndex();
      final obsolete = cubit.search();
      await cubit.search(); // A second tap does not start a second search.
      expect(cubit.state.status, AllusionStatus.searching);
      cubit.updateQuery(scope: AllusionScope.oldTestament, length: 2);
      expect(cubit.state.status, AllusionStatus.ready);
      expect(cubit.state.sourceReferences, hasLength(2));
      final current = cubit.search();
      repo.ready.complete(repo.index);
      await Future.wait([obsolete, current, preparation]);
      expect(repo.checks, 1);
      expect(repo.searches, 1);
      expect(cubit.state.results!.end.verse, 2);
      expect(
        cubit.state.matches.every((match) => match.reference.bookId <= 39),
        isTrue,
      );
    },
  );

  test(
    'warm-up and repeated searches share one revision check per visit',
    () async {
      final repo = _DelayedIndex(map);
      repo.ready.complete(repo.index);
      final cubit = AllusionSearchCubit(repo, FakeBibleLibrary());
      addTearDown(cubit.close);
      await cubit.beginVisit();
      await cubit.prepareIndex();
      await cubit.search();
      await cubit.search();
      expect(repo.checks, 1);
      expect(repo.searches, 2);
      await cubit.beginVisit();
      await cubit
          .search(); // The user can search before the next post-frame warm-up.
      await cubit.prepareIndex();
      expect(repo.checks, 2);
      expect(repo.searches, 3);
    },
  );

  test(
    'a new visit checks after an outstanding warm-up and retries its own failure',
    () async {
      final repo = _DelayedIndex(map);
      final cubit = AllusionSearchCubit(repo, FakeBibleLibrary());
      addTearDown(cubit.close);
      await cubit.beginVisit();
      final first = cubit.prepareIndex();
      final previous = repo.ready;
      final rechecked = Completer<void>();
      repo.onCheck = () {
        if (!rechecked.isCompleted) rechecked.complete();
      };
      repo.ready = Completer<AllusionIndex>();
      await cubit.beginVisit();
      final second = cubit.prepareIndex();
      expect(repo.checks, 1);
      previous.completeError(StateError('Previous connection closed'));
      await first;
      await rechecked.future;
      expect(repo.checks, 2);
      repo.ready.completeError(StateError('Offline'));
      await second;
      repo.ready = Completer<AllusionIndex>()..complete(repo.index);
      await cubit.search();
      await cubit.search();
      expect(repo.checks, 3);
      expect(repo.searches, 2);
    },
  );

  test('closing before index completion skips pending searches', () async {
    final repo = _DelayedIndex(map);
    final cubit = AllusionSearchCubit(
      repo,
      FakeBibleLibrary(),
      initialVerseMap: map,
    );
    final running = cubit.search();
    await cubit.close();
    repo.ready.complete(repo.index);
    await running;
    expect(repo.searches, 0);
  });

  test(
    'stale Greek passages cannot replace a new selection or emit after close',
    () async {
      final library = _DelayedOriginal();
      final cubit = AllusionSearchCubit(
        FakeAllusionRepository(map),
        library,
        initialVerseMap: map,
      );
      final first = cubit.beginVisit();
      cubit.updateQuery(verse: 2);
      final key = cubit.state.sourceReferences.single.verseKey;
      library.complete(1, key);
      await Future<void>.delayed(Duration.zero);
      library.complete(0, 'old');
      await first;
      expect(cubit.state.originals, {key: 'word G10'});
      cubit.updateQuery(verse: 3);
      await cubit.close();
      library.complete(2, 'late');
      await Future<void>.delayed(Duration.zero);
      expect(cubit.state.originals, isNull);
    },
  );

  test('failed preparation keeps the form and permits a retry', () async {
    final repo = _DelayedIndex(map);
    final cubit = AllusionSearchCubit(
      repo,
      FakeBibleLibrary(),
      initialVerseMap: map,
    );
    addTearDown(cubit.close);
    final search = cubit.search();
    repo.ready.completeError(StateError('unavailable'));
    await search;
    expect(cubit.state.status, AllusionStatus.failure);
    expect(cubit.state.verseMap, map);
    repo.ready = Completer<AllusionIndex>()..complete(repo.index);
    await cubit.search();
    expect(cubit.state.results, isNotNull);
    expect(cubit.state.status, AllusionStatus.ready);
  });
}

class _DelayedOriginal extends FakeBibleLibrary {
  final requests = <Completer<BiblePreview>>[];
  void complete(int i, String key) => requests[i].complete((
    module: FakeBibleLibrary.greek,
    verses: [BibleVerseText(verseKey: key, text: 'word G10')],
  ));
  @override
  Future<BiblePreview> loadPreview(List<String> keys, {String? moduleFile}) {
    if (moduleFile != FakeBibleLibrary.greek.fileName)
      return super.loadPreview(keys, moduleFile: moduleFile);
    final request = Completer<BiblePreview>();
    requests.add(request);
    return request.future;
  }
}

class _DelayedIndex extends FakeAllusionRepository {
  _DelayedIndex(super.map);
  Completer<AllusionIndex> ready = Completer<AllusionIndex>();
  int checks = 0;
  void Function()? onCheck;
  @override
  Future<AllusionIndex> loadIndex() {
    checks++;
    onCheck?.call();
    return ready.future;
  }
}
