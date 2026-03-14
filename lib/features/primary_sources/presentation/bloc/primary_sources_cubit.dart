import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_state.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/core/logging/common_logger.dart';

class PrimarySourcesCubit extends Cubit<PrimarySourcesState> {
  PrimarySourcesCubit(this._repository) : super(PrimarySourcesState.initial());

  final PrimarySourcesDbRepository _repository;
  final LatestRequestGuard _loadRequestGuard = LatestRequestGuard();

  Future<void> loadPrimarySources() async {
    final requestToken = _loadRequestGuard.start();
    if (!_canApplyRequest(requestToken)) {
      return;
    }

    emit(
      state.copyWith(
        isLoading: true,
        full: const <PrimarySource>[],
        significant: const <PrimarySource>[],
        fragments: const <PrimarySource>[],
        clearFailure: true,
      ),
    );

    try {
      final result = await _repository.loadGroupedSourcesResult();
      if (!_canApplyRequest(requestToken)) {
        return;
      }

      if (result is AppFailureResult<PrimarySourcesLoadResult>) {
        log.error(
          'Primary sources loading error: ${result.error.message}',
          result.error.stackTrace,
        );
        emit(state.copyWith(isLoading: false, failure: result.error));
        return;
      }

      if (result is AppSuccess<PrimarySourcesLoadResult>) {
        final grouped = result.data;
        emit(
          state.copyWith(
            isLoading: false,
            full: grouped.fullPrimarySources,
            significant: grouped.significantPrimarySources,
            fragments: grouped.fragmentsPrimarySources,
            clearFailure: true,
          ),
        );
      }
    } catch (error, stackTrace) {
      if (!_canApplyRequest(requestToken)) {
        return;
      }
      log.error('Primary sources loading error: $error', stackTrace);
      emit(
        state.copyWith(
          isLoading: false,
          failure: AppFailure.unknown(
            'Unexpected error while loading primary sources.',
            cause: error,
            stackTrace: stackTrace,
          ),
        ),
      );
    }
  }

  bool _canApplyRequest(RequestToken token) {
    return !isClosed && _loadRequestGuard.isActive(token);
  }

  @override
  Future<void> close() async {
    _loadRequestGuard.cancelActive();
    return super.close();
  }
}
