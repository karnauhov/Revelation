import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart' show RenderPositionedBox;
import 'package:flutter_bloc/flutter_bloc.dart';

/// The compact reading surface shared by passages and dictionary entries.
class StudyTextDialog extends StatelessWidget {
  const StudyTextDialog({
    required this.title,
    this.subtitle,
    required this.content,
    required this.actions,
    this.titleInfo,
    this.maxWidth = 660,
    this.moveByHeader = false,
    super.key,
  });

  final String title;
  final String? subtitle;
  final Widget content;
  final List<Widget> actions;
  final Widget? titleInfo;
  final double maxWidth;
  final bool moveByHeader;

  @override
  Widget build(BuildContext context) {
    if (!moveByHeader) return _buildDialog(context);
    return BlocProvider(
      create: (_) => _StudyDialogPositionCubit(),
      child: BlocBuilder<_StudyDialogPositionCubit, Alignment>(
        builder: (context, alignment) => _buildDialog(context, alignment),
      ),
    );
  }

  Widget _buildDialog(BuildContext context, [Alignment? alignment]) {
    final theme = Theme.of(context);
    const titlePadding = EdgeInsets.fromLTRB(16, 12, 16, 8);
    final heading = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Flexible(
              child: Text(
                title,
                textAlign: TextAlign.center,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (titleInfo != null)
              Transform.translate(
                offset: const Offset(4, -5),
                child: titleInfo,
              ),
          ],
        ),
        if (subtitle != null)
          Text(
            subtitle!,
            style: theme.textTheme.labelSmall,
            textAlign: TextAlign.center,
          ),
      ],
    );

    return AlertDialog(
      alignment: alignment,
      constraints: BoxConstraints(maxWidth: maxWidth),
      insetPadding: const EdgeInsets.all(10),
      backgroundColor: theme.colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      titlePadding: alignment == null ? titlePadding : EdgeInsets.zero,
      contentPadding: const EdgeInsets.symmetric(horizontal: 10),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
      title: alignment == null
          ? heading
          : _StudyDialogDragHeader(
              child: Padding(padding: titlePadding, child: heading),
            ),
      content: content,
      actions: actions,
    );
  }
}

class _StudyDialogDragHeader extends StatelessWidget {
  const _StudyDialogDragHeader({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => MouseRegion(
    cursor: SystemMouseCursors.move,
    child: GestureDetector(
      behavior: HitTestBehavior.opaque,
      onPanUpdate: (details) {
        final viewport = context
            .findAncestorRenderObjectOfType<RenderPositionedBox>();
        final surface = viewport?.child;
        if (viewport == null ||
            !viewport.hasSize ||
            surface == null ||
            !surface.hasSize) {
          return;
        }
        context.read<_StudyDialogPositionCubit>().move(
          details.delta,
          Offset(
            viewport.size.width - surface.size.width,
            viewport.size.height - surface.size.height,
          ),
        );
      },
      child: child,
    ),
  );
}

class _StudyDialogPositionCubit extends Cubit<Alignment> {
  _StudyDialogPositionCubit() : super(Alignment.center);

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
