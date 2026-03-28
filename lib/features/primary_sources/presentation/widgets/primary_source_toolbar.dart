import 'dart:async';

import 'package:flutter/material.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_source_screen.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar_overflow_menu.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceToolbar extends StatelessWidget {
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
  final bool isBottom;
  final double dropdownWidth;
  final Future<void> Function(model.Page? newPage) onChangeSelectedPage;
  final VoidCallback onShowCommonInfo;
  final Future<void> Function() onReloadImage;
  final VoidCallback onToggleNegative;
  final VoidCallback onToggleMonochrome;
  final VoidCallback onToggleShowWordSeparators;
  final VoidCallback onToggleShowStrongNumbers;
  final VoidCallback onToggleShowVerseNumbers;
  final VoidCallback onRemovePageSettings;
  final VoidCallback onOpenBrightnessContrastDialog;
  final VoidCallback onOpenReplaceColorDialog;
  final ValueChanged<bool> onSetMenuOpen;
  final aud = AudioController();

  PrimarySourceToolbar({
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
    required this.isBottom,
    required this.dropdownWidth,
    required this.onChangeSelectedPage,
    required this.onShowCommonInfo,
    required this.onReloadImage,
    required this.onToggleNegative,
    required this.onToggleMonochrome,
    required this.onToggleShowWordSeparators,
    required this.onToggleShowStrongNumbers,
    required this.onToggleShowVerseNumbers,
    required this.onRemovePageSettings,
    required this.onOpenBrightnessContrastDialog,
    required this.onOpenReplaceColorDialog,
    required this.onSetMenuOpen,
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
    }

    return Row(children: _buildFullActions(context));
  }

  int _calcFitButtons(double actionWidth) {
    const double buttonCellWidth = 40.0;
    const double startOffset = 80.0;
    final fit = ((actionWidth - startOffset) / buttonCellWidth).floor();
    return fit.clamp(0, PrimarySourceScreen.numButtons);
  }

  bool get _hasSelectedPageWithPermissions =>
      selectedPage != null && primarySource.permissionsReceived;

  bool get _selectedPageImageReady =>
      selectedPage != null &&
      primarySource.permissionsReceived &&
      localPageLoaded[selectedPage!.image] == true;

  List<Widget> _buildFullActions(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return [
      DropdownButton<model.Page>(
        value: selectedPage,
        hint: Text(
          primarySource.pages.isEmpty || !primarySource.permissionsReceived
              ? AppLocalizations.of(context)!.images_are_missing
              : '',
          style: TextStyle(color: colorScheme.onSurfaceVariant),
        ),
        onChanged: (model.Page? newPage) {
          aud.playSound('click');
          if (primarySource.permissionsReceived) {
            unawaited(onChangeSelectedPage(newPage));
            onShowCommonInfo();
          }
        },
        items: primarySource.permissionsReceived
            ? primarySource.pages.map<DropdownMenuItem<model.Page>>((page) {
                return DropdownMenuItem<model.Page>(
                  value: page,
                  child: _buildDropdownItem(context, page),
                );
              }).toList()
            : List.empty(),
        onTap: () {
          aud.playSound('click');
        },
      ),
      IconButton(
        icon: refreshError ? Icon(Icons.sync_problem) : Icon(Icons.sync),
        color: refreshError ? colorScheme.error : colorScheme.primary,
        tooltip: AppLocalizations.of(context)!.reload_image,
        onPressed: _hasSelectedPageWithPermissions
            ? () {
                aud.playSound('click');
                unawaited(onReloadImage());
              }
            : null,
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_in),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.zoom_in,
            onPressed: zoomStatus.canZoomIn
                ? () {
                    aud.playSound('click');
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    imageController.zoomIn(viewportCenter);
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.zoom_out,
            onPressed: zoomStatus.canZoomOut
                ? () {
                    aud.playSound('click');
                    final viewportSize = Size(
                      MediaQuery.of(context).size.width,
                      MediaQuery.of(context).size.height,
                    );
                    final viewportCenter = Offset(
                      viewportSize.width / 2,
                      viewportSize.height / 2,
                    );
                    imageController.zoomOut(viewportCenter, viewportSize);
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out_map),
            color: colorScheme.primary,
            tooltip: AppLocalizations.of(context)!.restore_original_scale,
            onPressed: zoomStatus.canReset
                ? () {
                    aud.playSound('click');
                    imageController.backToMinScale();
                  }
                : null,
          );
        },
      ),
      IconButton(
        icon: const Icon(Icons.invert_colors),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: isNegative
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_negative,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onToggleNegative();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.monochrome_photos),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: isMonochrome
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_monochrome,
        onPressed: _selectedPageImageReady && !primarySource.isMonochrome
            ? () {
                aud.playSound('click');
                onToggleMonochrome();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.brightness_6),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: brightness != 0 || contrast != 100
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.brightness_contrast,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onOpenBrightnessContrastDialog();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.format_paint),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: selectedArea != null && tolerance != 0
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.color_replacement,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onOpenReplaceColorDialog();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.horizontal_distribute),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: showWordSeparators
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_word_separators,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onToggleShowWordSeparators();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.local_offer),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: showStrongNumbers
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_strong_numbers,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onToggleShowStrongNumbers();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.format_list_numbered),
        color: colorScheme.primary,
        style: IconButton.styleFrom(
          backgroundColor: showVerseNumbers
              ? colorScheme.secondaryContainer
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_show_verse_numbers,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onToggleShowVerseNumbers();
              }
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.cleaning_services),
        color: colorScheme.primary,
        tooltip: AppLocalizations.of(context)!.page_settings_reset,
        onPressed: _selectedPageImageReady
            ? () {
                aud.playSound('click');
                onRemovePageSettings();
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
          primarySource: primarySource,
          selectedPage: selectedPage,
          localPageLoaded: localPageLoaded,
          refreshError: refreshError,
          isNegative: isNegative,
          isMonochrome: isMonochrome,
          brightness: brightness,
          contrast: contrast,
          selectedArea: selectedArea,
          tolerance: tolerance,
          showWordSeparators: showWordSeparators,
          showStrongNumbers: showStrongNumbers,
          showVerseNumbers: showVerseNumbers,
          zoomStatusNotifier: zoomStatusNotifier,
          imageController: imageController,
          onSetMenuOpen: onSetMenuOpen,
          onReloadImage: onReloadImage,
          onToggleNegative: onToggleNegative,
          onToggleMonochrome: onToggleMonochrome,
          onToggleShowWordSeparators: onToggleShowWordSeparators,
          onToggleShowStrongNumbers: onToggleShowStrongNumbers,
          onToggleShowVerseNumbers: onToggleShowVerseNumbers,
          onRemovePageSettings: onRemovePageSettings,
          onOpenBrightnessContrastDialog: onOpenBrightnessContrastDialog,
          onOpenReplaceColorDialog: onOpenReplaceColorDialog,
          audioController: aud,
          numButtons: numButtons,
        ),
    ];
  }

  Widget _buildDropdownItem(BuildContext context, model.Page page) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final bool? loaded = localPageLoaded[page.image];
    final Color textColor = loaded == null
        ? colorScheme.onSurfaceVariant
        : (loaded ? colorScheme.primary : colorScheme.error);

    final FontWeight weight = page == selectedPage
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
}
