import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart' show RenderPositionedBox;
import 'package:flutter_bloc/flutter_bloc.dart';

/// A footer command. RevelationDialog chooses its widget and colors.
class RevelationDialogAction {
  const RevelationDialogAction({
    required this.label,
    required this.onPressed,
    this.icon,
    this.key,
  }) : _isDestructive = false;

  /// Use for the primary action that finally confirms a destructive change.
  const RevelationDialogAction.destructive({
    required this.label,
    required this.onPressed,
    this.icon,
    this.key,
  }) : _isDestructive = true;

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final Key? key;
  final bool _isDestructive;
}

/// Shared surface for application-owned modal dialogs.
class RevelationDialog extends StatelessWidget {
  const RevelationDialog({
    required this.title,
    required this.content,
    this.secondaryActions = const [],
    this.primaryAction,
    this.constraints = const BoxConstraints(minWidth: 280, maxWidth: 660),
    this.initialAlignment = Alignment.center,
    this.insetPadding = const EdgeInsets.all(10),
    this.contentPadding = const EdgeInsets.symmetric(horizontal: 10),
    this.scrollContent = false,
    super.key,
  });

  final Widget title;
  final Widget content;
  final List<RevelationDialogAction> secondaryActions;

  /// The single main command, appended after the text actions.
  final RevelationDialogAction? primaryAction;
  final BoxConstraints constraints;
  final Alignment initialAlignment;
  final EdgeInsets insetPadding;
  final EdgeInsetsGeometry contentPadding;

  /// Wraps natural-height content in a viewport. Lists and other bodies that
  /// already scroll use the bounded space provided directly by the dialog.
  final bool scrollContent;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final actions = [
      for (final action in secondaryActions)
        TextButton.icon(
          key: action.key,
          onPressed: action.onPressed,
          icon: action.icon == null ? null : Icon(action.icon),
          label: Text(action.label, textAlign: TextAlign.center),
        ),
      if (primaryAction case final action?)
        FilledButton.icon(
          key: action.key,
          onPressed: action.onPressed,
          icon: action.icon == null ? null : Icon(action.icon),
          label: Text(action.label, textAlign: TextAlign.center),
          style: FilledButton.styleFrom(
            backgroundColor: action._isDestructive
                ? theme.colorScheme.error
                : theme.colorScheme.primary,
            foregroundColor: action._isDestructive
                ? theme.colorScheme.onError
                : theme.colorScheme.onPrimary,
            shape: const StadiumBorder(),
          ),
        ),
    ];
    return BlocProvider(
      create: (_) => _DialogPositionCubit(initialAlignment),
      child: BlocBuilder<_DialogPositionCubit, Alignment>(
        builder: (context, alignment) => AlertDialog(
          alignment: alignment,
          constraints: constraints,
          insetPadding: insetPadding,
          backgroundColor: theme.colorScheme.surface,
          shape: RoundedRectangleBorder(
            side: BorderSide(color: theme.colorScheme.primary),
            borderRadius: BorderRadius.circular(8),
          ),
          titlePadding: EdgeInsets.zero,
          titleTextStyle: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          title: _DialogDragHeader(child: title),
          contentPadding: contentPadding,
          content: scrollContent
              ? SingleChildScrollView(primary: false, child: content)
              : content,
          actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
          actionsOverflowDirection: VerticalDirection.down,
          actions: actions.isEmpty ? null : actions,
        ),
      ),
    );
  }
}

class _DialogDragHeader extends StatelessWidget {
  const _DialogDragHeader({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => MouseRegion(
    cursor: SystemMouseCursors.move,
    child: GestureDetector(
      behavior: HitTestBehavior.opaque,
      onPanUpdate: (details) {
        // Dialog's Align sits inside the safe area, keyboard and inset padding.
        final viewport = context
            .findAncestorRenderObjectOfType<RenderPositionedBox>();
        final surface = viewport?.child;
        if (viewport == null ||
            !viewport.hasSize ||
            surface == null ||
            !surface.hasSize) {
          return;
        }
        context.read<_DialogPositionCubit>().move(
          details.delta,
          Offset(
            viewport.size.width - surface.size.width,
            viewport.size.height - surface.size.height,
          ),
        );
      },
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
        child: DefaultTextStyle.merge(
          textAlign: TextAlign.center,
          child: child,
        ),
      ),
    ),
  );
}

class _DialogPositionCubit extends Cubit<Alignment> {
  _DialogPositionCubit(super.initialState);

  void move(Offset delta, Offset available) {
    emit(
      Alignment(
        _moveAxis(state.x, delta.dx, available.dx),
        _moveAxis(state.y, delta.dy, available.dy),
      ),
    );
  }

  double _moveAxis(double current, double delta, double available) =>
      available <= 0
      ? current
      : (current + 2 * delta / available).clamp(-1.0, 1.0);
}
