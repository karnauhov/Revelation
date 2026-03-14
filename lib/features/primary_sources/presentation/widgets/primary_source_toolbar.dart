import 'package:flutter/material.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/brightness_contrast_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar_overflow_menu.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_source_screen.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/replace_color_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_source_view_model.dart';

class PrimarySourceToolbar extends StatelessWidget {
  final PrimarySourceViewModel viewModel;
  final PrimarySource primarySource;
  final bool isBottom;
  final double dropdownWidth;
  final BuildContext screenContext;
  final aud = AudioController();

  PrimarySourceToolbar({
    required this.viewModel,
    required this.primarySource,
    required this.isBottom,
    required this.dropdownWidth,
    required this.screenContext,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    if (isBottom) {
      return LayoutBuilder(
        builder: (context, constraints) {
          final int calcButtons = _calcFitButtons(
            constraints.maxWidth - dropdownWidth,
          );
          final bool showFullActions =
              calcButtons >= PrimarySourceScreen.numButtons;
          return Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: showFullActions
                ? _buildFullActions(context)
                : _buildAdaptiveActions(context, calcButtons),
          );
        },
      );
    } else {
      return Row(children: _buildFullActions(context));
    }
  }

  int _calcFitButtons(double actionWidth) {
    const double buttonCellWidth = 40.0;
    const double startOffset = 80.0;
    final fit = ((actionWidth - startOffset) / buttonCellWidth).floor();
    return fit.clamp(0, PrimarySourceScreen.numButtons);
  }

