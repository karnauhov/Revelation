import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/screens/primary_source/image_preview.dart';
import 'package:revelation/screens/primary_source/primary_source_toolbar.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';

// Define the intent for exiting pipette or selectArea mode
class ExitChooseModeIntent extends Intent {
  const ExitChooseModeIntent();
}

class PrimarySourceScreen extends StatelessWidget {
  final PrimarySource primarySource;
  static final numButtons = 8;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  Widget build(BuildContext context) {
    final dropdownWidth = calcPagesListWidth(context);
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
                              style: Theme.of(context)
                                  .textTheme
                                  .headlineSmall
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          )
                        : viewModel.pipetteMode
                            ? AppBar(
                                title: Text(
                                  AppLocalizations.of(context)!
                                      .pick_color_header,
                                  style: Theme.of(context)
                                      .textTheme
                                      .headlineSmall
                                      ?.copyWith(fontWeight: FontWeight.bold),
                                ),
                              )
                            : AppBar(
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
                                          screenContext: context,
                                        ),
                                      ],
                                bottom: isBottom
                                    ? PreferredSize(
                                        preferredSize:
                                            const Size.fromHeight(32.0),
                                        child: Padding(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 16.0),
                                          child: PrimarySourceToolbar(
                                            viewModel: viewModel,
                                            primarySource: primarySource,
                                            isBottom: true,
                                            dropdownWidth: dropdownWidth,
                                            screenContext: context,
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
                                border:
                                    Border.all(color: Colors.black, width: 1.0),
                              ),
                              child: viewModel.isLoading
                                  ? const Center(
                                      child: CircularProgressIndicator())
                                  : viewModel.imageData != null
                                      ? ImagePreview(
                                          imageData: viewModel.imageData!,
                                          imageName: viewModel.imageName,
                                          controller: viewModel.imageController,
                                          isNegative: viewModel.isNegative,
                                          isMonochrome: viewModel.isMonochrome,
                                          brightness: viewModel.brightness,
                                          contrast: viewModel.contrast,
                                          replaceRegion:
                                              Rect.fromLTRB(100, 100, 300, 300),
                                          colorToReplace:
                                              viewModel.colorToReplace,
                                          newColor: viewModel.newColor,
                                          tolerance: viewModel.tolerance,
                                        )
                                      : Center(
                                          child: Text(
                                              AppLocalizations.of(context)!
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
                              child: viewModel.selectAreaMode
                                  ? Text(
                                      AppLocalizations.of(context)!
                                          .select_area_description,
                                      style: theme.bodySmall!
                                          .copyWith(fontSize: 10),
                                    )
                                  : viewModel.pipetteMode
                                      ? Text(
                                          AppLocalizations.of(context)!
                                              .pick_color_description,
                                          style: theme.bodySmall!
                                              .copyWith(fontSize: 10),
                                        )
                                      : Text.rich(
                                          TextSpan(
                                            style: theme.bodySmall!
                                                .copyWith(fontSize: 10),
                                            children: [
                                              if (viewModel.isMobileWeb)
                                                TextSpan(
                                                  text:
                                                      '⚠️ ${AppLocalizations.of(context)!.low_quality}; ',
                                                  style: const TextStyle(
                                                      color: Colors.blue),
                                                  recognizer:
                                                      TapGestureRecognizer()
                                                        ..onTap = () {
                                                          showCustomDialog(
                                                              MessageType
                                                                  .warningCommon,
                                                              param: AppLocalizations
                                                                      .of(context)!
                                                                  .low_quality_message);
                                                        },
                                                ),
                                              ..._buildLinkSpans(
                                                  primarySource.attributes!),
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
                  ),
                ),
              ),
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

  double calcPagesListWidth(BuildContext context) {
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
