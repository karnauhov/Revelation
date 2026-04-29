import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

class PrimarySourceDescriptionPanel extends StatelessWidget {
  final String? descriptionContent;
  final DescriptionKind currentDescriptionType;
  final GreekStrongTapHandler onGreekStrongTap;
  final GreekStrongPickerTapHandler onGreekStrongPickerTap;
  final WordTapHandler onWordTap;
  final bool showStrongInfoIcon;
  final bool canNavigate;
  final bool enableSwipeNavigation;
  final GlobalKey<TooltipState> referenceTooltipKey;
  final VoidCallback onNavigateBackward;
  final VoidCallback onNavigateForward;
  final ValueChanged<DragEndDetails> onHorizontalDragEnd;

  const PrimarySourceDescriptionPanel({
    required this.descriptionContent,
    required this.currentDescriptionType,
    required this.onGreekStrongTap,
    required this.onGreekStrongPickerTap,
    required this.onWordTap,
    required this.showStrongInfoIcon,
    required this.canNavigate,
    required this.enableSwipeNavigation,
    required this.referenceTooltipKey,
    required this.onNavigateBackward,
    required this.onNavigateForward,
    required this.onHorizontalDragEnd,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final tooltipMaxWidth = screenWidth > 432 ? 420.0 : screenWidth - 12.0;

    final descriptionView = Container(
      color: colorScheme.surface,
      child: Stack(
        children: [
          Positioned.fill(
            child: DescriptionMarkdownView(
              data: descriptionContent ?? localizations.click_for_info,
              padding: const EdgeInsets.fromLTRB(8, 2, 8, 8),
              h2FontWeight: currentDescriptionType == DescriptionKind.word
                  ? FontWeight.normal
                  : null,
              onGreekStrongTap: onGreekStrongTap,
              onGreekStrongPickerTap: onGreekStrongPickerTap,
              onWordTap: onWordTap,
              toolbarActions: [
                _DescriptionNavigationToolbarButton(
                  buttonKey: const Key('description_nav_back'),
                  canNavigate: canNavigate,
                  forward: false,
                  tooltip: _buildNavigationTooltip(
                    localizations,
                    forward: false,
                  ),
                  onTap: onNavigateBackward,
                ),
                _DescriptionNavigationToolbarButton(
                  buttonKey: const Key('description_nav_forward'),
                  canNavigate: canNavigate,
                  forward: true,
                  tooltip: _buildNavigationTooltip(
                    localizations,
                    forward: true,
                  ),
                  onTap: onNavigateForward,
                ),
              ],
            ),
          ),
          if (showStrongInfoIcon)
            Positioned(
              top: -8,
              right: -8,
              child: Tooltip(
                key: referenceTooltipKey,
                message: localizations.strong_reference_commentary,
                constraints: BoxConstraints(maxWidth: tooltipMaxWidth),
                showDuration: const Duration(seconds: 12),
                preferBelow: false,
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    referenceTooltipKey.currentState?.ensureTooltipVisible();
                  },
                  child: SizedBox(
                    width: 32,
                    height: 32,
                    child: Center(
                      child: Icon(
                        Icons.info_outline,
                        size: 18,
                        color: colorScheme.primary,
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );

    if (!enableSwipeNavigation) {
      return descriptionView;
    }

    return GestureDetector(
      key: const Key('description_panel_swipe_zone'),
      behavior: HitTestBehavior.translucent,
      onHorizontalDragEnd: onHorizontalDragEnd,
      child: descriptionView,
    );
  }

  String _buildNavigationTooltip(
    AppLocalizations localizations, {
    required bool forward,
  }) {
    return switch (currentDescriptionType) {
      DescriptionKind.word =>
        forward ? localizations.next_word : localizations.previous_word,
      DescriptionKind.verse =>
        forward ? localizations.next_verse : localizations.previous_verse,
      DescriptionKind.strongNumber =>
        forward
            ? localizations.next_dictionary_entry
            : localizations.previous_dictionary_entry,
      DescriptionKind.info =>
        forward
            ? localizations.next_description_item
            : localizations.previous_description_item,
    };
  }
}

class _DescriptionNavigationToolbarButton extends StatelessWidget {
  final Key buttonKey;
  final bool canNavigate;
  final bool forward;
  final String tooltip;
  final VoidCallback onTap;

  const _DescriptionNavigationToolbarButton({
    required this.buttonKey,
    required this.canNavigate,
    required this.forward,
    required this.tooltip,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return DescriptionMarkdownToolbarButton(
      buttonKey: buttonKey,
      tooltip: tooltip,
      icon: forward
          ? Icons.arrow_forward_ios_rounded
          : Icons.arrow_back_ios_new_rounded,
      iconSize: 18,
      enabled: canNavigate,
      onPressed: onTap,
    );
  }
}
