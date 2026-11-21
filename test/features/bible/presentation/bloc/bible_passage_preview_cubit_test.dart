import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_passage_preview_cubit.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

import '../../../../test_harness/fakes/fake_allusion_repositories.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap map;
  setUpAll(() async => map = await BibleVerseMap.loadFromAssets());

  test(
    'translation and Greek are paired by verse key, with an independent retry',
    () async {
      final library = _ControlledLibrary()..failOriginal = true;
      final cubit = BiblePassagePreviewCubit(library);
      addTearDown(cubit.close);
      await cubit.open(
        [map.referenceForKey('001')!, map.referenceForKey('002')!],
        verseMap: map,
        moduleFile: FakeBibleLibrary.ukrainian.fileName,
      );
      expect(cubit.state.module, FakeBibleLibrary.ukrainian);
      expect(cubit.state.original, isNull);
      expect(cubit.state.canStep(-1), isFalse);
      expect(cubit.state.lines.last.translation, contains('002'));
      library.failOriginal = false;
      await cubit.retry();
      expect(cubit.state.original, FakeBibleLibrary.greek);
      expect(cubit.state.lines.first.original, contains('G10'));
      expect(cubit.state.lines.map((line) => line.reference.verseKey), [
        '001',
        '002',
      ]);
      expect(library.previewCalls, 3);
    },
  );

  test(
    'a late response cannot move the reader back to an older verse',
    () async {
      final library = _ControlledLibrary();
      final earlier = Completer<void>();
      library.waitForKey['001'] = earlier;
      final cubit = BiblePassagePreviewCubit(library);
      addTearDown(cubit.close);
      final first = cubit.open([map.referenceForKey('001')!], verseMap: map);
      await cubit.step(1);
      expect(cubit.state.lines.single.reference.verseKey, '002');
      earlier.complete();
      await first;
      expect(cubit.state.lines.single.translation, contains('002'));
      expect(library.previewCalls, 4);
    },
  );

  test('closing before the editions return ignores both completions', () async {
    final library = _ControlledLibrary();
    final pending = Completer<void>();
    library.waitForKey['001'] = pending;
    final cubit = BiblePassagePreviewCubit(library);
    final read = cubit.open([map.referenceForKey('001')!], verseMap: map);
    final beforeClose = cubit.state;
    await cubit.close();
    pending.complete();
    await read;
    expect(cubit.state, beforeClose);
  });

  test(
    'moving a range crosses book boundaries and stops at the end of the canon',
    () async {
      final lastInGenesis = map.referenceFor(bookId: 1, chapter: 50, verse: 26);
      final cubit = BiblePassagePreviewCubit(FakeBibleLibrary());
      addTearDown(cubit.close);
      await cubit.open([
        map.offsetReference(lastInGenesis, -1)!,
        lastInGenesis,
      ], verseMap: map);
      await cubit.step(1);
      expect(cubit.state.lines.first.reference, lastInGenesis);
      expect(
        cubit.state.lines.last.reference,
        map.referenceFor(bookId: 2, chapter: 1, verse: 1),
      );
      final end = map.referenceForKey(map.lastVerseKey)!;
      await cubit.open([map.offsetReference(end, -1)!, end], verseMap: map);
      await cubit.step(1);
      expect(cubit.state.lines.last.reference, end);
      expect(cubit.state.canStep(1), isFalse);
    },
  );
}

class _ControlledLibrary extends FakeBibleLibrary {
  bool failOriginal = false;
  final waitForKey = <String, Completer<void>>{};

  @override
  Future<BiblePreview> loadPreview(
    List<String> keys, {
    String? moduleFile,
  }) async {
    final wait = waitForKey[keys.first];
    if (wait != null) await wait.future;
    if (failOriginal && moduleFile == FakeBibleLibrary.greek.fileName) {
      throw StateError('Original unavailable');
    }
    final result = await super.loadPreview(keys, moduleFile: moduleFile);
    return (module: result.module, verses: result.verses.reversed.toList());
  }
}
