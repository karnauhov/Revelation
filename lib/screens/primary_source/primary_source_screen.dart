import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/screens/primary_source/brightness_contrast_dialog.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:revelation/screens/primary_source/image_preview.dart';

class PrimarySourceScreen extends StatelessWidget {
  final PrimarySource primarySource;
  static final numButtons = 7;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  Widget build(BuildContext context) {
    final dropdownWidth = _calcPagesListWidth(context);
    TextTheme theme = Theme.of(context).textTheme;
    return ChangeNotifierProvider<PrimarySourceViewModel>(
      create: (_) => PrimarySourceViewModel(primarySource: primarySource),
      child: Consumer<PrimarySourceViewModel>(
        builder: (context, viewModel, child) {
          if (primarySource.permissionsReceived &&
              viewModel.selectedPage != null &&
              !primarySource.pages.contains(viewModel.selectedPage)) {
            viewModel.changeSelectedPage(
              primarySource.pages.isNotEmpty ? primarySource.pages.first : null,
            );
          }

          final double screenWidth = MediaQuery.of(context).size.width;
          final bool isBottom = _isBottomToolbar(screenWidth, dropdownWidth);

          return Scaffold(
            appBar: AppBar(
              title: getStyledText(
                primarySource.title,
                Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              actions: isBottom
                  ? null
                  : [
                      PrimarySourceToolbar(
                        viewModel: viewModel,
                        primarySource: primarySource,
                        isBottom: false,
                        dropdownWidth: dropdownWidth,
                      ),
                    ],
              bottom: isBottom
                  ? PreferredSize(
                      preferredSize: const Size.fromHeight(32.0),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: PrimarySourceToolbar(
                          viewModel: viewModel,
                          primarySource: primarySource,
                          isBottom: true,
                          dropdownWidth: dropdownWidth,
                        ),
                      ),
                    )
                  : null,
            ),
            body: Column(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(10.0, 0, 10, 0),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.black, width: 1.0),
                      ),
                      child: viewModel.isLoading
                          ? const Center(child: CircularProgressIndicator())
                          : viewModel.imageData != null
                              ? ImagePreview(
                                  imageData: viewModel.imageData!,
                                  controller: viewModel.imageController,
                                  isNegative: viewModel.isNegative,
                                  isMonochrome: viewModel.isMonochrome,
                                  brightness: viewModel.brightness,
                                  contrast: viewModel.contrast,
                                )
                              : Center(
                                  child: Text(AppLocalizations.of(context)!
                                      .image_not_loaded),
                                ),
                    ),
                  ),
                ),
                if (primarySource.attributes != null &&
                    primarySource.attributes!.isNotEmpty &&
                    primarySource.permissionsReceived)
                  Align(
                    alignment: Alignment.centerRight,
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(10, 0, 10, 2),
                      child: Text.rich(
                        TextSpan(
                          style: theme.bodySmall!.copyWith(fontSize: 10),
                          children: [
                            if (viewModel.isMobileWeb)
                              TextSpan(
                                text:
                                    '⚠️ ${AppLocalizations.of(context)!.low_quality}; ',
                                style: const TextStyle(color: Colors.blue),
                                recognizer: TapGestureRecognizer()
                                  ..onTap = () {
                                    showCustomDialog(MessageType.warningCommon,
                                        param: AppLocalizations.of(context)!
                                            .low_quality_message);
                                  },
                              ),
                            ..._buildLinkSpans(primarySource.attributes!),
                          ],
                        ),
                        maxLines: 5,
                        softWrap: true,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                if (primarySource.attributes == null ||
                    primarySource.attributes!.isEmpty ||
                    !primarySource.permissionsReceived)
                  Text.rich(TextSpan(text: ""))
              ],
            ),
          );
        },
      ),
    );
  }

  List<InlineSpan> _buildLinkSpans(List<Map<String, String>> links) {
    List<InlineSpan> spans = [];
    for (int i = 0; i < links.length; i++) {
      var link = links[i];
      if (link['url'] != null && link['url']!.isNotEmpty) {
        spans.add(
          TextSpan(
            text: link['text'],
            style: const TextStyle(color: Colors.blue),
            recognizer: TapGestureRecognizer()
              ..onTap = () {
                launchLink(link['url']!);
              },
          ),
        );
      } else {
        spans.add(
          TextSpan(
            text: link['text'],
          ),
        );
      }
      if (i < links.length - 1) {
        spans.add(const TextSpan(text: '; '));
      }
    }
    return spans;
  }

  double _calcPagesListWidth(BuildContext context) {
    final itemStyle =
        Theme.of(context).textTheme.bodyMedium ?? TextStyle(fontSize: 16);

    double calculateTextWidth(String text) {
      return (TextPainter(
        text: TextSpan(text: text, style: itemStyle),
        textDirection: TextDirection.ltr,
        maxLines: 1,
      )..layout())
          .size
          .width;
    }

    double maxWidth;
    if (primarySource.permissionsReceived && primarySource.pages.isNotEmpty) {
      maxWidth = primarySource.pages
          .map((page) => calculateTextWidth("${page.name} (${page.content})"))
          .reduce((a, b) => a > b ? a : b);
    } else {
      maxWidth =
          calculateTextWidth(AppLocalizations.of(context)!.images_are_missing);
    }
    return maxWidth + 40;
  }

  bool _isBottomToolbar(double screenWidth, double dropdownWidth) {
    const widthForTitle = 100;
    const double iconButtonWidth = 48.0;
    final double actionsWidth = dropdownWidth + numButtons * iconButtonWidth;
    return actionsWidth > screenWidth - widthForTitle * 1 - 60;
  }
}

