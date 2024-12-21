import 'package:flutter/material.dart';

class MainViewModel extends ChangeNotifier {
  MainViewModel();

  Future<void> initializeData() async {
    notifyListeners();
  }
}
