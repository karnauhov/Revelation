import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_attributes_footer.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_description_panel.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_split_view.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/shared/ui/styled_text/styled_text_utils.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/primary_source_view_model.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';

// Define the intent for exiting pipette or selectArea mode
class ExitChooseModeIntent extends Intent {
  const ExitChooseModeIntent();
}

// Define the intent for moving to the next/previous selected description
class NavigateSelectedDescriptionIntent extends Intent {
  final bool forward;

  const NavigateSelectedDescriptionIntent({required this.forward});
}

class PrimarySourceScreen extends StatefulWidget {
  final PrimarySource primarySource;
  final String? initialPageName;
  final int? initialWordIndex;
  static final numButtons = 12;

  const PrimarySourceScreen({
    required this.primarySource,
    this.initialPageName,
    this.initialWordIndex,
    super.key,
  });

  @override
  PrimarySourceScreenState createState() => PrimarySourceScreenState();
}

class PrimarySourceScreenState extends State<PrimarySourceScreen>
    with WidgetsBindingObserver {
  PrimarySourceViewModel? _viewModel;
  final GlobalKey<TooltipState> _referenceTooltipKey =
      GlobalKey<TooltipState>();
  final PrimarySourceReferenceService _referenceResolver =
      PrimarySourceReferenceService();
  bool _initialReferenceApplied = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _viewModel?.dispose();
    _viewModel = null;
    super.dispose();
  }

  @override
  void didUpdateWidget(covariant PrimarySourceScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.primarySource != widget.primarySource) {
      _viewModel?.dispose();
      _viewModel = null;
      _initialReferenceApplied = false;
    }
  }

  @override
  void didChangeMetrics() {
    super.didChangeMetrics();
    final viewModel = _viewModel;
    if (viewModel != null && viewModel.isMenuOpen) {
      Navigator.of(context).pop();
      viewModel.setMenuOpen(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dropdownWidth = calcPagesListWidth(context);
    final theme = Theme.of(context);
    final TextTheme textTheme = theme.textTheme;
    final ColorScheme colorScheme = theme.colorScheme;

    final currentIsWeb = isWeb();
    return MultiBlocProvider(
      providers: [
        BlocProvider<PrimarySourceSessionCubit>(
          create: (_) =>
              PrimarySourceSessionCubit(source: widget.primarySource),
        ),
        BlocProvider<PrimarySourceImageCubit>(
          create: (_) => PrimarySourceImageCubit(
            source: widget.primarySource,
            isWeb: currentIsWeb,
            isMobileWeb: currentIsWeb && isMobileBrowser(),
          ),
        ),
        BlocProvider<PrimarySourcePageSettingsCubit>(
          create: (_) => PrimarySourcePageSettingsCubit(
            PrimarySourcePageSettingsOrchestrator(PagesRepository()),
          ),
        ),
        BlocProvider<PrimarySourceSelectionCubit>(
          create: (_) => PrimarySourceSelectionCubit(),
        ),
        BlocProvider<PrimarySourceDescriptionCubit>(
          create: (_) => PrimarySourceDescriptionCubit(),
        ),
        BlocProvider<PrimarySourceViewportCubit>(
          create: (_) => PrimarySourceViewportCubit(),
        ),
      ],
      child: Builder(
        builder: (context) {
          _watchPrimarySourceBlocStates(context);
          final viewModel = _ensureViewModel(context);
          _tryApplyInitialReference(viewModel);

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
          final bool allowDescriptionNavigationByArrows =
              (isDesktop() || isWeb()) &&
              _canNavigateDescriptionByArrow(viewModel);
          final shortcuts = <ShortcutActivator, Intent>{
            const SingleActivator(LogicalKeyboardKey.escape):
                const ExitChooseModeIntent(),
            const SingleActivator(LogicalKeyboardKey.backspace):
                const ExitChooseModeIntent(),
          };

          if (allowDescriptionNavigationByArrows) {
            shortcuts.addAll({
              const SingleActivator(LogicalKeyboardKey.arrowLeft):
                  const NavigateSelectedDescriptionIntent(forward: false),
              const SingleActivator(LogicalKeyboardKey.arrowUp):
                  const NavigateSelectedDescriptionIntent(forward: false),
              const SingleActivator(LogicalKeyboardKey.arrowRight):
                  const NavigateSelectedDescriptionIntent(forward: true),
              const SingleActivator(LogicalKeyboardKey.arrowDown):
                  const NavigateSelectedDescriptionIntent(forward: true),
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
                  NavigateSelectedDescriptionIntent:
                      CallbackAction<NavigateSelectedDescriptionIntent>(
                        onInvoke: (intent) {
                          _tryNavigateDescriptionByArrow(
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
                        PrimarySourceAttributesFooter(
                          attributes: widget.primarySource.attributes,
                          permissionsReceived:
                              widget.primarySource.permissionsReceived,
                          selectAreaMode: viewModel.selectAreaMode,
                          pipetteMode: viewModel.pipetteMode,
                          isMobileWeb: viewModel.isMobileWeb,
                        ),
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
      viewModel: viewModel,
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
      showVerseNumbers: viewModel.showVerseNumbers,
      words: viewModel.selectedPage != null
          ? viewModel.selectedPage!.words
          : [],
      verses: viewModel.selectedPage != null
          ? viewModel.selectedPage!.verses
          : [],
      selectedVerseIndex:
          viewModel.currentDescriptionType == DescriptionKind.verse
          ? viewModel.currentDescriptionNumber
          : null,
    );
  }

  Widget _buildDescriptionView(
    BuildContext context,
    PrimarySourceViewModel viewModel,
  ) {
    final bool showStrongInfoIcon =
        viewModel.currentDescriptionType == DescriptionKind.word ||
        viewModel.currentDescriptionType == DescriptionKind.strongNumber;
    final bool canNavigate =
        _canNavigateDescriptionByArrow(viewModel) &&
        !viewModel.selectAreaMode &&
        !viewModel.pipetteMode;
    return PrimarySourceDescriptionPanel(
      descriptionContent: viewModel.descriptionContent,
      onGreekStrongTap: viewModel.showInfoForStrongNumber,
      onGreekStrongPickerTap: (strongNumber, linkContext) {
        _openStrongNumberPickerDialog(linkContext, viewModel, strongNumber);
      },
      onWordTap: (sourceId, pageName, wordIndex, linkContext) {
        return _handleWordLinkTap(
          sourceId: sourceId,
          pageName: pageName,
          wordIndex: wordIndex,
          linkContext: linkContext,
          viewModel: viewModel,
        );
      },
      showStrongInfoIcon: showStrongInfoIcon,
      canNavigate: canNavigate,
      enableSwipeNavigation: _isMobileSwipeNavigationEnabled(viewModel),
      referenceTooltipKey: _referenceTooltipKey,
      onNavigateBackward: () {
        viewModel.navigateDescriptionSelection(context, forward: false);
      },
      onNavigateForward: () {
        viewModel.navigateDescriptionSelection(context, forward: true);
      },
      onHorizontalDragEnd: (details) {
        _handleDescriptionSwipe(details, viewModel);
      },
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

  void _tryApplyInitialReference(PrimarySourceViewModel viewModel) {
    if (_initialReferenceApplied) {
      return;
    }

    final normalizedPageName = widget.initialPageName?.trim();
    final hasPageName =
        normalizedPageName != null && normalizedPageName.isNotEmpty;
    final hasWordIndex = widget.initialWordIndex != null;
    if (!hasPageName && !hasWordIndex) {
      return;
    }
    _initialReferenceApplied = true;

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) {
        return;
      }
      await _openReferenceInCurrentSource(
        viewModel: viewModel,
        linkContext: context,
        pageName: normalizedPageName,
        wordIndex: widget.initialWordIndex,
        navigateToFirstPageWhenPageMissing: false,
      );
    });
  }

  Future<void> _handleWordLinkTap({
    required String sourceId,
    required String? pageName,
    required int? wordIndex,
    required BuildContext linkContext,
    required PrimarySourceViewModel viewModel,
  }) async {
    final normalizedSourceId = sourceId.trim();
    final normalizedPageName = pageName?.trim();
    final shouldOpenFirstPage =
        normalizedPageName == null || normalizedPageName.isEmpty;

    if (normalizedSourceId.isEmpty) {
      log.warning("Empty source id in word link.");
      return;
    }

    if (normalizedSourceId == widget.primarySource.id) {
      await _openReferenceInCurrentSource(
        viewModel: viewModel,
        linkContext: linkContext,
        pageName: normalizedPageName,
        wordIndex: wordIndex,
        navigateToFirstPageWhenPageMissing: shouldOpenFirstPage,
      );
      return;
    }

    final targetSource = _findPrimarySourceById(normalizedSourceId);
    if (targetSource == null) {
      log.warning("Primary source '$normalizedSourceId' was not found.");
      return;
    }

    if (!mounted) {
      return;
    }
    linkContext.push(
      '/primary_source',
      extra: PrimarySourceRouteArgs(
        primarySource: targetSource,
        pageName: normalizedPageName,
        wordIndex: wordIndex,
      ),
    );
  }

  Future<void> _openReferenceInCurrentSource({
    required PrimarySourceViewModel viewModel,
    required BuildContext linkContext,
    String? pageName,
    int? wordIndex,
    required bool navigateToFirstPageWhenPageMissing,
  }) async {
    if (pageName != null && pageName.isNotEmpty) {
      model.Page? targetPage;
      for (final page in widget.primarySource.pages) {
        if (page.name == pageName) {
          targetPage = page;
          break;
        }
      }
      if (targetPage == null) {
        log.warning(
          "Page '$pageName' was not found in source '${widget.primarySource.id}'.",
        );
        return;
      }
      if (viewModel.selectedPage != targetPage) {
        await viewModel.changeSelectedPage(targetPage);
      }
    } else if (navigateToFirstPageWhenPageMissing &&
        widget.primarySource.pages.isNotEmpty) {
      final firstPage = widget.primarySource.pages.first;
      if (viewModel.selectedPage != firstPage) {
        await viewModel.changeSelectedPage(firstPage);
      }
    }

    if (wordIndex == null) {
      return;
    }

    if (wordIndex < 0) {
      log.warning("Wrong word index in word link: '$wordIndex'.");
      return;
    }

    if (!linkContext.mounted) {
      return;
    }
    viewModel.showInfoForWord(wordIndex, linkContext);
  }

  PrimarySource? _findPrimarySourceById(String sourceId) {
    return _referenceResolver.findSourceById(sourceId);
  }

  Widget _buildSplitView(
    BuildContext context,
    PrimarySourceViewModel viewModel,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    return PrimarySourceSplitView(
      imagePreview: _buildImagePreview(viewModel),
      descriptionPanel: _buildDescriptionView(context, viewModel),
      dividerColor: colorScheme.onSurface,
    );
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

  bool _canNavigateDescriptionByArrow(PrimarySourceViewModel viewModel) {
    if (viewModel.currentDescriptionNumber == null) {
      return false;
    }

    if (viewModel.currentDescriptionType == DescriptionKind.word) {
      return viewModel.selectedPage?.words.isNotEmpty ?? false;
    }

    if (viewModel.currentDescriptionType == DescriptionKind.strongNumber) {
      return true;
    }

    if (viewModel.currentDescriptionType == DescriptionKind.verse) {
      return viewModel.selectedPage?.verses.isNotEmpty ?? false;
    }

    return false;
  }

  void _tryNavigateDescriptionByArrow(
    PrimarySourceViewModel viewModel, {
    required bool forward,
  }) {
    if (!(isDesktop() || isWeb())) {
      return;
    }
    if (viewModel.selectAreaMode || viewModel.pipetteMode) {
      return;
    }
    if (!_canNavigateDescriptionByArrow(viewModel)) {
      return;
    }
    viewModel.navigateDescriptionSelection(context, forward: forward);
  }

  PrimarySourceViewModel _ensureViewModel(BuildContext context) {
    final current = _viewModel;
    if (current != null) {
      return current;
    }

    final created = PrimarySourceViewModel(
      PagesRepository(),
      primarySource: widget.primarySource,
      imageCubit: context.read<PrimarySourceImageCubit>(),
      pageSettingsCubit: context.read<PrimarySourcePageSettingsCubit>(),
      selectionCubit: context.read<PrimarySourceSelectionCubit>(),
      descriptionCubit: context.read<PrimarySourceDescriptionCubit>(),
      viewportCubit: context.read<PrimarySourceViewportCubit>(),
      sessionCubit: context.read<PrimarySourceSessionCubit>(),
    );
    _viewModel = created;
    return created;
  }

  void _watchPrimarySourceBlocStates(BuildContext context) {
    context.select((PrimarySourceSessionCubit cubit) => cubit.state);
    context.select((PrimarySourceImageCubit cubit) => cubit.state);
    context.select((PrimarySourcePageSettingsCubit cubit) => cubit.state);
    context.select((PrimarySourceSelectionCubit cubit) => cubit.state);
    context.select((PrimarySourceDescriptionCubit cubit) => cubit.state);
    context.select((PrimarySourceViewportCubit cubit) => cubit.state);
  }
}
