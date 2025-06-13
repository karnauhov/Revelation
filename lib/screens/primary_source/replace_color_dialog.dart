import 'package:flutter/material.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';

class ReplaceColorDialog extends StatefulWidget {
  final PrimarySourceViewModel viewModel;
  final BuildContext parentContext;
  final Function(Rect?, Color, Color, double) onApply;
  final Function() onCancel;
  final Rect? selectedArea;
  final Color colorToReplace;
  final Color newColor;
  final double tolerance;

  const ReplaceColorDialog({
    required this.viewModel,
    required this.parentContext,
    required this.onApply,
    required this.onCancel,
    this.selectedArea,
    this.colorToReplace = const Color(0xFFFFFFFF),
    this.newColor = const Color(0xFFFFFFFF),
    this.tolerance = 0.0,
    super.key,
  });

  @override
  ReplaceColorDialogState createState() => ReplaceColorDialogState();
}

class ReplaceColorDialogState extends State<ReplaceColorDialog> {
  final aud = AudioController();
  late Rect? selectedArea;
  late Color colorToReplace;
  late Color newColor;
  late double tolerance;

  @override
  void initState() {
    super.initState();
    selectedArea = widget.selectedArea;
    colorToReplace = widget.colorToReplace;
    newColor = widget.newColor;
    tolerance = widget.tolerance;
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
                  widget.viewModel.selectedArea == null
                      ? AppLocalizations.of(context)!.not_selected
                      : '${AppLocalizations.of(context)!.size} (${(widget.viewModel.selectedArea!.right - widget.viewModel.selectedArea!.left).abs().toStringAsFixed(0)} x ${(widget.viewModel.selectedArea!.bottom - widget.viewModel.selectedArea!.top).abs().toStringAsFixed(0)})',
                  style: TextStyle(
                    color: colorScheme.onSurface,
                  ),
                ),
              ),
              IconButton(
                icon: Icon(
                  Icons.crop,
                ),
                color: colorScheme.primary,
                tooltip: AppLocalizations.of(context)!.area_selection,
                onPressed: () async {
                  aud.playSound("click");
                  Navigator.of(context).pop();
                  widget.viewModel.startSelectAreaMode((onSelected) {
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
                                  onApply: (selectedArea, colorToReplace,
                                      newColor, tolerance) {
                                    widget.viewModel.applyColorReplacement(
                                        selectedArea,
                                        colorToReplace,
                                        newColor,
                                        tolerance);
                                  },
                                  onCancel: () {
                                    widget.viewModel.resetColorReplacement();
                                  },
                                  selectedArea: widget.viewModel.selectedArea,
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
                  border: Border.all(
                    color: colorScheme.outline,
                  ),
                ),
              ),
              IconButton(
                icon: Icon(
                  Icons.palette,
                ),
                color: colorScheme.primary,
                tooltip: AppLocalizations.of(context)!.palette,
                onPressed: () async {
                  aud.playSound("click");
                  Color picked = colorToReplace;
                  await showDialog(
                    context: context,
                    builder: (context) {
                      return AlertDialog(
                        backgroundColor: colorScheme.surface,
                        title: Text(
                          AppLocalizations.of(context)!.select_color,
                          style: TextStyle(color: colorScheme.onSurface),
                        ),
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
                              style: TextButton.styleFrom(
                                foregroundColor: colorScheme.primary,
                              ),
                              child: Text(
                                AppLocalizations.of(context)!.cancel,
                                style: TextStyle(color: colorScheme.primary),
                              ),
                              onPressed: () {
                                aud.playSound("click");
                                Navigator.of(context).pop();
                              }),
                          TextButton(
                            style: TextButton.styleFrom(
                              foregroundColor: colorScheme.primary,
                            ),
                            child: Text(
                              AppLocalizations.of(context)!.ok,
                              style: TextStyle(color: colorScheme.primary),
                            ),
                            onPressed: () {
                              aud.playSound("click");
                              Navigator.of(context).pop();
                              setState(() {
                                colorToReplace = picked;
                              });
                              widget.onApply(selectedArea, colorToReplace,
                                  newColor, tolerance);
                            },
                          ),
                        ],
                      );
                    },
                  );
                },
              ),
              IconButton(
                icon: Icon(
                  Icons.colorize,
                ),
                color: colorScheme.primary,
                tooltip: AppLocalizations.of(context)!.eyedropper,
                onPressed: () {
                  aud.playSound("click");
                  Navigator.of(context).pop();
                  widget.viewModel.startPipetteMode((pickedColor) {
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
                                  onApply: (selectedArea, colorToReplace,
                                      newColor, tolerance) {
                                    widget.viewModel.applyColorReplacement(
                                        selectedArea,
                                        colorToReplace,
                                        newColor,
                                        tolerance);
                                  },
                                  onCancel: () {
                                    widget.viewModel.resetColorReplacement();
                                  },
                                  selectedArea: widget.viewModel.selectedArea,
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
                  }, true);
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
                  border: Border.all(
                    color: colorScheme.outline,
                  ),
                ),
              ),
              IconButton(
                icon: Icon(
                  Icons.palette,
                ),
                color: colorScheme.primary,
                tooltip: AppLocalizations.of(context)!.palette,
                onPressed: () async {
                  aud.playSound("click");
                  Color picked = newColor;
                  await showDialog(
                    context: context,
                    builder: (context) {
                      return AlertDialog(
                        backgroundColor: colorScheme.surface,
                        title: Text(
                          AppLocalizations.of(context)!.select_color,
                          style: TextStyle(color: colorScheme.onSurface),
                        ),
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
                              style: TextButton.styleFrom(
                                foregroundColor: colorScheme.primary,
                              ),
                              child: Text(
                                AppLocalizations.of(context)!.cancel,
                                style: TextStyle(color: colorScheme.primary),
                              ),
                              onPressed: () {
                                aud.playSound("click");
                                Navigator.of(context).pop();
                              }),
                          TextButton(
                            style: TextButton.styleFrom(
                              foregroundColor: colorScheme.primary,
                            ),
                            child: Text(
                              AppLocalizations.of(context)!.ok,
                              style: TextStyle(color: colorScheme.primary),
                            ),
                            onPressed: () {
                              aud.playSound("click");
                              Navigator.of(context).pop();
                              setState(() {
                                newColor = picked;
                              });
                              widget.onApply(selectedArea, colorToReplace,
                                  newColor, tolerance);
                            },
                          ),
                        ],
                      );
                    },
                  );
                },
              ),
              IconButton(
                icon: Icon(
                  Icons.colorize,
                ),
                color: colorScheme.primary,
                tooltip: AppLocalizations.of(context)!.eyedropper,
                onPressed: () {
                  aud.playSound("click");
                  Navigator.of(context).pop();
                  widget.viewModel.startPipetteMode((pickedColor) {
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
                                  onApply: (selectedArea, colorToReplace,
                                      newColor, tolerance) {
                                    widget.viewModel.applyColorReplacement(
                                        selectedArea,
                                        colorToReplace,
                                        newColor,
                                        tolerance);
                                  },
                                  onCancel: () {
                                    widget.viewModel.resetColorReplacement();
                                  },
                                  selectedArea: widget.viewModel.selectedArea,
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
                  }, false);
                },
              )
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
                  inactiveColor: colorScheme.onSurface.withValues(alpha: 0.3),
                  onChanged: (value) {
                    aud.playSound("click");
                    setState(() {
                      tolerance = value;
                    });
                  },
                  onChangeEnd: (value) {
                    widget.onApply(
                        selectedArea, colorToReplace, newColor, tolerance);
                  },
                ),
              ),
            ],
          ),
          if (isWeb())
            Row(
              mainAxisSize: MainAxisSize.max,
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 280),
                  child: Text.rich(
                    textAlign: TextAlign.center,
                    TextSpan(
                      text:
                          "⚠️ ${AppLocalizations.of(context)!.replace_color_message}",
                      style: TextStyle(
                        fontSize: 10,
                        color: colorScheme.onSurface,
                      ),
                    ),
                    maxLines: 3,
                    softWrap: true,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
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
            widget.onApply(selectedArea, colorToReplace, newColor, tolerance);
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
