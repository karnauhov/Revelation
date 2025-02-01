import 'package:flutter/material.dart';
import '../models/primary_source.dart';
import '../repositories/primary_sources_repository.dart';

class PrimarySourcesViewModel extends ChangeNotifier {
  final PrimarySourcesRepository _primarySourcesRepository;
  final List<PrimarySource> _primarySources = [];
  List<PrimarySource> get primarySources => _primarySources;
  PrimarySourcesViewModel(this._primarySourcesRepository);

  void loadPrimarySources(BuildContext context) {
    _primarySources.clear();
    _primarySources
        .addAll(_primarySourcesRepository.getPrimarySources(context));
    notifyListeners();
  }
}
