import 'package:flutter/material.dart';
import 'package:revelation/repositories/primary_sources_db_repository.dart';
import 'package:revelation/utils/common.dart';
import '../models/primary_source.dart';

class PrimarySourcesViewModel extends ChangeNotifier {
  final PrimarySourcesDbRepository _primarySourcesRepository;
  final List<PrimarySource> _fullPrimarySources = [];
  final List<PrimarySource> _significantPrimarySources = [];
  final List<PrimarySource> _fragmentsPrimarySources = [];
  bool _isLoading = false;

  List<PrimarySource> get fullPrimarySources => _fullPrimarySources;
  List<PrimarySource> get significantPrimarySources =>
      _significantPrimarySources;
  List<PrimarySource> get fragmentsPrimarySources => _fragmentsPrimarySources;
  bool get isLoading => _isLoading;

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

    try {
      final result = await _primarySourcesRepository.loadGroupedSources();
      _fullPrimarySources.addAll(result.fullPrimarySources);
      _significantPrimarySources.addAll(result.significantPrimarySources);
      _fragmentsPrimarySources.addAll(result.fragmentsPrimarySources);
    } catch (error, stackTrace) {
      log.error('Primary sources loading error: $error', stackTrace);
    } finally {
      _isLoading = false;
    }

    notifyListeners();
  }
}
