import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import '../../viewmodels/settings_view_model.dart';
import '../../utils/app_constants.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    final settingsViewModel = Provider.of<SettingsViewModel>(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.settings_screen),
      ),
      body: ListView(
        children: [
          ListTile(
            title: Text(AppLocalizations.of(context)!.language),
            subtitle: Text(AppConstants
                    .languages[settingsViewModel.settings.selectedLanguage] ??
                ""),
            trailing: const Icon(Icons.arrow_forward_ios),
            onTap: () async {
              final selected = await _showLanguageDialog(
                  context, settingsViewModel.settings.selectedLanguage);
              if (selected != null) {
                settingsViewModel.changeLanguage(selected);
              }
            },
          ),
        ],
      ),
    );
  }

  Future<String?> _showLanguageDialog(
      BuildContext context, String currentLanguage) async {
    return showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: AppConstants.languages.keys.length,
              itemBuilder: (context, index) {
                final languageCode =
                    AppConstants.languages.keys.elementAt(index);
                final languageName = AppConstants.languages[languageCode]!;
                return ListTile(
                  title: Text(languageName),
                  selected: languageCode == currentLanguage,
                  onTap: () {
                    Navigator.pop(context, languageCode);
                  },
                );
              },
            ),
          ),
        );
      },
    );
  }
}
