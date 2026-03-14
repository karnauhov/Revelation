import 'dart:async';

import 'package:flutter/material.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceToolbarOverflowMenuButton extends StatelessWidget {
  final PrimarySource primarySource;
  final model.Page? selectedPage;
  final Map<String, bool?> localPageLoaded;
  final bool refreshError;
  final bool isNegative;
  final bool isMonochrome;
  final double brightness;
  final double contrast;
  final Rect? selectedArea;
  final double tolerance;
  final bool showWordSeparators;
  final bool showStrongNumbers;
  final bool showVerseNumbers;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier;
  final ImagePreviewController imageController;
  final ValueChanged<bool> onSetMenuOpen;
  final Future<void> Function() onReloadImage;
  final VoidCallback onToggleNegative;
  final VoidCallback onToggleMonochrome;
  final VoidCallback onToggleShowWordSeparators;
  final VoidCallback onToggleShowStrongNumbers;
  final VoidCallback onToggleShowVerseNumbers;
  final VoidCallback onRemovePageSettings;
  final VoidCallback onOpenBrightnessContrastDialog;
  final VoidCallback onOpenReplaceColorDialog;
  final AudioController audioController;
  final int numButtons;

  const PrimarySourceToolbarOverflowMenuButton({
    required this.primarySource,
    required this.selectedPage,
    required this.localPageLoaded,
    required this.refreshError,
    required this.isNegative,
    required this.isMonochrome,
    required this.brightness,
    required this.contrast,
    required this.selectedArea,
    required this.tolerance,
    required this.showWordSeparators,
    required this.showStrongNumbers,
    required this.showVerseNumbers,
    required this.zoomStatusNotifier,
    required this.imageController,
    required this.onSetMenuOpen,
    required this.onReloadImage,
    required this.onToggleNegative,
    required this.onToggleMonochrome,
    required this.onToggleShowWordSeparators,
    required this.onToggleShowStrongNumbers,
    required this.onToggleShowVerseNumbers,
    required this.onRemovePageSettings,
    required this.onOpenBrightnessContrastDialog,
    required this.onOpenReplaceColorDialog,
    required this.audioController,
    required this.numButtons,
    super.key,
  });

  bool get _hasSelectedPageWithPermissions =>
      selectedPage != null && primarySource.permissionsReceived;

  bool get _selectedPageImageReady =>
      selectedPage != null &&
      primarySource.permissionsReceived &&
      localPageLoaded[selectedPage!.image] == true;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ZoomStatus>(
      valueListenable: zoomStatusNotifier,
      builder: (context, zoomStatus, child) {
        final GlobalKey menuKey = GlobalKey();
        final colorScheme = Theme.of(context).colorScheme;
        return IconButton(
          key: menuKey,
          icon: const Icon(Icons.more_vert),
          color: colorScheme.primary,
          tooltip: AppLocalizations.of(context)!.menu,
          onPressed: () async {
            audioController.playSound('click');
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

            onSetMenuOpen(true);

            final selectedValue = await showMenu<String>(
              context: context,
              position: position,
              items: _buildMenuItems(context, colorScheme, zoomStatus),
            );

            onSetMenuOpen(false);

            if (selectedValue != null) {
              audioController.playSound('click');
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
          enabled: _hasSelectedPageWithPermissions,
          child: Builder(
            builder: (context) {
              final isEnabled = _hasSelectedPageWithPermissions;
              final iconColor = isEnabled
                  ? colorScheme.primary
                  : colorScheme.onSurface.withValues(alpha: 0.38);
              return Row(
                children: [
                  refreshError
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
              final iconColor = zoomStatus.canZoomIn
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
              final iconColor = zoomStatus.canZoomOut
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
              final iconColor = zoomStatus.canReset
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
          padding: isNegative
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_negative',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.invert_colors,
            active: isNegative,
            label: AppLocalizations.of(context)!.toggle_negative,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 6)
        PopupMenuItem(
          padding: isMonochrome
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_monochrome',
          enabled: _selectedPageImageReady && !primarySource.isMonochrome,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.monochrome_photos,
            active: isMonochrome,
            label: AppLocalizations.of(context)!.toggle_monochrome,
            enabled:
                _hasSelectedPageWithPermissions && !primarySource.isMonochrome,
          ),
        ),
      if (numButtons < 7)
        PopupMenuItem(
          padding: brightness != 0 || contrast != 100
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'brightness_contrast',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.brightness_6,
            active: brightness != 0 || contrast != 100,
            label: AppLocalizations.of(context)!.brightness_contrast,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 8)
        PopupMenuItem(
          padding: selectedArea != null && tolerance != 0
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'replace_color',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.format_paint,
            active: selectedArea != null && tolerance != 0,
            label: AppLocalizations.of(context)!.color_replacement,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 9)
        PopupMenuItem(
          padding: showWordSeparators
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_word_separators',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.horizontal_distribute,
            active: showWordSeparators,
            label: AppLocalizations.of(context)!.toggle_show_word_separators,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 10)
        PopupMenuItem(
          padding: showStrongNumbers
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_strong_numbers',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.local_offer,
            active: showStrongNumbers,
            label: AppLocalizations.of(context)!.toggle_show_strong_numbers,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 11)
        PopupMenuItem(
          padding: showVerseNumbers
              ? const EdgeInsets.symmetric(horizontal: 4.0)
              : const EdgeInsets.symmetric(horizontal: 12.0),
          value: 'toggle_show_verse_numbers',
          enabled: _selectedPageImageReady,
          child: _buildToggleMenuRow(
            context: context,
            colorScheme: colorScheme,
            icon: Icons.format_list_numbered,
            active: showVerseNumbers,
            label: AppLocalizations.of(context)!.toggle_show_verse_numbers,
            enabled: _hasSelectedPageWithPermissions,
          ),
        ),
      if (numButtons < 12)
        PopupMenuItem(
          value: 'reset_page',
          enabled: _selectedPageImageReady,
          child: Builder(
            builder: (context) {
              final iconColor = _hasSelectedPageWithPermissions
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

  Widget _buildToggleMenuRow({
    required BuildContext context,
    required ColorScheme colorScheme,
    required IconData icon,
    required bool active,
    required String label,
    required bool enabled,
  }) {
    final iconColor = enabled
        ? colorScheme.primary
        : colorScheme.onSurface.withValues(alpha: 0.38);
    return Row(
      children: [
        if (enabled && active)
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: colorScheme.secondaryContainer,
            ),
            child: Icon(icon, color: colorScheme.primary),
          )
        else
          Icon(icon, color: iconColor),
        if (!active) const SizedBox(width: 8),
        Text(label),
      ],
    );
  }

  void _handleSelectedAction(
    String selectedValue,
    ZoomStatus zoomStatus,
    Offset viewportCenter,
    Size viewportSize,
  ) {
    switch (selectedValue) {
      case 'refresh':
        if (_hasSelectedPageWithPermissions) {
          unawaited(onReloadImage());
        }
        break;
      case 'zoom_in':
        if (zoomStatus.canZoomIn) {
          imageController.zoomIn(viewportCenter);
        }
        break;
      case 'zoom_out':
        if (zoomStatus.canZoomOut) {
          imageController.zoomOut(viewportCenter, viewportSize);
        }
        break;
      case 'reset':
        if (zoomStatus.canReset) {
          imageController.backToMinScale();
        }
        break;
      case 'toggle_negative':
        if (_hasSelectedPageWithPermissions) {
          onToggleNegative();
        }
        break;
      case 'toggle_monochrome':
        if (_hasSelectedPageWithPermissions && !primarySource.isMonochrome) {
          onToggleMonochrome();
        }
        break;
      case 'brightness_contrast':
        if (_hasSelectedPageWithPermissions) {
          onOpenBrightnessContrastDialog();
        }
        break;
      case 'replace_color':
        if (_hasSelectedPageWithPermissions) {
          onOpenReplaceColorDialog();
        }
        break;
      case 'toggle_show_word_separators':
        if (_hasSelectedPageWithPermissions) {
          onToggleShowWordSeparators();
        }
        break;
      case 'toggle_show_strong_numbers':
        if (_hasSelectedPageWithPermissions) {
          onToggleShowStrongNumbers();
        }
        break;
      case 'toggle_show_verse_numbers':
        if (_hasSelectedPageWithPermissions) {
          onToggleShowVerseNumbers();
        }
        break;
      case 'reset_page':
        if (_hasSelectedPageWithPermissions) {
          onRemovePageSettings();
        }
        break;
    }
  }
}
