import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/repositories/pages_repository.dart';
import 'package:revelation/screens/primary_source/image_preview.dart';
import 'package:revelation/screens/primary_source/primary_source_toolbar.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

// Define the intent for exiting pipette or selectArea mode
class ExitChooseModeIntent extends Intent {
  const ExitChooseModeIntent();
}

class PrimarySourceScreen extends StatefulWidget {
  final PrimarySource primarySource;
  static final numButtons = 9;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  PrimarySourceScreenState createState() => PrimarySourceScreenState();
}

class PrimarySourceScreenState extends State<PrimarySourceScreen>
    with WidgetsBindingObserver {
  late PrimarySourceViewModel _viewModel;

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
          }

          final double screenWidth = MediaQuery.of(context).size.width;
          final bool isBottom = _isBottomToolbar(screenWidth, dropdownWidth);

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
              shortcuts: {
                const SingleActivator(LogicalKeyboardKey.escape):
                    const ExitChooseModeIntent(),
                const SingleActivator(LogicalKeyboardKey.backspace):
                    const ExitChooseModeIntent(),
              },
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
    );
  }

  Widget _buildDescriptionView(
    BuildContext context,
    PrimarySourceViewModel viewModel,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      color: colorScheme.surface,
      child: Markdown(
        data:
            viewModel.descriptionContent ??
            AppLocalizations.of(context)!.click_for_info,
        styleSheet: getMarkdownStyleSheet(theme, colorScheme),
      ),
    );
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
                launchLink(link['url']!);
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
}
