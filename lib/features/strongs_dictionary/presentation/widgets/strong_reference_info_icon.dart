import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';

class StrongReferenceInfoIcon extends StatelessWidget {
  const StrongReferenceInfoIcon({required this.tooltipKey, super.key});

  final GlobalKey<TooltipState> tooltipKey;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final tooltipMaxWidth = screenWidth > 432 ? 420.0 : screenWidth - 12.0;

    return Tooltip(
      key: tooltipKey,
      message: localizations.strong_reference_commentary,
      constraints: BoxConstraints(maxWidth: tooltipMaxWidth),
      showDuration: const Duration(seconds: 12),
      preferBelow: false,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          tooltipKey.currentState?.ensureTooltipVisible();
        },
        child: SizedBox(
          key: const Key('strong_reference_info_icon'),
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
    );
  }
}
