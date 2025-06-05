import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/common_widgets/error_message.dart';
import 'topic_card.dart';
import '../../models/topic_info.dart';
import '../../utils/common.dart';

class TopicList extends StatefulWidget {
  const TopicList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _TopicListState createState() => _TopicListState();
}

class _TopicListState extends State<TopicList> {
  late Future<List<TopicInfo>> _topicsFuture;

  @override
  void initState() {
    super.initState();
    _topicsFuture = parseTopics(rootBundle, 'assets/data/topics.xml');
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
