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
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final cardColor = colorScheme.surfaceContainerHighest;
    final onSurfaceColor = colorScheme.onSurface;
    final onSurfaceVariantColor = colorScheme.onSurfaceVariant;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      color: cardColor,
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
            placeholderBuilder: (BuildContext context) => Center(
              child: SizedBox(
                width: 24.0,
                height: 24.0,
                child: CircularProgressIndicator(
                  strokeWidth: 2.0,
                  color: colorScheme.primary,
                ),
              ),
            ),
          ),
        ),
        title: Text(
          locLinks(context, topic.name),
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: onSurfaceColor,
              ),
        ),
        subtitle: Text(
          locLinks(context, topic.description),
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: onSurfaceVariantColor,
              ),
        ),
        trailing: Icon(
          Icons.chevron_right,
          color: onSurfaceVariantColor,
        ),
      ),
    );
  }
}
