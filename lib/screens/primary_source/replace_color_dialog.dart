import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';

class ReplaceColorDialog extends StatefulWidget {
  final Function(Color, Color, double) onApply;
  final Function() onCancel;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;

  const ReplaceColorDialog({
    required this.onApply,
    required this.onCancel,
    this.colorToReplace = const Color(0xFFFFFFFF),
    this.newColor = const Color(0xFFFFFFFF),
    this.tolerance = 1.0,
    super.key,
  });

  @override
  ReplaceColorDialogState createState() => ReplaceColorDialogState();
}

class ReplaceColorDialogState extends State<ReplaceColorDialog> {
  late Color colorToReplace;
  late Color newColor;
  late double tolerance;

  @override
  void initState() {
    super.initState();
    colorToReplace = widget.colorToReplace;
    newColor = widget.newColor;
    tolerance = widget.tolerance;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '${AppLocalizations.of(context)!.color_to_replace}:',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: colorToReplace,
                  border: Border.all(color: Colors.black26),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.colorize),
                tooltip: AppLocalizations.of(context)!.eyedropper,
                onPressed: () {
                  // TODO: implement pipette picker
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
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: newColor,
                  border: Border.all(color: Colors.black26),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.palette),
                tooltip: AppLocalizations.of(context)!.palette,
                onPressed: () async {
                  // TODO: implement color picker dialog
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
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                flex: 2,
                child: Slider(
                  value: tolerance,
                  min: 0,
                  max: 100,
                  divisions: 100,
                  label: tolerance.toStringAsFixed(0),
                  onChanged: (value) {
                    setState(() {
                      tolerance = value;
                    });
                  },
                  onChangeEnd: (value) {
                    widget.onApply(colorToReplace, newColor, tolerance);
                  },
                ),
              ),
            ],
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
            widget.onApply(colorToReplace, newColor, tolerance);
            Navigator.of(context).pop();
          },
          child: Text(AppLocalizations.of(context)!.ok),
        ),
      ],
    );
  }
}
