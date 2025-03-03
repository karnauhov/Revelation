import 'package:flutter/material.dart';
import '../models/primary_source.dart';
import '../repositories/primary_sources_repository.dart';

class PrimarySourcesViewModel extends ChangeNotifier {
  final PrimarySourcesRepository _primarySourcesRepository;
  final List<PrimarySource> _fullPrimarySources = [];
  final List<PrimarySource> _significantPrimarySources = [];
  final List<PrimarySource> _fragmentsPrimarySources = [];
  List<PrimarySource> get fullPrimarySources => _fullPrimarySources;
  List<PrimarySource> get significantPrimarySources =>
      _significantPrimarySources;
  List<PrimarySource> get fragmentsPrimarySources => _fragmentsPrimarySources;
  PrimarySourcesViewModel(this._primarySourcesRepository);

  void loadPrimarySources(BuildContext context) {
    _fullPrimarySources.clear();
    _significantPrimarySources.clear();
    _fragmentsPrimarySources.clear();

    _fullPrimarySources
        .addAll(_primarySourcesRepository.getFullPrimarySources(context));
    _significantPrimarySources.addAll(
        _primarySourcesRepository.getSignificantPrimarySources(context));
    _fragmentsPrimarySources
        .addAll(_primarySourcesRepository.getFragmentsPrimarySources(context));

    notifyListeners();
  }
}
