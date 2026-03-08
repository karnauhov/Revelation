import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/db/db_common.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';

class TopicCard extends StatefulWidget {
  final TopicInfo topic;

  const TopicCard({super.key, required this.topic});

  @override
  State<TopicCard> createState() => _TopicCardState();
}

class _TopicCardState extends State<TopicCard> {
  final TopicsRepository _topicsRepository = TopicsRepository();

  late Future<AppResult<CommonResource?>> _iconFuture;

  @override
  void initState() {
    super.initState();
    _iconFuture = _loadIcon();
  }

  @override
  void didUpdateWidget(covariant TopicCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.topic.idIcon != widget.topic.idIcon) {
      _iconFuture = _loadIcon();
    }
  }

  Future<AppResult<CommonResource?>> _loadIcon() async {
    final key = widget.topic.idIcon.trim();
    return _topicsRepository.getCommonResource(key);
  }

  Widget _buildDefaultIcon(Color color) {
    return SvgPicture.asset(
      'assets/images/UI/code.svg',
      width: 48,
      height: 48,
      colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
    );
  }

  Widget _buildLoadingIcon(Color color) {
    return Center(
      child: SizedBox(
        width: 24.0,
        height: 24.0,
        child: CircularProgressIndicator(strokeWidth: 2.0, color: color),
      ),
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
            name: widget.topic.name,
            description: widget.topic.description,
            file: widget.topic.route,
          ),
        ),
        leading: SizedBox(
          width: iconWidth,
          height: iconHeight,
          child: FutureBuilder<AppResult<CommonResource?>>(
            future: _iconFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return _buildLoadingIcon(colorScheme.primary);
              }
              final result = snapshot.data;
              if (result is! AppSuccess<CommonResource?>) {
                return _buildDefaultIcon(titleColor);
              }
              final resource = result.data;
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
                  placeholderBuilder: (context) =>
                      _buildLoadingIcon(colorScheme.primary),
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
            },
          ),
        ),
        title: Text(
          widget.topic.name,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: titleColor,
          ),
        ),
        subtitle: Text(
          widget.topic.description,
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(color: titleColor),
        ),
        trailing: Icon(Icons.chevron_right, color: titleColor),
      ),
    );
  }
}