  List<Widget> _buildFullActions(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return [
      DropdownButton<model.Page>(
        value: viewModel.selectedPage,
        hint: Text(
          primarySource.pages.isEmpty || !primarySource.permissionsReceived
              ? AppLocalizations.of(context)!.images_are_missing
              : "",
          style: TextStyle(color: colorScheme.onSurfaceVariant),
        ),
        onChanged: (model.Page? newPage) {
          aud.playSound("click");
          if (primarySource.permissionsReceived) {
            viewModel.changeSelectedPage(newPage);
            viewModel.showCommonInfo(context);
          }
        },
        items: primarySource.permissionsReceived
            ? primarySource.pages.map<DropdownMenuItem<model.Page>>((
                model.Page value,
              ) {
                return DropdownMenuItem<model.Page>(
                  value: value,
                  child: _buildDropdownItem(context, viewModel, value),
                );
              }).toList()
            : List.empty(),
        onTap: () {
          aud.playSound("click");
        },
      ),
      IconButton(
        icon: viewModel.refreshError
            ? Icon(Icons.sync_problem)
            : Icon(Icons.sync),
        color: viewModel.refreshError ? colorScheme.error : colorScheme.primary,
        tooltip: AppLocalizations.of(context)!.reload_image,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () {
                aud.playSound("click");
                viewModel.loadImage(
                  viewModel.selectedPage!.image,
                  isReload: true,
                );
              }
            : null,
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_in),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.zoom_in,
            onPressed: zoomStatus.canZoomIn
                ? () {
                    aud.playSound("click");
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    viewModel.imageController.zoomIn(viewportCenter);
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.zoom_out,
            onPressed: zoomStatus.canZoomOut
                ? () {
                    aud.playSound("click");
                    final viewportSize = Size(
                      MediaQuery.of(context).size.width,
                      MediaQuery.of(context).size.height,
                    );
                    final viewportCenter = Offset(
                      viewportSize.width / 2,
                      viewportSize.height / 2,
                    );
                    viewModel.imageController.zoomOut(
                      viewportCenter,
                      viewportSize,
                    );
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out_map),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.restore_original_scale,
            onPressed: zoomStatus.canReset
                ? () {
                    aud.playSound("click");
                    viewModel.imageController.backToMinScale();
                  }
                : null,
          );
        },
      ),
      IconButton(
        icon: const Icon(Icons.invert_colors),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: viewModel.isNegative
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_negative,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.toggleNegative();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.monochrome_photos),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: viewModel.isMonochrome
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_monochrome,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                !viewModel.primarySource.isMonochrome &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.toggleMonochrome();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.brightness_6),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor:
              viewModel.brightness != 0 || viewModel.contrast != 100
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.brightness_contrast,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                _showBrightnessContrastDialog();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.format_paint),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor:
              viewModel.selectedArea != null && viewModel.tolerance != 0
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.color_replacement,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                _showReplaceColorDialog();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.horizontal_distribute),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: viewModel.showWordSeparators
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_word_separators,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.toggleShowWordSeparators();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.local_offer),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: viewModel.showStrongNumbers
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_strong_numbers,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.toggleShowStrongNumbers();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.format_list_numbered),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: viewModel.showVerseNumbers
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_verse_numbers,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.toggleShowVerseNumbers();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.cleaning_services),
        color: colorScheme.primary,
        tooltip: AppLocalizations.of(context)!.page_settings_reset,
        onPressed:
            viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                viewModel.removePageSettings();
              }
            : null,
      ),
    ];
  }

  List<Widget> _buildAdaptiveActions(BuildContext context, int numButtons) {
    final allActions = _buildFullActions(context);
    final visibleActions = allActions.sublist(
      0,
      1 + (numButtons > 0 ? numButtons : 0),
    );
    final hasOverflow = numButtons < PrimarySourceScreen.numButtons;

    return [
      ...visibleActions,
      if (hasOverflow)
        PrimarySourceToolbarOverflowMenuButton(
          viewModel: viewModel,
          audioController: aud,
          numButtons: numButtons,
          onOpenBrightnessContrastDialog: _showBrightnessContrastDialog,
          onOpenReplaceColorDialog: _showReplaceColorDialog,
        ),
    ];
  }

  Widget _buildDropdownItem(
    BuildContext context,
    PrimarySourceViewModel viewModel,
    model.Page page,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final bool? loaded = viewModel.localPageLoaded[page.image];
    final Color textColor = loaded == null
        ? colorScheme.onSurfaceVariant
        : (loaded ? colorScheme.primary : colorScheme.error);

    final FontWeight weight = page == viewModel.selectedPage
        ? FontWeight.bold
        : FontWeight.normal;

    return Text.rich(
      TextSpan(
        style: TextStyle(color: textColor, fontWeight: weight),
        children: [
          TextSpan(text: page.name),
          TextSpan(
            text: ' (${page.content})',
            style: theme.textTheme.bodySmall!.copyWith(
              color: textColor,
              fontWeight: weight,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showBrightnessContrastDialog() {
    return showDialog(
      context: screenContext,
      routeSettings: RouteSettings(name: "brightness_contrast_dialog"),
      barrierColor: Colors.transparent,
      builder: (context) {
        return Stack(
          children: [
            Positioned(
              right: -60,
              top: 75,
              child: ConstrainedBox(
                constraints: const BoxConstraints(minWidth: 350, maxWidth: 500),
                child: BrightnessContrastDialog(
                  onApply: (brightness, contrast) {
                    viewModel.applyBrightnessContrast(brightness, contrast);
                  },
                  onCancel: () {
                    viewModel.resetBrightnessContrast();
                  },
                  brightness: viewModel.brightness,
                  contrast: viewModel.contrast,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Future<void> _showReplaceColorDialog() {
    return showDialog(
      context: screenContext,
      routeSettings: RouteSettings(name: "replace_color_dialog"),
      useRootNavigator: false,
      barrierColor: Colors.transparent,
      builder: (context) {
        return Stack(
          children: [
            Positioned(
              right: -35,
              top: 75,
              child: ConstrainedBox(
                constraints: const BoxConstraints(minWidth: 350, maxWidth: 450),
                child: ReplaceColorDialog(
                  viewModel: viewModel,
                  parentContext: screenContext,
                  onApply: (selectedArea, colorToReplace, newColor, tolerance) {
                    viewModel.applyColorReplacement(
                      selectedArea,
                      colorToReplace,
                      newColor,
                      tolerance,
                    );
                  },
                  onCancel: () {
                    viewModel.resetColorReplacement();
                  },
                  selectedArea: viewModel.selectedArea,
                  colorToReplace: viewModel.colorToReplace,
                  newColor: viewModel.newColor,
                  tolerance: viewModel.tolerance,
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
