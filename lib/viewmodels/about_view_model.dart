import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:flutter/services.dart';

class AboutViewModel extends ChangeNotifier {
  String appVersion = '';
  String buildNumber = '';
  String changelog = '';

  bool isLoading = true;
  bool isChangelogExpanded = false;
  bool isAcknowledgementsExpanded = false;

  AboutViewModel() {
    _initData();
  }

  Future<void> _initData() async {
    await Future.wait([
      _initPackageInfo(),
      _loadChangelog(),
    ]);
    isLoading = false;
    notifyListeners();
  }

  Future<void> _initPackageInfo() async {
    final PackageInfo packageInfo = await PackageInfo.fromPlatform();
    appVersion = packageInfo.version;
    buildNumber = packageInfo.buildNumber;
  }

  Future<void> _loadChangelog() async {
    try {
      final String log = await rootBundle.loadString('CHANGELOG.md');
      changelog = log;
    } catch (e) {
      changelog = 'No changelog available.';
    }
  }

  void toggleChangelogExpanded() {
    isChangelogExpanded = !isChangelogExpanded;
    notifyListeners();
  }

  void toggleAcknowledgements() {
    isAcknowledgementsExpanded = !isAcknowledgementsExpanded;
    notifyListeners();
  }
}
