import 'package:flutter/material.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';

class BrightnessContrastDialog extends StatefulWidget {
  final Function(double, double) onApply;
  final Function() onCancel;
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
  BrightnessContrastDialogState createState() =>
      BrightnessContrastDialogState();
}

class BrightnessContrastDialogState extends State<BrightnessContrastDialog> {
  final aud = AudioController();
  double brightness = 0;
  double contrast = 100;

  @override
  void initState() {
    super.initState();
    brightness = widget.brightness;
    contrast = widget.contrast;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return AlertDialog(
      backgroundColor: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
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
              setState(() {
                brightness = value;
              });
            },
            onChangeEnd: (value) {
              aud.playSound("click");
              setState(() {
                brightness = value;
              });
              widget.onApply(brightness, contrast);
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
              setState(() {
                contrast = value;
              });
            },
            onChangeEnd: (value) {
              setState(() {
                contrast = value;
              });
              widget.onApply(brightness, contrast);
            },
          ),
        ],
      ),
      actions: [
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: colorScheme.primary,
          ),
          onPressed: () {
            aud.playSound("click");
            widget.onCancel();
            Navigator.of(context).pop();
          },
          child: Text(
            AppLocalizations.of(context)!.reset,
            style: TextStyle(color: colorScheme.primary),
          ),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: colorScheme.primary,
          ),
          onPressed: () {
            aud.playSound("click");
            Navigator.of(context).pop();
          },
          child: Text(
            AppLocalizations.of(context)!.ok,
            style: TextStyle(color: colorScheme.primary),
          ),
        ),
      ],
    );
  }
}
