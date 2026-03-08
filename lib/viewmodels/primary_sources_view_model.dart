import 'package:flutter/material.dart';
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

  List<PrimarySource> get fullPrimarySources => _fullPrimarySources;
  List<PrimarySource> get significantPrimarySources =>
      _significantPrimarySources;
  List<PrimarySource> get fragmentsPrimarySources => _fragmentsPrimarySources;
  bool get isLoading => _isLoading;
  AppFailure? get lastFailure => _lastFailure;
  bool get hasError => _lastFailure != null;

  PrimarySourcesViewModel(this._primarySourcesRepository);

  Future<void> loadPrimarySources() async {
    if (_isLoading) {
      return;
    }

    _isLoading = true;
    notifyListeners();

    _fullPrimarySources.clear();
    _significantPrimarySources.clear();
    _fragmentsPrimarySources.clear();
    _lastFailure = null;

    try {
      final result = await _primarySourcesRepository.loadGroupedSourcesResult();
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
      log.error('Primary sources loading error: $error', stackTrace);
      _lastFailure = AppFailure.unknown(
        'Unexpected error while loading primary sources.',
        cause: error,
        stackTrace: stackTrace,
      );
    } finally {
      _isLoading = false;
    }

    notifyListeners();
  }
}
