import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_tool_draft_cubits.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/manuscript_tool_dialog.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';

class BrightnessContrastDialog extends StatelessWidget {
  final void Function(double, double) onApply;
  final VoidCallback onCancel;

  final double brightness;
  final double contrast;

  const BrightnessContrastDialog({
    required this.onApply,
    required this.onCancel,

    this.brightness = 0,
    this.contrast = 100,
    super.key,
  });

  @override
  Widget build(BuildContext context) => BlocProvider(
    create: (_) => BrightnessDraftCubit(brightness, contrast),
    child: Builder(
      builder: (context) {
        final draft = context.watch<BrightnessDraftCubit>();
        final brightness = draft.state.brightness;
        final contrast = draft.state.contrast;
        final aud = AudioController();
        final colorScheme = Theme.of(context).colorScheme;
        return ManuscriptToolDialog(
          title: Text(AppLocalizations.of(context)!.brightness_contrast),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${AppLocalizations.of(context)!.brightness}: ${brightness.toStringAsFixed(0)}',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Slider(
                value: brightness,
                min: -100,
                max: 100,
                activeColor: colorScheme.primary,
                inactiveColor: colorScheme.onSurface.withValues(alpha: 0.3),
                onChanged: (value) {
                  draft.setBrightness(value);
                },
                onChangeEnd: (value) {
                  aud.playSound("click");
                  draft.setBrightness(value);
                  onApply(draft.state.brightness, draft.state.contrast);
                },
              ),
              const SizedBox(height: 20),
              Text(
                '${AppLocalizations.of(context)!.contrast}: ${contrast.toStringAsFixed(0)}',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Slider(
                value: contrast,
                min: 0,
                max: 200,
                activeColor: colorScheme.primary,
                inactiveColor: colorScheme.onSurface.withValues(alpha: 0.3),
                onChanged: (value) {
                  aud.playSound("click");
                  draft.setContrast(value);
                },
                onChangeEnd: (value) {
                  draft.setContrast(value);
                  onApply(draft.state.brightness, draft.state.contrast);
                },
              ),
            ],
          ),
          secondaryActions: [
            RevelationDialogAction(
              label: AppLocalizations.of(context)!.reset,
              onPressed: () {
                aud.playSound("click");
                onCancel();
                Navigator.of(context).pop();
              },
            ),
            RevelationDialogAction(
              label: AppLocalizations.of(context)!.dialog_done,
              onPressed: () {
                aud.playSound("click");
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    ),
  );
}
