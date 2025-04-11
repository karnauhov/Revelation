import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../models/topic_info.dart';
import '../../utils/common.dart';

class TopicCard extends StatelessWidget {
  final TopicInfo topic;

  const TopicCard({super.key, required this.topic});

  @override
  Widget build(BuildContext context) {
    const iconWidth = 48.0;
    const iconHeight = 48.0;

    return Card(
      margin: EdgeInsets.symmetric(vertical: 4),
      color: Theme.of(context).colorScheme.surfaceContainer,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => context.push('/topic', extra: {
          'name': topic.name,
          'description': topic.description,
          'file': topic.route
        }),
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: SvgPicture.asset(
            topic.idIcon.isNotEmpty
                ? "assets/images/UI/${topic.idIcon}.svg"
                : 'assets/images/UI/code.svg',
            width: iconWidth,
            height: iconHeight,
            placeholderBuilder: (BuildContext context) =>
                CircularProgressIndicator(),
          ),
        ),
        title: Text(
          locLinks(context, topic.name),
          style: Theme.of(context)
              .textTheme
              .titleMedium
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          locLinks(context, topic.description),
          style: TextStyle(
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
      ),
    );
  }
}
