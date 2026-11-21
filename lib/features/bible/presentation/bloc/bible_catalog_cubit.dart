import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';

class BibleCatalogState {
  const BibleCatalogState({
    this.modules = const [],
    this.loading = true,
    this.failed = false,
  });
  final List<BibleModuleInfo> modules;
  final bool loading;
  final bool failed;

  @override
  bool operator ==(Object other) =>
      other is BibleCatalogState &&
      listEquals(modules, other.modules) &&
      loading == other.loading &&
      failed == other.failed;
  @override
  int get hashCode => Object.hash(Object.hashAll(modules), loading, failed);
}

class BibleCatalogCubit extends Cubit<BibleCatalogState> {
  BibleCatalogCubit(this._library) : super(const BibleCatalogState());
  final BibleLibraryRepository _library;
  final _requests = LatestRequestGuard();

  Future<void> load() async {
    final request = _requests.start();
    try {
      final cached = await _library.cachedCatalog();
      if (isClosed || !_requests.isActive(request)) return;
      emit(BibleCatalogState(modules: cached));
      final refreshed = await _library.loadCatalog(refresh: true);
      if (isClosed || !_requests.isActive(request)) return;
      emit(BibleCatalogState(modules: refreshed, loading: false));
    } catch (error, stackTrace) {
      if (isClosed || !_requests.isActive(request)) return;
      addError(error, stackTrace);
      emit(
        BibleCatalogState(
          modules: _library.cachedModules,
          loading: false,
          failed: true,
        ),
      );
    }
  }
}
