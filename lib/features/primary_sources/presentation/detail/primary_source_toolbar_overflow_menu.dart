import 'package:flutter/material.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_source_view_model.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceToolbarOverflowMenuButton extends StatelessWidget {
  final PrimarySourceViewModel viewModel;
  final AudioController audioController;
  final int numButtons;
  final VoidCallback onOpenBrightnessContrastDialog;
  final VoidCallback onOpenReplaceColorDialog;

  const PrimarySourceToolbarOverflowMenuButton({
    required this.viewModel,
    required this.audioController,
    required this.numButtons,
    required this.onOpenBrightnessContrastDialog,
    required this.onOpenReplaceColorDialog,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ZoomStatus>(
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
            audioController.playSound("click");
            final RenderBox button =
                menuKey.currentContext!.findRenderObject() as RenderBox;
            final RenderBox overlay =
                Overlay.of(context).context.findRenderObject() as RenderBox;
            final RelativeRect position = RelativeRect.fromRect(
              Rect.fromPoints(
                button.localToGlobal(Offset.zero, ancestor: overlay),
                button.localToGlobal(
                  button.size.bottomRight(Offset.zero),
                  ancestor: overlay,
                ),
              ),
              Offset.zero & overlay.size,
            );

            final viewportSize = MediaQuery.of(context).size;
            final viewportCenter = Offset(
              viewportSize.width / 2,
              viewportSize.height / 2,
            );

            viewModel.setMenuOpen(true);

            final selectedValue = await showMenu<String>(
              context: context,
              position: position,
              items: _buildMenuItems(context, colorScheme, zoomStatus),
            );

            viewModel.setMenuOpen(false);

            if (selectedValue != null) {
              audioController.playSound("click");
              _handleSelectedAction(
                selectedValue,
                zoomStatus,
                viewportCenter,
                viewportSize,
              );
            }
          },
        );
      },
    );
  }

  List<PopupMenuEntry<String>> _buildMenuItems(
    BuildContext context,
    ColorScheme colorScheme,
    ZoomStatus zoomStatus,
  ) {
    return [
      if (numButtons < 1)
        PopupMenuItem(
          value: 'refresh',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  viewModel.refreshError
                      ? Icon(
                          Icons.sync_problem,
                          color: isEnabled
                              ? colorScheme.error
                              : colorScheme.onSurface.withValues(alpha: 0.38),
                        )
                      : Icon(Icons.sync, color: iconColor),
                  const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.reload_image),
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
                  Text(AppLocalizations.of(context)!.restore_original_scale),
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
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
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
                      child: Icon(
                        Icons.invert_colors,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.invert_colors, color: iconColor),
                  if (!viewModel.isNegative) const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.toggle_negative),
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
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              !viewModel.primarySource.isMonochrome &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
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
                      child: Icon(
                        Icons.monochrome_photos,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.monochrome_photos, color: iconColor),
                  if (!viewModel.isMonochrome) const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.toggle_monochrome),
                ],
              );
            },
          ),
        ),
      if (numButtons < 7)
        PopupMenuItem(
          padding: viewModel.brightness != 0 || viewModel.contrast != 100
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'brightness_contrast',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  if (isEnabled &&
                      (viewModel.brightness != 0 || viewModel.contrast != 100))
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: colorScheme.secondaryContainer,
                      ),
                      child: Icon(
                        Icons.brightness_6,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.brightness_6, color: iconColor),
                  if (viewModel.brightness == 0 && viewModel.contrast == 100)
                    const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.brightness_contrast),
                ],
              );
            },
          ),
        ),
      if (numButtons < 8)
        PopupMenuItem(
          padding: viewModel.selectedArea != null && viewModel.tolerance != 0
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'replace_color',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
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
                      child: Icon(
                        Icons.format_paint,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.format_paint, color: iconColor),
                  if (viewModel.selectedArea == null ||
                      viewModel.tolerance == 0)
                    const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.color_replacement),
                ],
              );
            },
          ),
        ),
      if (numButtons < 9)
        PopupMenuItem(
          padding: viewModel.showWordSeparators
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_word_separators',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  if (isEnabled && viewModel.showWordSeparators)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: colorScheme.secondaryContainer,
                      ),
                      child: Icon(
                        Icons.horizontal_distribute,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.horizontal_distribute, color: iconColor),
                  if (!viewModel.showWordSeparators) const SizedBox(width: 8),
                  Text(
                    AppLocalizations.of(context)!.toggle_show_word_separators,
                  ),
                ],
              );
            },
          ),
        ),
      if (numButtons < 10)
        PopupMenuItem(
          padding: viewModel.showStrongNumbers
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_strong_numbers',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  if (isEnabled && viewModel.showStrongNumbers)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: colorScheme.secondaryContainer,
                      ),
                      child: Icon(
                        Icons.local_offer,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.local_offer, color: iconColor),
                  if (!viewModel.showStrongNumbers) const SizedBox(width: 8),
                  Text(
                    AppLocalizations.of(context)!.toggle_show_strong_numbers,
                  ),
                ],
              );
            },
          ),
        ),
      if (numButtons < 11)
        PopupMenuItem(
          padding: viewModel.showVerseNumbers
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_verse_numbers',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  if (isEnabled && viewModel.showVerseNumbers)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: colorScheme.secondaryContainer,
                      ),
                      child: Icon(
                        Icons.format_list_numbered,
                        color: colorScheme.primary,
                      ),
                    )
                  else
                    Icon(Icons.format_list_numbered, color: iconColor),
                  if (!viewModel.showVerseNumbers) const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.toggle_show_verse_numbers),
                ],
              );
            },
          ),
        ),
      if (numButtons < 12)
        PopupMenuItem(
          value: 'reset_page',
          enabled:
              viewModel.selectedPage != null &&
              viewModel.primarySource.permissionsReceived &&
              viewModel.localPageLoaded[viewModel.selectedPage!.image] == true,
          child: Builder(
            builder: (context) {
              final isEnabled =
                  viewModel.selectedPage != null &&
                  viewModel.primarySource.permissionsReceived;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  Icon(Icons.cleaning_services, color: iconColor),
                  const SizedBox(width: 8),
                  Text(AppLocalizations.of(context)!.page_settings_reset),
                ],
              );
            },
          ),
        ),
    ];
  }

  void _handleSelectedAction(
    String selectedValue,
    ZoomStatus zoomStatus,
    Offset viewportCenter,
    Size viewportSize,
  ) {
    switch (selectedValue) {
      case 'refresh':
        if (viewModel.selectedPage != null &&
            viewModel.primarySource.permissionsReceived) {
          viewModel.loadImage(viewModel.selectedPage!.image, isReload: true);
        }
        break;
      case 'zoom_in':
        if (zoomStatus.canZoomIn) {
          viewModel.imageController.zoomIn(viewportCenter);
        }
        break;
      case 'zoom_out':
        if (zoomStatus.canZoomOut) {
          viewModel.imageController.zoomOut(viewportCenter, viewportSize);
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
          onOpenBrightnessContrastDialog();
        }
        break;
      case 'replace_color':
        if (viewModel.selectedPage != null &&
            viewModel.primarySource.permissionsReceived) {
          onOpenReplaceColorDialog();
        }
        break;
      case 'toggle_show_word_separators':
        if (viewModel.selectedPage != null &&
            viewModel.primarySource.permissionsReceived) {
          viewModel.toggleShowWordSeparators();
        }
        break;
      case 'toggle_show_strong_numbers':
        if (viewModel.selectedPage != null &&
            viewModel.primarySource.permissionsReceived) {
          viewModel.toggleShowStrongNumbers();
        }
        break;
      case 'toggle_show_verse_numbers':
        if (viewModel.selectedPage != null &&
            viewModel.primarySource.permissionsReceived) {
          viewModel.toggleShowVerseNumbers();
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
}
