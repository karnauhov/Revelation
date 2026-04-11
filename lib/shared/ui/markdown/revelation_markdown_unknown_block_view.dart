import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';

class RevelationMarkdownUnknownBlockUpdateAction {
  const RevelationMarkdownUnknownBlockUpdateAction({required this.routeName});

  final String routeName;

  static RevelationMarkdownUnknownBlockUpdateAction? resolve({
    bool? isWebOverride,
  }) {
    if (isWebOverride ?? isWeb()) {
      return null;
    }

    return const RevelationMarkdownUnknownBlockUpdateAction(
      routeName: 'download',
    );
  }
}

class RevelationMarkdownUnknownBlockView extends StatelessWidget {
  const RevelationMarkdownUnknownBlockView({required this.block, super.key});

  final RevelationMarkdownUnknownBlockData block;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final updateAction = RevelationMarkdownUnknownBlockUpdateAction.resolve();

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: colorScheme.outlineVariant),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.extension_off_outlined,
                  color: colorScheme.onSurfaceVariant,
                  size: 32,
                ),
                const SizedBox(height: 12),
                Text(
                  l10n.markdown_unknown_block_title,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  l10n.markdown_unknown_block_description(block.name),
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
                if (updateAction != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    l10n.markdown_unknown_block_update_hint,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 16),
                  FilledButton.tonalIcon(
                    onPressed: () => _openDownloadScreen(
                      context,
                      routeName: updateAction.routeName,
                    ),
                    icon: const Icon(Icons.system_update_alt_outlined),
                    label: Text(l10n.markdown_unknown_block_update_action),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _openDownloadScreen(BuildContext context, {required String routeName}) {
    final router = GoRouter.maybeOf(context);
    if (router == null) {
      return;
    }
    unawaited(router.pushNamed(routeName));
  }
}
