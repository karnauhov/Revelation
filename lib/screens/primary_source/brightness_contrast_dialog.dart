import 'package:flutter/material.dart';
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
    return AlertDialog(
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${AppLocalizations.of(context)!.brightness}: ${brightness.toStringAsFixed(0)}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Slider(
            value: brightness,
            min: -100,
            max: 100,
            onChanged: (value) {
              setState(() {
                brightness = value;
              });
            },
            onChangeEnd: (value) {
              setState(() {
                brightness = value;
              });
              widget.onApply(brightness, contrast);
            },
          ),
          const SizedBox(height: 20),
          Text(
            '${AppLocalizations.of(context)!.contrast}: ${contrast.toStringAsFixed(0)}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Slider(
            value: contrast,
            min: 0,
            max: 200,
            onChanged: (value) {
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
          onPressed: () {
            widget.onCancel();
            Navigator.of(context).pop();
          },
          child: Text(AppLocalizations.of(context)!.reset),
        ),
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: Text(AppLocalizations.of(context)!.ok),
        ),
      ],
    );
  }
}
