import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';

class TopicCard extends StatelessWidget {
  const TopicCard({super.key, required this.topic, required this.iconResource});

  final TopicInfo topic;
  final TopicResource? iconResource;

  Widget _buildDefaultIcon(Color color) {
    return SvgPicture.asset(
      'assets/images/UI/code.svg',
      width: 48,
      height: 48,
      colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
    );
  }

  @override
  Widget build(BuildContext context) {
    const iconWidth = 48.0;
    const iconHeight = 48.0;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final cardColor = colorScheme.surfaceContainerHighest;
    final titleColor = colorScheme.primary;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      color: cardColor,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => context.push(
          '/topic',
          extra: TopicRouteArgs(
            name: topic.name,
            description: topic.description,
            file: topic.route,
          ),
        ),
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: _buildIcon(iconResource, titleColor, iconWidth, iconHeight),
        ),
        title: Text(
          topic.name,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: titleColor,
          ),
        ),
        subtitle: Text(
          topic.description,
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(color: titleColor),
        ),
        trailing: Icon(Icons.chevron_right, color: titleColor),
      ),
    );
  }

  Widget _buildIcon(
    TopicResource? resource,
    Color titleColor,
    double iconWidth,
    double iconHeight,
  ) {
    if (resource == null) {
      return _buildDefaultIcon(titleColor);
    }

    final mimeType = resource.mimeType.toLowerCase();
    final isSvg =
        mimeType.contains('svg') ||
        resource.fileName.toLowerCase().endsWith('.svg');
    if (isSvg) {
      return SvgPicture.memory(
        resource.data,
        width: iconWidth,
        height: iconHeight,
        colorFilter: ColorFilter.mode(titleColor, BlendMode.srcIn),
      );
    }

    return Image.memory(
      resource.data,
      width: iconWidth,
      height: iconHeight,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) =>
          _buildDefaultIcon(titleColor),
    );
  }
}
