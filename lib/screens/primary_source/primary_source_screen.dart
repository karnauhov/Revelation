import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/repositories/pages_repository.dart';
import 'package:revelation/screens/primary_source/image_preview.dart';
import 'package:revelation/screens/primary_source/primary_source_toolbar.dart';
import 'package:revelation/screens/primary_source/strong_number_picker_dialog.dart';
import 'package:revelation/utils/app_link_handler.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

// Define the intent for exiting pipette or selectArea mode
class ExitChooseModeIntent extends Intent {
  const ExitChooseModeIntent();
}

// Define the intent for select rectangle
class SelectRectangleIntent extends Intent {
  const SelectRectangleIntent();
}

// Define the intent for moving to the next/previous selected word
class NavigateSelectedWordIntent extends Intent {
  final bool forward;

  const NavigateSelectedWordIntent({required this.forward});
}

class PrimarySourceScreen extends StatefulWidget {
  final PrimarySource primarySource;
  static final numButtons = 11;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  PrimarySourceScreenState createState() => PrimarySourceScreenState();
}

class PrimarySourceScreenState extends State<PrimarySourceScreen>
    with WidgetsBindingObserver {
  late PrimarySourceViewModel _viewModel;
  final GlobalKey<TooltipState> _referenceTooltipKey =
      GlobalKey<TooltipState>();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeMetrics() {
    super.didChangeMetrics();
    if (_viewModel.isMenuOpen) {
      Navigator.of(context).pop();
      _viewModel.setMenuOpen(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dropdownWidth = calcPagesListWidth(context);
    final theme = Theme.of(context);
    final TextTheme textTheme = theme.textTheme;
    final ColorScheme colorScheme = theme.colorScheme;

    return ChangeNotifierProvider<PrimarySourceViewModel>(
      create: (_) => PrimarySourceViewModel(
        PagesRepository(),
        primarySource: widget.primarySource,
      ),
      child: Consumer<PrimarySourceViewModel>(
        builder: (context, viewModel, child) {
          _viewModel = viewModel;

          if (widget.primarySource.permissionsReceived &&
              viewModel.selectedPage != null &&
              !widget.primarySource.pages.contains(viewModel.selectedPage)) {
            viewModel.changeSelectedPage(
              widget.primarySource.pages.isNotEmpty
                  ? widget.primarySource.pages.first
                  : null,
            );
            viewModel.showCommonInfo(context);
          }

          final double screenWidth = MediaQuery.of(context).size.width;
          final bool isBottom = _isBottomToolbar(screenWidth, dropdownWidth);
          final bool allowWordNavigationByArrows = isDesktop() || isWeb();
          final bool isWordSelected =
              viewModel.currentDescriptionType == DescriptionType.word &&
              viewModel.currentDescriptionNumber != null &&
              (viewModel.selectedPage?.words.isNotEmpty ?? false);
          final shortcuts = <ShortcutActivator, Intent>{
            const SingleActivator(LogicalKeyboardKey.escape):
                const ExitChooseModeIntent(),
            const SingleActivator(LogicalKeyboardKey.backspace):
                const ExitChooseModeIntent(),
            const SingleActivator(LogicalKeyboardKey.keyR, alt: true):
                const SelectRectangleIntent(),
          };

          if (allowWordNavigationByArrows && isWordSelected) {
            shortcuts.addAll({
              const SingleActivator(LogicalKeyboardKey.arrowLeft):
                  const NavigateSelectedWordIntent(forward: false),
              const SingleActivator(LogicalKeyboardKey.arrowUp):
                  const NavigateSelectedWordIntent(forward: false),
              const SingleActivator(LogicalKeyboardKey.arrowRight):
                  const NavigateSelectedWordIntent(forward: true),
              const SingleActivator(LogicalKeyboardKey.arrowDown):
                  const NavigateSelectedWordIntent(forward: true),
            });
          }

          return PopScope(
            canPop: !viewModel.pipetteMode && !viewModel.selectAreaMode,
            onPopInvokedWithResult: (didPop, result) {
              if (!didPop && viewModel.pipetteMode) {
                viewModel.finishPipetteMode(null);
              }
              if (!didPop && viewModel.selectAreaMode) {
                viewModel.finishSelectAreaMode(null);
              }
            },
            child: Shortcuts(
              shortcuts: shortcuts,
              child: Actions(
                actions: {
                  ExitChooseModeIntent: CallbackAction<ExitChooseModeIntent>(
                    onInvoke: (intent) {
                      if (viewModel.pipetteMode) {
                        viewModel.finishPipetteMode(null);
                      } else if (viewModel.selectAreaMode) {
                        viewModel.finishSelectAreaMode(null);
                      }
                      return null;
                    },
                  ),
                  SelectRectangleIntent: CallbackAction<SelectRectangleIntent>(
                    onInvoke: (intent) {
                      viewModel.startGettingServiceRectangle((rect) {
                        if (rect != null &&
                            viewModel.imageController.imageSize != null &&
                            viewModel.imageController.imageSize!.width != 0 &&
                            viewModel.imageController.imageSize!.height != 0) {
                          final w = viewModel.imageController.imageSize!.width;
                          final h = viewModel.imageController.imageSize!.height;
                          double left = roundTo(rect.left / w, 3);
                          double top = roundTo(rect.top / h, 3);
                          double right = roundTo(rect.right / w, 3);
                          double bottom = roundTo(rect.bottom / h, 3);
                          String result =
                              "PageRect(${left}, ${top}, ${right}, ${bottom}),";
                          Clipboard.setData(ClipboardData(text: result));
                          log.debug(result);
                        }
                      });
                      return null;
                    },
                  ),
                  NavigateSelectedWordIntent:
                      CallbackAction<NavigateSelectedWordIntent>(
                        onInvoke: (intent) {
                          _tryNavigateSelectedWord(
                            viewModel,
                            forward: intent.forward,
                          );
                          return null;
                        },
                      ),
                },
                child: Focus(
                  autofocus: true,
                  child: Scaffold(
                    appBar: viewModel.selectAreaMode
                        ? AppBar(
                            title: Text(
                              AppLocalizations.of(context)!.select_area_header,
                              style: textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            foregroundColor: colorScheme.primary,
                          )
                        : viewModel.pipetteMode
                        ? AppBar(
                            title: Text(
                              AppLocalizations.of(context)!.pick_color_header,
                              style: textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            foregroundColor: colorScheme.primary,
                          )
                        : AppBar(
                            title: getStyledText(
                              widget.primarySource.title,
                              textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            actions: isBottom
                                ? null
                                : [
                                    PrimarySourceToolbar(
                                      viewModel: viewModel,
                                      primarySource: widget.primarySource,
                                      isBottom: false,
                                      dropdownWidth: dropdownWidth,
                                      screenContext: context,
                                    ),
                                  ],
                            bottom: isBottom
                                ? PreferredSize(
                                    preferredSize: const Size.fromHeight(32.0),
                                    child: Padding(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16.0,
                                      ),
                                      child: PrimarySourceToolbar(
                                        viewModel: viewModel,
                                        primarySource: widget.primarySource,
                                        isBottom: true,
                                        dropdownWidth: dropdownWidth,
                                        screenContext: context,
                                      ),
                                    ),
                                  )
                                : null,
                            foregroundColor: colorScheme.primary,
                          ),
                    body: Column(
                      children: [
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.fromLTRB(
                              10.0,
                              0,
                              10.0,
                              0,
                            ),
                            child: Container(
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: colorScheme.onSurface,
                                  width: 1.0,
                                ),
                              ),
                              child: viewModel.isLoading
                                  ? Center(
                                      child: CircularProgressIndicator(
                                        color: colorScheme.primary,
                                      ),
                                    )
                                  : viewModel.imageData != null
                                  ? _buildSplitView(context, viewModel)
                                  : Center(
                                      child: Text(
                                        AppLocalizations.of(
                                          context,
                                        )!.image_not_loaded,
                                        style: textTheme.bodyMedium?.copyWith(
                                          color: colorScheme.onSurfaceVariant,
                                        ),
                                      ),
                                    ),
                            ),
                          ),
                        ),
                        if (widget.primarySource.attributes != null &&
                            widget.primarySource.attributes!.isNotEmpty &&
                            widget.primarySource.permissionsReceived)
                          Align(
                            alignment: Alignment.centerRight,
                            child: Padding(
                              padding: const EdgeInsets.fromLTRB(
                                10.0,
                                0,
                                10.0,
                                2.0,
                              ),
                              child: viewModel.selectAreaMode
                                  ? Text(
                                      AppLocalizations.of(
                                        context,
                                      )!.select_area_description,
                                      style: textTheme.bodySmall?.copyWith(
                                        fontSize: 10,
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                    )
                                  : viewModel.pipetteMode
                                  ? Text(
                                      AppLocalizations.of(
                                        context,
                                      )!.pick_color_description,
                                      style: textTheme.bodySmall?.copyWith(
                                        fontSize: 10,
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                    )
                                  : Text.rich(
                                      TextSpan(
                                        style: textTheme.bodySmall?.copyWith(
                                          fontSize: 10,
                                          color: colorScheme.onSurfaceVariant,
                                        ),
                                        children: [
                                          if (viewModel.isMobileWeb)
                                            TextSpan(
                                              text:
                                                  '⚠️ ${AppLocalizations.of(context)!.low_quality}; ',
                                              style: textTheme.bodySmall
                                                  ?.copyWith(
                                                    fontSize: 10,
                                                    color: colorScheme.primary,
                                                  ),
                                              recognizer: TapGestureRecognizer()
                                                ..onTap = () {
                                                  showCustomDialog(
                                                    MessageType.warningCommon,
                                                    param: AppLocalizations.of(
                                                      context,
                                                    )!.low_quality_message,
                                                  );
                                                },
                                            ),
                                          ..._buildLinkSpans(
                                            widget.primarySource.attributes!,
                                          ),
                                        ],
                                      ),
                                      maxLines: 5,
                                      softWrap: true,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                            ),
                          ),
                        if (widget.primarySource.attributes == null ||
                            widget.primarySource.attributes!.isEmpty ||
                            !widget.primarySource.permissionsReceived)
                          Text.rich(TextSpan(text: "")),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildImagePreview(PrimarySourceViewModel viewModel) {
    return ImagePreview(
      imageData: viewModel.imageData!,
      imageName: viewModel.imageName,
      controller: viewModel.imageController,
      isNegative: viewModel.isNegative,
      isMonochrome: viewModel.isMonochrome,
      brightness: viewModel.brightness,
      contrast: viewModel.contrast,
      replaceRegion: viewModel.selectedArea,
      colorToReplace: viewModel.colorToReplace,
      newColor: viewModel.newColor,
      tolerance: viewModel.tolerance,
      showWordSeparators: viewModel.showWordSeparators,
      showStrongNumbers: viewModel.showStrongNumbers,
      words: viewModel.selectedPage != null
          ? viewModel.selectedPage!.words
          : [],
    );
  }

  Widget _buildDescriptionView(
    BuildContext context,
    PrimarySourceViewModel viewModel,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final tooltipMaxWidth = screenWidth > 432 ? 420.0 : screenWidth - 12.0;

    final descriptionView = Container(
      color: colorScheme.surface,
      child: Stack(
        children: [
          Markdown(
            data: viewModel.descriptionContent ?? localizations.click_for_info,
            styleSheet: getMarkdownStyleSheet(theme, colorScheme),
            onTapLink: (text, href, title) {
              handleAppLink(
                context,
                href,
                onGreekStrongTap: viewModel.showInfoForStrongNumber,
                onGreekStrongPickerTap: (strongNumber, linkContext) {
                  _openStrongNumberPickerDialog(
                    linkContext,
                    viewModel,
                    strongNumber,
                  );
                },
              );
            },
          ),
          Positioned(
            top: -8,
            right: -8,
            child: Tooltip(
              key: _referenceTooltipKey,
              message: localizations.strong_reference_commentary,
              constraints: BoxConstraints(maxWidth: tooltipMaxWidth),
              showDuration: const Duration(seconds: 12),
              preferBelow: false,
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () {
                  _referenceTooltipKey.currentState?.ensureTooltipVisible();
                },
                child: SizedBox(
                  width: 32,
                  height: 32,
                  child: Center(
                    child: Icon(
                      Icons.info_outline,
                      size: 18,
                      color: colorScheme.primary,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );

    if (!_isMobileSwipeNavigationEnabled(viewModel)) {
      return descriptionView;
    }

    return GestureDetector(
      behavior: HitTestBehavior.translucent,
      onHorizontalDragEnd: (details) {
        _handleDescriptionSwipe(details, viewModel);
      },
      child: descriptionView,
    );
  }

  Future<void> _openStrongNumberPickerDialog(
    BuildContext dialogContext,
    PrimarySourceViewModel viewModel,
    int initialStrongNumber,
  ) async {
    final pickedStrongNumber = await showDialog<int>(
      context: dialogContext,
      routeSettings: const RouteSettings(name: 'strong_number_picker_dialog'),
      builder: (context) => StrongNumberPickerDialog(
        entries: viewModel.getGreekStrongPickerEntries(),
        initialStrongNumber: initialStrongNumber,
      ),
    );

    if (!mounted || pickedStrongNumber == null) {
      return;
    }

    viewModel.showInfoForStrongNumber(pickedStrongNumber, context);
  }

  Widget _buildSplitView(
    BuildContext context,
    PrimarySourceViewModel viewModel,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        final totalWidth = constraints.maxWidth;
        final totalHeight = constraints.maxHeight;
        final isLandscape =
            MediaQuery.of(context).orientation == Orientation.landscape;

        if (isLandscape) {
          final previewWidth = totalWidth * 2 / 3;
          final descriptionWidth = totalWidth * 1 / 3 - 10;
          return Row(
            children: [
              SizedBox(
                width: previewWidth,
                child: _buildImagePreview(viewModel),
              ),
              Container(width: 1, color: colorScheme.onSurface),
              SizedBox(
                width: descriptionWidth,
                child: _buildDescriptionView(context, viewModel),
              ),
            ],
          );
        } else {
          final previewHeight = totalHeight * 2 / 3;
          final descriptionHeight = totalHeight * 1 / 3 - 10;
          return Column(
            children: [
              SizedBox(
                height: previewHeight,
                child: _buildImagePreview(viewModel),
              ),
              Container(height: 1, color: colorScheme.onSurface),
              SizedBox(
                height: descriptionHeight,
                child: _buildDescriptionView(context, viewModel),
              ),
            ],
          );
        }
      },
    );
  }

  List<InlineSpan> _buildLinkSpans(List<Map<String, String>> links) {
    final theme = Theme.of(context);
    final ColorScheme colorScheme = theme.colorScheme;
    final TextStyle defaultStyle = Theme.of(context).textTheme.bodySmall!
        .copyWith(fontSize: 10, color: colorScheme.onSurfaceVariant);
    final List<InlineSpan> spans = [];
    for (int i = 0; i < links.length; i++) {
      final link = links[i];
      if (link['url'] != null && link['url']!.isNotEmpty) {
        spans.add(
          TextSpan(
            text: link['text'],
            style: defaultStyle.copyWith(color: colorScheme.primary),
            recognizer: TapGestureRecognizer()
              ..onTap = () {
                handleAppLink(context, link['url']);
              },
          ),
        );
      } else {
        spans.add(TextSpan(text: link['text'], style: defaultStyle));
      }
      if (i < links.length - 1) {
        spans.add(TextSpan(text: '; ', style: defaultStyle));
      }
    }
    return spans;
  }

  double calcPagesListWidth(BuildContext context) {
    final TextStyle itemStyle =
        Theme.of(context).textTheme.bodyMedium ?? TextStyle(fontSize: 16);

    double calculateTextWidth(String text) {
      return (TextPainter(
        text: TextSpan(text: text, style: itemStyle),
        textDirection: TextDirection.ltr,
        maxLines: 1,
      )..layout()).size.width;
    }

    double maxWidth;
    if (widget.primarySource.permissionsReceived &&
        widget.primarySource.pages.isNotEmpty) {
      maxWidth = widget.primarySource.pages
          .map((page) => calculateTextWidth("${page.name} (${page.content})"))
          .reduce((a, b) => a > b ? a : b);
    } else {
      maxWidth = calculateTextWidth(
        AppLocalizations.of(context)!.images_are_missing,
      );
    }
    return maxWidth + 40;
  }

  bool _isBottomToolbar(double screenWidth, double dropdownWidth) {
    const widthForTitle = 100;
    const double iconButtonWidth = 48.0;
    final double actionsWidth =
        dropdownWidth + PrimarySourceScreen.numButtons * iconButtonWidth;
    return actionsWidth > screenWidth - widthForTitle * 1 - 60;
  }

  bool _isMobileSwipeNavigationEnabled(PrimarySourceViewModel viewModel) {
    return isMobile() || viewModel.isMobileWeb;
  }

  void _handleDescriptionSwipe(
    DragEndDetails details,
    PrimarySourceViewModel viewModel,
  ) {
    if (!_isMobileSwipeNavigationEnabled(viewModel)) {
      return;
    }
    if (viewModel.selectAreaMode || viewModel.pipetteMode) {
      return;
    }

    final velocity = details.primaryVelocity;
    if (velocity == null || velocity.abs() < 250) {
      return;
    }

    final bool forward = velocity < 0;
    viewModel.navigateDescriptionSelection(context, forward: forward);
  }

  void _tryNavigateSelectedWord(
    PrimarySourceViewModel viewModel, {
    required bool forward,
  }) {
    if (!(isDesktop() || isWeb())) {
      return;
    }
    if (viewModel.selectAreaMode || viewModel.pipetteMode) {
      return;
    }
    if (viewModel.currentDescriptionType != DescriptionType.word) {
      return;
    }
    final words = viewModel.selectedPage?.words;
    if (words == null || words.isEmpty) {
      return;
    }
    final currentIndex = viewModel.currentDescriptionNumber;
    if (currentIndex == null ||
        currentIndex < 0 ||
        currentIndex >= words.length) {
      return;
    }

    final int nextIndex = forward
        ? (currentIndex + 1) % words.length
        : (currentIndex - 1 + words.length) % words.length;
    viewModel.showInfoForWord(nextIndex, context);
  }
}
