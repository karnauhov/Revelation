import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/common_widgets/error_message.dart';
import 'package:revelation/features/settings/presentation/viewmodels/settings_view_model.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'topic_card.dart';

class TopicList extends StatefulWidget {
  const TopicList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _TopicListState createState() => _TopicListState();
}

class _TopicListState extends State<TopicList> {
  final TopicsRepository _topicsRepository = TopicsRepository();

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
      _topicsFuture = _loadTopics(language);
    }
  }

  Future<List<TopicInfo>> _loadTopics(String language) async {
    return _topicsRepository.getTopics(language: language);
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
            errorMessage: AppLocalizations.of(context)!.error_loading_topics,
          );
        } else {
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary),
            ),
          );
        }
      },
    );
  }
}
