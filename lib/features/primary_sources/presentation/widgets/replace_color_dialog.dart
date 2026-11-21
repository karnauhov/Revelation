import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_tool_draft_cubits.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/manuscript_tool_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';

class ReplaceColorDialog extends StatelessWidget {
  final BuildContext parentContext;

  final void Function(Rect?, Color, Color, double) onApply;
  final VoidCallback onCancel;
  final void Function(void Function(Rect?)) onStartSelectAreaMode;
  final void Function(void Function(Color?), bool isColorToReplace)
  onStartPipetteMode;
  final Rect? Function() readSelectedArea;
  final Color Function() readColorToReplace;
  final Color Function() readNewColor;
  final double Function() readTolerance;
  final Rect? selectedArea;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;

  const ReplaceColorDialog({
    required this.parentContext,

    required this.onApply,
    required this.onCancel,
    required this.onStartSelectAreaMode,
    required this.onStartPipetteMode,
    required this.readSelectedArea,
    required this.readColorToReplace,
    required this.readNewColor,
    required this.readTolerance,
    this.selectedArea,
    this.colorToReplace = const Color(0xFFFFFFFF),
    this.newColor = const Color(0xFFFFFFFF),
    this.tolerance = 0.0,
    super.key,
  });

  @override
  Widget build(BuildContext context) => BlocProvider(
    create: (_) => ReplacementDraftCubit(colorToReplace, newColor, tolerance),
    child: Builder(
      builder: (context) {
        final draft = context.watch<ReplacementDraftCubit>();
        final colorToReplace = draft.state.from;
        final newColor = draft.state.to;
        final tolerance = draft.state.tolerance;
        final colorScheme = Theme.of(context).colorScheme;
        final aud = AudioController();
        final currentSelectedArea = readSelectedArea();
        final areaSizeText = currentSelectedArea == null
            ? AppLocalizations.of(context)!.not_selected
            : '${AppLocalizations.of(context)!.size} (${(currentSelectedArea.right - currentSelectedArea.left).abs().toStringAsFixed(0)} x ${(currentSelectedArea.bottom - currentSelectedArea.top).abs().toStringAsFixed(0)})';

        return ManuscriptToolDialog(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '${AppLocalizations.of(context)!.area}:',
                      style: TextStyle(
                        color: colorScheme.onSurface,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      areaSizeText,
                      style: TextStyle(color: colorScheme.onSurface),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.crop),
                    color: colorScheme.primary,
                    tooltip: AppLocalizations.of(context)!.area_selection,
                    onPressed: () {
                      aud.playSound('click');
                      Navigator.of(context).pop();
                      onStartSelectAreaMode((_) {
                        _reopenDialog();
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '${AppLocalizations.of(context)!.color_to_replace}:',
                      style: TextStyle(
                        color: colorScheme.onSurface,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: colorToReplace,
                      border: Border.all(color: colorScheme.outline),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.palette),
                    color: colorScheme.primary,
                    tooltip: AppLocalizations.of(context)!.palette,
                    onPressed: () =>
                        _pickColor(context, draft, replaceFrom: true),
                  ),
                  IconButton(
                    icon: Icon(Icons.colorize),
                    color: colorScheme.primary,
                    tooltip: AppLocalizations.of(context)!.eyedropper,
                    onPressed: () {
                      aud.playSound('click');
                      Navigator.of(context).pop();
                      onStartPipetteMode((_) {
                        _reopenDialog();
                      }, true);
                    },
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '${AppLocalizations.of(context)!.new_color}:',
                      style: TextStyle(
                        color: colorScheme.onSurface,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: newColor,
                      border: Border.all(color: colorScheme.outline),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.palette),
                    color: colorScheme.primary,
                    tooltip: AppLocalizations.of(context)!.palette,
                    onPressed: () =>
                        _pickColor(context, draft, replaceFrom: false),
                  ),
                  IconButton(
                    icon: Icon(Icons.colorize),
                    color: colorScheme.primary,
                    tooltip: AppLocalizations.of(context)!.eyedropper,
                    onPressed: () {
                      aud.playSound('click');
                      Navigator.of(context).pop();
                      onStartPipetteMode((_) {
                        _reopenDialog();
                      }, false);
                    },
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      '${AppLocalizations.of(context)!.tolerance}: ${tolerance.toStringAsFixed(0)}',
                      style: TextStyle(
                        color: colorScheme.onSurface,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Slider(
                      value: tolerance,
                      min: 0,
                      max: 100,
                      divisions: 100,
                      activeColor: colorScheme.primary,
                      inactiveColor: colorScheme.onSurface.withValues(
                        alpha: 0.3,
                      ),
                      onChanged: (value) {
                        aud.playSound('click');
                        draft.setTolerance(value);
                      },
                      onChangeEnd: (value) {
                        onApply(selectedArea, colorToReplace, newColor, value);
                      },
                    ),
                  ),
                ],
              ),
              if (isWeb())
                Text(
                  AppLocalizations.of(context)!.replace_color_message,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
            ],
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(foregroundColor: colorScheme.primary),
              onPressed: () {
                aud.playSound('click');
                onCancel();
                Navigator.of(context).pop();
              },
              child: Text(
                AppLocalizations.of(context)!.reset,
                style: TextStyle(color: colorScheme.primary),
              ),
            ),
            TextButton(
              style: TextButton.styleFrom(foregroundColor: colorScheme.primary),
              onPressed: () {
                aud.playSound('click');
                onApply(selectedArea, colorToReplace, newColor, tolerance);
                Navigator.of(context).pop();
              },
              child: Text(
                AppLocalizations.of(context)!.ok,
                style: TextStyle(color: colorScheme.primary),
              ),
            ),
          ],
        );
      },
    ),
  );

  Future<void> _pickColor(
    BuildContext context,
    ReplacementDraftCubit draft, {
    required bool replaceFrom,
  }) async {
    final audio = AudioController();
    audio.playSound('click');
    var picked = replaceFrom ? draft.state.from : draft.state.to;
    final choice = await showDialog<Color>(
      context: context,
      barrierColor: Colors.transparent,
      routeSettings: const RouteSettings(name: 'palette_dialog'),
      builder: (ctx) {
        final l10n = AppLocalizations.of(ctx)!;
        return ManuscriptToolDialog(
          title: Text(l10n.select_color),
          content: ColorPicker(
            portraitOnly: true,
            pickerColor: picked,
            onColorChanged: (value) => picked = value,
            pickerAreaHeightPercent: 0.8,
          ),
          actions: [
            TextButton(
              onPressed: () {
                audio.playSound('click');
                Navigator.pop(ctx);
              },
              child: Text(l10n.cancel),
            ),
            TextButton(
              onPressed: () {
                audio.playSound('click');
                Navigator.pop(ctx, picked);
              },
              child: Text(l10n.ok),
            ),
          ],
        );
      },
    );
    if (!context.mounted || choice == null || draft.isClosed) return;
    draft.setColor(choice, replaceFrom: replaceFrom);
    onApply(
      selectedArea,
      draft.state.from,
      draft.state.to,
      draft.state.tolerance,
    );
  }

  Future<void> _reopenDialog() async {
    if (!parentContext.mounted) return;
    await showDialog<void>(
      context: parentContext,
      routeSettings: const RouteSettings(name: 'replace_color_dialog'),
      useRootNavigator: false,
      barrierColor: Colors.transparent,
      builder: (_) => ReplaceColorDialog(
        parentContext: parentContext,

        onApply: onApply,
        onCancel: onCancel,
        onStartSelectAreaMode: onStartSelectAreaMode,
        onStartPipetteMode: onStartPipetteMode,
        readSelectedArea: readSelectedArea,
        readColorToReplace: readColorToReplace,
        readNewColor: readNewColor,
        readTolerance: readTolerance,
        selectedArea: readSelectedArea(),
        colorToReplace: readColorToReplace(),
        newColor: readNewColor(),
        tolerance: readTolerance(),
      ),
    );
  }
}
