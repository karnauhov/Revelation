import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_player.dart';

typedef RevelationMarkdownYoutubeEmbedBuilder =
    Widget Function({Key? key, required RevelationMarkdownYoutubeData video});

class RevelationMarkdownYoutubeView extends StatelessWidget {
  const RevelationMarkdownYoutubeView({required this.video, super.key});

  @visibleForTesting
  static RevelationMarkdownYoutubeEmbedBuilder? embedBuilderForTest;

  final RevelationMarkdownYoutubeData video;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final targetPlayerWidth = video.maxWidth ?? 960;

    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: targetPlayerWidth),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: AspectRatio(
            aspectRatio: video.resolvedAspectRatio,
            child: video.isValid
                ? _buildEmbed(video)
                : _InvalidYoutubeCard(
                    title: l10n.markdown_youtube_unavailable_title,
                    description: l10n.markdown_youtube_unavailable_description,
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmbed(RevelationMarkdownYoutubeData video) {
    final builder = embedBuilderForTest ?? buildRevelationMarkdownYoutubePlayer;
    return builder(
      key: ValueKey('markdown-youtube-player-${video.viewTypeKey}'),
      video: video,
    );
  }
}

class _InvalidYoutubeCard extends StatelessWidget {
  const _InvalidYoutubeCard({required this.title, required this.description});

  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.play_circle_outline,
                size: 36,
                color: colorScheme.onSurfaceVariant,
              ),
              const SizedBox(height: 12),
              Text(
                title,
                textAlign: TextAlign.center,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                description,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
