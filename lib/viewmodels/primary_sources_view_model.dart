import 'package:flutter/material.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/repositories/primary_sources_db_repository.dart';
import 'package:revelation/utils/common.dart';
import '../models/primary_source.dart';

class PrimarySourcesViewModel extends ChangeNotifier {
  final PrimarySourcesDbRepository _primarySourcesRepository;
  final List<PrimarySource> _fullPrimarySources = [];
  final List<PrimarySource> _significantPrimarySources = [];
  final List<PrimarySource> _fragmentsPrimarySources = [];
  bool _isLoading = false;
  AppFailure? _lastFailure;
  final LatestRequestGuard _loadRequestGuard = LatestRequestGuard();
  bool _isDisposed = false;

  List<PrimarySource> get fullPrimarySources => _fullPrimarySources;
  List<PrimarySource> get significantPrimarySources =>
      _significantPrimarySources;
  List<PrimarySource> get fragmentsPrimarySources => _fragmentsPrimarySources;
  bool get isLoading => _isLoading;
  AppFailure? get lastFailure => _lastFailure;
  bool get hasError => _lastFailure != null;

  PrimarySourcesViewModel(this._primarySourcesRepository);

  Future<void> loadPrimarySources() async {
    final requestToken = _loadRequestGuard.start();
    if (!_canApplyRequest(requestToken)) {
      return;
    }

    _isLoading = true;
    _fullPrimarySources.clear();
    _significantPrimarySources.clear();
    _fragmentsPrimarySources.clear();
    _lastFailure = null;
    notifyListeners();

    try {
      final result = await _primarySourcesRepository.loadGroupedSourcesResult();
      if (!_canApplyRequest(requestToken)) {
        return;
      }

      if (result is AppFailureResult<PrimarySourcesLoadResult>) {
        _lastFailure = result.error;
        log.error(
          'Primary sources loading error: ${result.error.message}',
          result.error.stackTrace,
        );
      } else if (result is AppSuccess<PrimarySourcesLoadResult>) {
        final grouped = result.data;
        _fullPrimarySources.addAll(grouped.fullPrimarySources);
        _significantPrimarySources.addAll(grouped.significantPrimarySources);
        _fragmentsPrimarySources.addAll(grouped.fragmentsPrimarySources);
      }
    } catch (error, stackTrace) {
      if (!_canApplyRequest(requestToken)) {
        return;
      }
      log.error('Primary sources loading error: $error', stackTrace);
      _lastFailure = AppFailure.unknown(
        'Unexpected error while loading primary sources.',
        cause: error,
        stackTrace: stackTrace,
      );
    } finally {
      if (_canApplyRequest(requestToken)) {
        _isLoading = false;
        notifyListeners();
      }
    }
  }

  bool _canApplyRequest(RequestToken token) {
    return !_isDisposed && _loadRequestGuard.isActive(token);
  }

  @override
  void notifyListeners() {
    if (_isDisposed) {
      return;
    }
    super.notifyListeners();
  }

  @override
  void dispose() {
    _loadRequestGuard.cancelActive();
    _isDisposed = true;
    super.dispose();
  }
}