class PrimarySourceToolbar extends StatelessWidget {
  final PrimarySourceViewModel viewModel;
  final PrimarySource primarySource;
  final bool isBottom;
  final double dropdownWidth;

  const PrimarySourceToolbar({
    required this.viewModel,
    required this.primarySource,
    required this.isBottom,
    required this.dropdownWidth,
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
    return [
      DropdownButton<model.Page>(
        value: viewModel.selectedPage,
        hint: Text(
          primarySource.pages.isEmpty || !primarySource.permissionsReceived
              ? AppLocalizations.of(context)!.images_are_missing
              : "",
        ),
        onChanged: (model.Page? newPage) {
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
      ),
      IconButton(
        icon: viewModel.refreshError
            ? const Icon(Icons.sync_problem)
            : const Icon(Icons.sync),
        tooltip: AppLocalizations.of(context)!.reload_image,
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () => viewModel.loadImage(viewModel.selectedPage!.image,
                isReload: true)
            : null,
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_in),
            tooltip: AppLocalizations.of(context)!.zoom_in,
            onPressed: zoomStatus.canZoomIn
                ? () {
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
            tooltip: AppLocalizations.of(context)!.zoom_out,
            onPressed: zoomStatus.canZoomOut
                ? () {
                    final viewportSize = Size(
                      MediaQuery.of(context).size.width,
                      MediaQuery.of(context).size.height,
                    );
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
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
            tooltip: AppLocalizations.of(context)!.restore_original_scale,
            onPressed: zoomStatus.canReset
                ? () {
                    viewModel.imageController.backToMinScale();
                  }
                : null,
          );
        },
      ),
      IconButton(
        icon: Icon(
          Icons.invert_colors,
          color: viewModel.isNegative
              ? Theme.of(context).colorScheme.secondary
              : null,
        ),
        style: IconButton.styleFrom(
          backgroundColor: viewModel.isNegative
              ? Theme.of(context)
                  .colorScheme
                  .secondary
                  .withAlpha((0.2 * 255).round())
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_negative,
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () => viewModel.toggleNegative()
            : null,
      ),
      IconButton(
        icon: Icon(
          Icons.monochrome_photos,
          color: viewModel.isMonochrome
              ? Theme.of(context).colorScheme.secondary
              : null,
        ),
        style: IconButton.styleFrom(
          backgroundColor: viewModel.isMonochrome
              ? Theme.of(context)
                  .colorScheme
                  .secondary
                  .withAlpha((0.2 * 255).round())
              : Colors.transparent,
          shape: const CircleBorder(),
        ),
        tooltip: AppLocalizations.of(context)!.toggle_monochrome,
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null &&
                !viewModel.primarySource.isMonochrome
            ? () => viewModel.toggleMonochrome()
            : null,
      ),
      IconButton(
        icon: const Icon(Icons.brightness_6),
        tooltip: AppLocalizations.of(context)!.brightness_contrast,
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () {
                _showBrightnessContrastDialog(context);
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
            return PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert),
              tooltip: AppLocalizations.of(context)!.menu,
              onSelected: (value) {
                switch (value) {
                  case 'refresh':
                    if (viewModel.selectedPage != null &&
                        viewModel.primarySource.permissionsReceived) {
                      viewModel.loadImage(viewModel.selectedPage!.image,
                          isReload: true);
                    }
                    break;
                  case 'zoom_in':
                    if (zoomStatus.canZoomIn) {
                      final viewportCenter = Offset(
                        MediaQuery.of(context).size.width / 2,
                        MediaQuery.of(context).size.height / 2,
                      );
                      viewModel.imageController.zoomIn(viewportCenter);
                    }
                    break;
                  case 'zoom_out':
                    if (zoomStatus.canZoomOut) {
                      final viewportSize = Size(
                        MediaQuery.of(context).size.width,
                        MediaQuery.of(context).size.height,
                      );
                      final viewportCenter = Offset(
                        MediaQuery.of(context).size.width / 2,
                        MediaQuery.of(context).size.height / 2,
                      );
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
                      _showBrightnessContrastDialog(context);
                    }
                    break;
                }
              },
              itemBuilder: (context) => [
                if (numButtons < 1)
                  PopupMenuItem(
                    value: 'refresh',
                    enabled: viewModel.selectedPage != null &&
                        viewModel.primarySource.permissionsReceived,
                    child: Row(
                      children: [
                        viewModel.refreshError
                            ? const Icon(Icons.sync_problem,
                                color: Colors.black54)
                            : const Icon(Icons.sync, color: Colors.black54),
                        const SizedBox(width: 8),
                        Text(AppLocalizations.of(context)!.reload_image),
                      ],
                    ),
                  ),
                if (numButtons < 2)
                  PopupMenuItem(
                    value: 'zoom_in',
                    enabled: zoomStatus.canZoomIn,
                    child: Row(
                      children: [
                        const Icon(Icons.zoom_in, color: Colors.black54),
                        const SizedBox(width: 8),
                        Text(AppLocalizations.of(context)!.zoom_in),
                      ],
                    ),
                  ),
                if (numButtons < 3)
                  PopupMenuItem(
                    value: 'zoom_out',
                    enabled: zoomStatus.canZoomOut,
                    child: Row(
                      children: [
                        const Icon(Icons.zoom_out, color: Colors.black54),
                        const SizedBox(width: 8),
                        Text(AppLocalizations.of(context)!.zoom_out),
                      ],
                    ),
                  ),
                if (numButtons < 4)
                  PopupMenuItem(
                    value: 'reset',
                    enabled: zoomStatus.canReset,
                    child: Row(
                      children: [
                        const Icon(Icons.zoom_out_map, color: Colors.black54),
                        const SizedBox(width: 8),
                        Text(AppLocalizations.of(context)!
                            .restore_original_scale),
                      ],
                    ),
                  ),
                if (numButtons < 5) const PopupMenuDivider(),
                if (numButtons < 5)
                  CheckedPopupMenuItem(
                    value: 'toggle_negative',
                    enabled: viewModel.selectedPage != null &&
                        viewModel.primarySource.permissionsReceived,
                    checked: viewModel.isNegative,
                    child: Text(AppLocalizations.of(context)!.toggle_negative),
                  ),
                if (numButtons < 6)
                  CheckedPopupMenuItem(
                    value: 'toggle_monochrome',
                    enabled: viewModel.selectedPage != null &&
                        viewModel.primarySource.permissionsReceived &&
                        !viewModel.primarySource.isMonochrome,
                    checked: viewModel.isMonochrome,
                    child:
                        Text(AppLocalizations.of(context)!.toggle_monochrome),
                  ),
                if (numButtons < 7)
                  PopupMenuItem(
                    value: 'brightness_contrast',
                    enabled: viewModel.selectedPage != null &&
                        viewModel.primarySource.permissionsReceived,
                    child: Row(
                      children: [
                        const Icon(Icons.brightness_6, color: Colors.black54),
                        const SizedBox(width: 8),
                        Text(AppLocalizations.of(context)!.brightness_contrast),
                      ],
                    ),
                  ),
              ],
            );
          },
        ),
    ];
  }

  Widget _buildDropdownItem(
      BuildContext context, PrimarySourceViewModel viewModel, model.Page page) {
    final bool? loaded = viewModel.localPageLoaded[page.image];
    return Text(
      "${page.name} (${page.content})",
      style: TextStyle(
        color: loaded == null
            ? Colors.grey.shade900
            : (loaded ? Colors.teal.shade900 : Colors.red.shade900),
        fontWeight: page == viewModel.selectedPage
            ? FontWeight.bold
            : FontWeight.normal,
      ),
    );
  }

  Future<void> _showBrightnessContrastDialog(BuildContext context) {
    return showDialog(
      context: context,
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
}
