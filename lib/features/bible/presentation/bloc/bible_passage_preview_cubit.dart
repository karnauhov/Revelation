import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

typedef BiblePassageLine = ({
  BibleVerseReference reference,
  String? translation,
  String? original,
});

class BiblePassagePreviewState {
  const BiblePassagePreviewState({
    this.lines = const [],
    this.verseMap,
    this.module,
    this.original,
    this.loading = true,
  });

  final List<BiblePassageLine> lines;
  final BibleVerseMap? verseMap;
  final BibleModuleInfo? module;
  final BibleModuleInfo? original;
  final bool loading;

  bool canStep(int direction) {
    if (lines.isEmpty || verseMap == null) return false;
    final edge = direction < 0 ? lines.first : lines.last;
    return verseMap!.offsetReference(edge.reference, direction) != null;
  }

  @override
  bool operator ==(Object other) =>
      other is BiblePassagePreviewState &&
      listEquals(lines, other.lines) &&
      verseMap == other.verseMap &&
      module == other.module &&
      original == other.original &&
      loading == other.loading;

  @override
  int get hashCode =>
      Object.hash(Object.hashAll(lines), verseMap, module, original, loading);
}

class BiblePassagePreviewCubit extends Cubit<BiblePassagePreviewState> {
  BiblePassagePreviewCubit(this._library)
    : super(const BiblePassagePreviewState());

  final BibleLibraryRepository _library;
  final _requests = LatestRequestGuard();
  String? _requestedModule;

  Future<void> open(
    List<BibleVerseReference> references, {
    BibleVerseMap? verseMap,
    String? moduleFile,
  }) {
    _requestedModule = moduleFile;
    return _read(references, verseMap);
  }

  Future<void> retry() =>
      _read(state.lines.map((line) => line.reference).toList(), state.verseMap);

  Future<void> step(int direction) async {
    if (!state.canStep(direction)) return;
    final map = state.verseMap!;
    await _read([
      for (final line in state.lines)
        map.offsetReference(line.reference, direction)!,
    ], map);
  }

  Future<void> _read(
    List<BibleVerseReference> references,
    BibleVerseMap? map,
  ) async {
    final request = _requests.start();
    emit(
      BiblePassagePreviewState(
        verseMap: map,
        lines: List.unmodifiable([
          for (final reference in references)
            (reference: reference, translation: null, original: null),
        ]),
      ),
    );
    final keys = references.map((ref) => ref.verseKey).toList(growable: false);

    Future<BiblePreview?> readEdition(String? file) async {
      try {
        return await _library.loadPreview(keys, moduleFile: file);
      } catch (error, stackTrace) {
        if (!isClosed && _requests.isActive(request)) {
          addError(error, stackTrace);
        }
        return null;
      }
    }

    Future<BibleVerseMap?> readMap() async {
      try {
        return map ?? await BibleVerseMap.loadFromAssets();
      } catch (error, stackTrace) {
        if (!isClosed && _requests.isActive(request)) {
          addError(error, stackTrace);
        }
        return null;
      }
    }

    final (verseMap, translation, greek) = await (
      readMap(),
      readEdition(_requestedModule),
      readEdition(AppConstants.defaultBibleModuleDB),
    ).wait;
    if (isClosed || !_requests.isActive(request)) return;

    final translations = {
      if (translation != null)
        for (final verse in translation.verses) verse.verseKey: verse.text,
    };
    final originals = {
      if (greek != null)
        for (final verse in greek.verses) verse.verseKey: verse.text,
    };
    emit(
      BiblePassagePreviewState(
        module: translation?.module,
        original: greek?.module,
        verseMap: verseMap,
        loading: false,
        lines: List.unmodifiable([
          for (final ref in references)
            (
              reference: ref,
              translation: translations[ref.verseKey],
              original: originals[ref.verseKey],
            ),
        ]),
      ),
    );
  }
}
