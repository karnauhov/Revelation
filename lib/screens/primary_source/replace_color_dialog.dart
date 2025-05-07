import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';

class ReplaceColorDialog extends StatefulWidget {
  final PrimarySourceViewModel viewModel;
  final BuildContext parentContext;
  final Function(Color, Color, double) onApply;
  final Function() onCancel;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;

  const ReplaceColorDialog({
    required this.viewModel,
    required this.parentContext,
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
                  Navigator.of(context).pop();
                  widget.viewModel.startPipetteMode((pickedColor) {
                    log.d("PickedColor: $pickedColor");
                    showDialog(
                      context: widget.parentContext,
                      useRootNavigator: false,
                      barrierColor: Colors.transparent,
                      builder: (context) {
                        return Stack(
                          children: [
                            Positioned(
                              right: -35,
                              top: 75,
                              child: ConstrainedBox(
                                constraints: const BoxConstraints(
                                    minWidth: 350, maxWidth: 450),
                                child: ReplaceColorDialog(
                                  viewModel: widget.viewModel,
                                  parentContext: widget.parentContext,
                                  onApply:
                                      (colorToReplace, newColor, tolerance) {
                                    widget.viewModel.applyColorReplacement(
                                        colorToReplace, newColor, tolerance);
                                  },
                                  onCancel: () {
                                    widget.viewModel.resetColorReplacement();
                                  },
                                  colorToReplace:
                                      widget.viewModel.colorToReplace,
                                  newColor: widget.viewModel.newColor,
                                  tolerance: widget.viewModel.tolerance,
                                ),
                              ),
                            ),
                          ],
                        );
                      },
                    );
                  });
                },
              )
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
                  Color picked = newColor;
                  await showDialog(
                    context: context,
                    builder: (context) {
                      return AlertDialog(
                        title: Text(AppLocalizations.of(context)!.select_color),
                        content: SingleChildScrollView(
                          child: ColorPicker(
                            pickerColor: picked,
                            onColorChanged: (color) {
                              picked = color;
                            },
                            pickerAreaHeightPercent: 0.8,
                          ),
                        ),
                        actions: [
                          TextButton(
                            child: Text(AppLocalizations.of(context)!.cancel),
                            onPressed: () => Navigator.of(context).pop(),
                          ),
                          TextButton(
                            child: Text(AppLocalizations.of(context)!.ok),
                            onPressed: () {
                              Navigator.of(context).pop();
                              setState(() {
                                newColor = picked;
                              });
                              widget.onApply(
                                  colorToReplace, newColor, tolerance);
                            },
                          ),
                        ],
                      );
                    },
                  );
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
