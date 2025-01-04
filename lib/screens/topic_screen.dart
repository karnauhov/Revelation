import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:provider/provider.dart';

import '../utils/common.dart';
import '../viewmodels/settings_view_model.dart';

class TopicScreen extends StatelessWidget {
  final String? name;
  final String? description;
  final String? file;
  const TopicScreen({super.key, this.name, this.description, this.file});

  @override
  Widget build(BuildContext context) {
    final settingsViewModel = Provider.of<SettingsViewModel>(context);
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              locLinks(context, name ?? ""),
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              locLinks(context, description ?? ""),
              style: Theme.of(context)
                  .textTheme
                  .labelSmall
                  ?.copyWith(fontWeight: FontWeight.normal),
            ),
          ],
        ),
      ),
      body: FutureBuilder<String>(
        future: loadMarkdownAsset(
            file, settingsViewModel.settings.selectedLanguage),
        builder: (context, snapshot) {
          return Markdown(data: snapshot.data ?? '');
        },
      ),
    );
  }

  Future<String> loadMarkdownAsset(String? file, String language) async {
    if (file != null) {
      final path = "assets/data/topics/${file}_$language.md";
      return await rootBundle.loadString(path);
    } else {
      return "";
    }
  }
}
