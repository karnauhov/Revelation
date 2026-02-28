import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/common_widgets/error_message.dart';
import 'package:revelation/managers/db_manager.dart';
import 'package:revelation/viewmodels/settings_view_model.dart';
import 'topic_card.dart';
import '../../models/topic_info.dart';

class TopicList extends StatefulWidget {
  const TopicList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _TopicListState createState() => _TopicListState();
}

class _TopicListState extends State<TopicList> {
  late Future<List<TopicInfo>> _topicsFuture;
  String? _topicsLanguage;

  @override
  void initState() {
    super.initState();
    _topicsFuture = Future.value(const []);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final language = Provider.of<SettingsViewModel>(
      context,
    ).settings.selectedLanguage;
    if (_topicsLanguage != language) {
      _topicsLanguage = language;
      _topicsFuture = _loadTopicsFromDb(language);
    }
  }

  Future<List<TopicInfo>> _loadTopicsFromDb(String language) async {
    await DBManager().updateLanguage(language);
    final topics = await DBManager().getTopics();
    return topics
        .map(
          (topic) => TopicInfo(
            name: topic.name,
            idIcon: topic.idIcon,
            description: topic.description,
            route: topic.route,
          ),
        )
        .toList(growable: false);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    return FutureBuilder<List<TopicInfo>>(
      future: _topicsFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final topics = snapshot.data!;
          return Column(
            children: topics.map((topic) => TopicCard(topic: topic)).toList(),
          );
        } else if (snapshot.hasError) {
          return ErrorMessage(
              errorMessage: AppLocalizations.of(context)!.error_loading_topics);
        } else {
          return Center(
            child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary)),
          );
        }
      },
    );
  }
}
