import 'package:flutter/material.dart';
import 'package:revelation/controllers/audio_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/screens/primary_source/brightness_contrast_dialog.dart';
import 'package:revelation/screens/primary_source/primary_source_screen.dart';
import 'package:revelation/screens/primary_source/replace_color_dialog.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';

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
          final int calcButtons =
              _calcFitButtons(constraints.maxWidth - dropdownWidth);
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
      return Row(
        children: _buildFullActions(context),
      );
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
          }
        },
        items: primarySource.permissionsReceived
            ? primarySource.pages
                .map<DropdownMenuItem<model.Page>>((model.Page value) {
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
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () {
                aud.playSound("click");
                viewModel.loadImage(viewModel.selectedPage!.image,
                    isReload: true);
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
                    viewModel.imageController
                        .zoomOut(viewportCenter, viewportSize);
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
        onPressed: viewModel.primarySource.permissionsReceived &&
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
        onPressed: viewModel.primarySource.permissionsReceived &&
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
        onPressed: viewModel.primarySource.permissionsReceived &&
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
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                viewModel.localPageLoaded[viewModel.selectedPage!.image] == true
            ? () {
                aud.playSound("click");
                _showReplaceColorDialog();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.cleaning_services),
        color: colorScheme.primary,
        tooltip: AppLocalizations.of(context)!.page_settings_reset,
        onPressed: viewModel.primarySource.permissionsReceived &&
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
    final visibleActions =
        allActions.sublist(0, 1 + (numButtons > 0 ? numButtons : 0));
    final overflowActions = numButtons < PrimarySourceScreen.numButtons
        ? allActions.sublist(1 + numButtons)
        : [];

    return [
      ...visibleActions,
      if (overflowActions.isNotEmpty)
        ValueListenableBuilder<ZoomStatus>(
          valueListenable: viewModel.zoomStatusNotifier,
          builder: (context, zoomStatus, child) {
            final GlobalKey menuKey = GlobalKey();
            final theme = Theme.of(context);
            final colorScheme = theme.colorScheme;
            return IconButton(
              key: menuKey,
              icon: const Icon(Icons.more_vert),
              color: colorScheme.primary,
              tooltip: AppLocalizations.of(context)!.menu,
              onPressed: () async {
                aud.playSound("click");
                final RenderBox button =
                    menuKey.currentContext!.findRenderObject() as RenderBox;
                final RenderBox overlay =
                    Overlay.of(context).context.findRenderObject() as RenderBox;
                final RelativeRect position = RelativeRect.fromRect(
                  Rect.fromPoints(
                    button.localToGlobal(Offset.zero, ancestor: overlay),
                    button.localToGlobal(button.size.bottomRight(Offset.zero),
                        ancestor: overlay),
                  ),
                  Offset.zero & overlay.size,
                );

                // Pre-calculate viewport size and center
                final viewportSize = MediaQuery.of(context).size;
                final viewportCenter = Offset(
                  viewportSize.width / 2,
                  viewportSize.height / 2,
                );

                viewModel.setMenuOpen(true);

                final selectedValue = await showMenu<String>(
                  context: context,
                  position: position,
                  items: [
                    if (numButtons < 1)
                      PopupMenuItem(
                        value: 'refresh',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                viewModel.refreshError
                                    ? Icon(Icons.sync_problem,
                                        color: isEnabled
                                            ? colorScheme.error
                                            : colorScheme.onSurface
                                                .withValues(alpha: 0.38))
                                    : Icon(Icons.sync, color: iconColor),
                                const SizedBox(width: 8),
                                Text(
                                    AppLocalizations.of(context)!.reload_image),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 2)
                      PopupMenuItem(
                        value: 'zoom_in',
                        enabled: zoomStatus.canZoomIn,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = zoomStatus.canZoomIn;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                Icon(Icons.zoom_in, color: iconColor),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!.zoom_in),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 3)
                      PopupMenuItem(
                        value: 'zoom_out',
                        enabled: zoomStatus.canZoomOut,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = zoomStatus.canZoomOut;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                Icon(Icons.zoom_out, color: iconColor),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!.zoom_out),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 4)
                      PopupMenuItem(
                        value: 'reset',
                        enabled: zoomStatus.canReset,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = zoomStatus.canReset;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                Icon(Icons.zoom_out_map, color: iconColor),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .restore_original_scale),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 5) const PopupMenuDivider(),
                    if (numButtons < 5)
                      PopupMenuItem(
                        padding: viewModel.isNegative
                            ? const EdgeInsets.symmetric(horizontal: 4.0)
                            : const EdgeInsets.symmetric(horizontal: 12.0),
                        value: 'toggle_negative',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived &&
                            viewModel.localPageLoaded[
                                    viewModel.selectedPage!.image] ==
                                true,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                if (isEnabled && viewModel.isNegative)
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: colorScheme.secondaryContainer,
                                    ),
                                    child: Icon(Icons.invert_colors,
                                        color: colorScheme.primary),
                                  )
                                else
                                  Icon(Icons.invert_colors, color: iconColor),
                                if (!viewModel.isNegative)
                                  const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .toggle_negative),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 6)
                      PopupMenuItem(
                        padding: viewModel.isMonochrome
                            ? const EdgeInsets.symmetric(horizontal: 4.0)
                            : const EdgeInsets.symmetric(horizontal: 12.0),
                        value: 'toggle_monochrome',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived &&
                            !viewModel.primarySource.isMonochrome &&
                            viewModel.localPageLoaded[
                                    viewModel.selectedPage!.image] ==
                                true,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived &&
                                !viewModel.primarySource.isMonochrome;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                if (isEnabled && viewModel.isMonochrome)
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: colorScheme.secondaryContainer,
                                    ),
                                    child: Icon(Icons.monochrome_photos,
                                        color: colorScheme.primary),
                                  )
                                else
                                  Icon(Icons.monochrome_photos,
                                      color: iconColor),
                                if (!viewModel.isMonochrome)
                                  const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .toggle_monochrome),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 7)
                      PopupMenuItem(
                        padding: viewModel.brightness != 0 ||
                                viewModel.contrast != 100
                            ? const EdgeInsets.symmetric(horizontal: 4.0)
                            : const EdgeInsets.symmetric(horizontal: 12.0),
                        value: 'brightness_contrast',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived &&
                            viewModel.localPageLoaded[
                                    viewModel.selectedPage!.image] ==
                                true,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                if (isEnabled &&
                                    (viewModel.brightness != 0 ||
                                        viewModel.contrast != 100))
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: colorScheme.secondaryContainer,
                                    ),
                                    child: Icon(Icons.brightness_6,
                                        color: colorScheme.primary),
                                  )
                                else
                                  Icon(Icons.brightness_6, color: iconColor),
                                if (viewModel.brightness == 0 &&
                                    viewModel.contrast == 100)
                                  const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .brightness_contrast),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 8)
                      PopupMenuItem(
                        padding: viewModel.selectedArea != null &&
                                viewModel.tolerance != 0
                            ? const EdgeInsets.symmetric(horizontal: 4.0)
                            : const EdgeInsets.symmetric(horizontal: 12.0),
                        value: 'replace_color',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived &&
                            viewModel.localPageLoaded[
                                    viewModel.selectedPage!.image] ==
                                true,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                if (isEnabled &&
                                    viewModel.selectedArea != null &&
                                    viewModel.tolerance != 0)
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: colorScheme.secondaryContainer,
                                    ),
                                    child: Icon(Icons.format_paint,
                                        color: colorScheme.primary),
                                  )
                                else
                                  Icon(Icons.format_paint, color: iconColor),
                                if (viewModel.selectedArea == null ||
                                    viewModel.tolerance == 0)
                                  const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .color_replacement),
                              ],
                            );
                          },
                        ),
                      ),
                    if (numButtons < 9)
                      PopupMenuItem(
                        value: 'reset_page',
                        enabled: viewModel.selectedPage != null &&
                            viewModel.primarySource.permissionsReceived &&
                            viewModel.localPageLoaded[
                                    viewModel.selectedPage!.image] ==
                                true,
                        child: Builder(
                          builder: (context) {
                            final isEnabled = viewModel.selectedPage != null &&
                                viewModel.primarySource.permissionsReceived;
                            final iconColor = isEnabled
                                ? colorScheme.primary
                                : colorScheme.onSurface.withValues(alpha: 0.38);
                            return Row(
                              children: [
                                Icon(Icons.cleaning_services, color: iconColor),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .page_settings_reset),
                              ],
                            );
                          },
                        ),
                      ),
                  ],
                );

                viewModel.setMenuOpen(false);

                if (selectedValue != null) {
                  aud.playSound("click");
                  switch (selectedValue) {
                    case 'refresh':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived) {
                        viewModel.loadImage(viewModel.selectedPage!.image,
                            isReload: true);
                      }
                      break;
                    case 'zoom_in':
                      if (zoomStatus.canZoomIn) {
                        viewModel.imageController.zoomIn(viewportCenter);
                      }
                      break;
                    case 'zoom_out':
                      if (zoomStatus.canZoomOut) {
                        viewModel.imageController
                            .zoomOut(viewportCenter, viewportSize);
                      }
                      break;
                    case 'reset':
                      if (zoomStatus.canReset) {
                        viewModel.imageController.backToMinScale();
                      }
                      break;
                    case 'toggle_negative':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived) {
                        viewModel.toggleNegative();
                      }
                      break;
                    case 'toggle_monochrome':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived &&
                          !viewModel.primarySource.isMonochrome) {
                        viewModel.toggleMonochrome();
                      }
                      break;
                    case 'brightness_contrast':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived) {
                        _showBrightnessContrastDialog();
                      }
                      break;
                    case 'replace_color':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived) {
                        _showReplaceColorDialog();
                      }
                      break;
                    case 'reset_page':
                      if (viewModel.selectedPage != null &&
                          viewModel.primarySource.permissionsReceived) {
                        viewModel.removePageSettings();
                      }
                      break;
                  }
                }
              },
            );
          },
        ),
    ];
  }

  Widget _buildDropdownItem(
      BuildContext context, PrimarySourceViewModel viewModel, model.Page page) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final bool? loaded = viewModel.localPageLoaded[page.image];
    final Color textColor = loaded == null
        ? colorScheme.onSurfaceVariant
        : (loaded ? colorScheme.primary : colorScheme.error);

    final FontWeight weight =
        page == viewModel.selectedPage ? FontWeight.bold : FontWeight.normal;

    return Text.rich(
      TextSpan(
        style: TextStyle(
          color: textColor,
          fontWeight: weight,
        ),
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
                        selectedArea, colorToReplace, newColor, tolerance);
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
