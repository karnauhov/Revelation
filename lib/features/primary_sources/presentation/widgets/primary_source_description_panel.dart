import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

class PrimarySourceDescriptionPanel extends StatelessWidget {
  final String? descriptionContent;
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
              padding: const EdgeInsets.fromLTRB(8, 2, 8, 58),
              onGreekStrongTap: onGreekStrongTap,
              onGreekStrongPickerTap: onGreekStrongPickerTap,
              onWordTap: onWordTap,
            ),
          ),
          Positioned(
            left: 4,
            bottom: 4,
            child: _DescriptionNavigationOverlayButton(
              buttonKey: const Key('description_nav_back'),
              canNavigate: canNavigate,
              forward: false,
              onTap: onNavigateBackward,
            ),
          ),
          Positioned(
            right: 4,
            bottom: 4,
            child: _DescriptionNavigationOverlayButton(
              buttonKey: const Key('description_nav_forward'),
              canNavigate: canNavigate,
              forward: true,
              onTap: onNavigateForward,
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
}

class _DescriptionNavigationOverlayButton extends StatelessWidget {
  final Key? buttonKey;
  final bool canNavigate;
  final bool forward;
  final VoidCallback onTap;

  const _DescriptionNavigationOverlayButton({
    this.buttonKey,
    required this.canNavigate,
    required this.forward,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final Color bgColor = colorScheme.surface.withValues(
      alpha: canNavigate ? 0.08 : 0.04,
    );
    final Color iconColor = colorScheme.primary.withValues(
      alpha: canNavigate ? 0.35 : 0.18,
    );

    return IgnorePointer(
      ignoring: !canNavigate,
      child: Material(
        type: MaterialType.transparency,
        child: InkResponse(
          radius: 28,
          highlightShape: BoxShape.circle,
          onTap: onTap,
          child: Container(
            key: buttonKey,
            width: 54,
            height: 54,
            decoration: BoxDecoration(color: bgColor, shape: BoxShape.circle),
            alignment: Alignment.center,
            child: Icon(
              forward
                  ? Icons.arrow_forward_ios_rounded
                  : Icons.arrow_back_ios_new_rounded,
              size: 22,
              color: iconColor,
            ),
          ),
        ),
      ),
    );
  }
}
