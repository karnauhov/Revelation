import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class PlatformExpansionTile extends StatelessWidget {
  const PlatformExpansionTile({
    super.key,
    required this.title,
    required this.children,
    this.initiallyExpanded = false,
    this.onExpansionChanged,
    this.tilePadding,
    this.minTileHeight,
  });

  final Widget title;
  final List<Widget> children;
  final bool initiallyExpanded;
  final ValueChanged<bool>? onExpansionChanged;
  final EdgeInsetsGeometry? tilePadding;
  final double? minTileHeight;

  bool get _useWindowsReplacement =>
      !kIsWeb && defaultTargetPlatform == TargetPlatform.windows;

  @override
  Widget build(BuildContext context) {
    if (!_useWindowsReplacement) {
      return ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        onExpansionChanged: onExpansionChanged,
        tilePadding: tilePadding,
        minTileHeight: minTileHeight,
        title: title,
        children: children,
      );
    }

    return _WindowsExpansionTile(
      title: title,
      initiallyExpanded: initiallyExpanded,
      onExpansionChanged: onExpansionChanged,
      tilePadding: tilePadding,
      minTileHeight: minTileHeight,
      children: children,
    );
  }
}

class _WindowsExpansionTile extends StatefulWidget {
  const _WindowsExpansionTile({
    required this.title,
    required this.children,
    required this.initiallyExpanded,
    this.onExpansionChanged,
    this.tilePadding,
    this.minTileHeight,
  });

  final Widget title;
  final List<Widget> children;
  final bool initiallyExpanded;
  final ValueChanged<bool>? onExpansionChanged;
  final EdgeInsetsGeometry? tilePadding;
  final double? minTileHeight;

  @override
  State<_WindowsExpansionTile> createState() => _WindowsExpansionTileState();
}

class _WindowsExpansionTileState extends State<_WindowsExpansionTile> {
  late bool _isExpanded = widget.initiallyExpanded;

  @override
  void didUpdateWidget(covariant _WindowsExpansionTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initiallyExpanded != widget.initiallyExpanded) {
      _isExpanded = widget.initiallyExpanded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final expansionTheme = ExpansionTileTheme.of(context);
    final duration =
        expansionTheme.expansionAnimationStyle?.duration ??
        const Duration(milliseconds: 200);
    final curve =
        expansionTheme.expansionAnimationStyle?.curve ?? Curves.easeInOut;
    final iconColor = _isExpanded
        ? expansionTheme.iconColor ?? colorScheme.primary
        : expansionTheme.collapsedIconColor ??
              (theme.useMaterial3
                  ? colorScheme.onSurface
                  : theme.unselectedWidgetColor);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        ListTile(
          minTileHeight: widget.minTileHeight,
          contentPadding:
              widget.tilePadding ??
              expansionTheme.tilePadding ??
              const EdgeInsets.symmetric(horizontal: 16),
          title: widget.title,
          trailing: AnimatedRotation(
            turns: _isExpanded ? 0.5 : 0.0,
            duration: duration,
            curve: curve,
            child: Icon(Icons.expand_more, color: iconColor),
          ),
          onTap: _toggleExpanded,
        ),
        ClipRect(
          child: AnimatedSize(
            duration: duration,
            curve: curve,
            alignment: Alignment.topCenter,
            child: _isExpanded
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    children: widget.children,
                  )
                : const SizedBox.shrink(),
          ),
        ),
      ],
    );
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });
    widget.onExpansionChanged?.call(_isExpanded);
  }
}
