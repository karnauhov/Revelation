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
import 'package:revelation/features/primary_sources/presentation/widgets/brightness_contrast_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/replace_color_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/shared/ui/styled_text/styled_text_utils.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart';
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
  PrimarySourceDetailCoordinator? _viewModel;
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
            viewModel.showCommonInfo(AppLocalizations.of(context)!);
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
                                    _buildToolbar(
                                      viewModel: viewModel,
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
                                      child: _buildToolbar(
                                        viewModel: viewModel,
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
                              child: Builder(
                                builder: (contentContext) {
                                  final contentSlice = contentContext.select((
                                    PrimarySourceImageCubit cubit,
                                  ) {
                                    final state = cubit.state;
                                    return (
                                      isLoading: state.isLoading,
                                      hasImage: state.imageData != null,
                                    );
                                  });
                                  if (contentSlice.isLoading) {
                                    return Center(
                                      child: CircularProgressIndicator(
                                        color: colorScheme.primary,
                                      ),
                                    );
                                  }
                                  if (contentSlice.hasImage) {
                                    return _buildSplitView(
                                      contentContext,
                                      viewModel,
                                    );
                                  }
                                  return Center(
                                    child: Text(
                                      AppLocalizations.of(
                                        contentContext,
                                      )!.image_not_loaded,
                                      style: textTheme.bodyMedium?.copyWith(
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                    ),
                                  );
                                },
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

  Widget _buildImagePreview(PrimarySourceDetailCoordinator viewModel) {
    return Builder(
      builder: (previewContext) {
        final imageData = previewContext.select(
          (PrimarySourceImageCubit cubit) => cubit.state.imageData,
        );
        if (imageData == null) {
          return const SizedBox.shrink();
        }

        final imageName = previewContext.select(
          (PrimarySourceSessionCubit cubit) => cubit.state.imageName,
        );
        final selectedPage = previewContext.select(
          (PrimarySourceSessionCubit cubit) => cubit.state.selectedPage,
        );
        final pageSettingsSlice = previewContext.select((
          PrimarySourcePageSettingsCubit cubit,
        ) {
          final state = cubit.state;
          return (
            isNegative: state.isNegative,
            isMonochrome: state.isMonochrome,
            brightness: state.brightness,
            contrast: state.contrast,
            showWordSeparators: state.showWordSeparators,
            showStrongNumbers: state.showStrongNumbers,
            showVerseNumbers: state.showVerseNumbers,
          );
        });
        final viewportSlice = previewContext.select((
          PrimarySourceViewportCubit cubit,
        ) {
          final state = cubit.state;
          return (
            pipetteMode: state.pipetteMode,
            selectAreaMode: state.selectAreaMode,
            selectedArea: state.selectedArea,
            colorToReplace: state.colorToReplace,
            newColor: state.newColor,
            tolerance: state.tolerance,
          );
        });
        final descriptionSlice = previewContext.select((
          PrimarySourceDescriptionCubit cubit,
        ) {
          final state = cubit.state;
          return (
            currentType: state.currentType,
            currentNumber: state.currentNumber,
          );
        });

        return ImagePreview(
          imageData: imageData,
          imageName: imageName,
          controller: viewModel.imageController,
          pipetteMode: viewportSlice.pipetteMode,
          selectAreaMode: viewportSlice.selectAreaMode,
          isNegative: pageSettingsSlice.isNegative,
          isMonochrome: pageSettingsSlice.isMonochrome,
          brightness: pageSettingsSlice.brightness,
          contrast: pageSettingsSlice.contrast,
          replaceRegion: viewportSlice.selectedArea,
          colorToReplace: viewportSlice.colorToReplace,
          newColor: viewportSlice.newColor,
          tolerance: viewportSlice.tolerance,
          showWordSeparators: pageSettingsSlice.showWordSeparators,
          showStrongNumbers: pageSettingsSlice.showStrongNumbers,
          showVerseNumbers: pageSettingsSlice.showVerseNumbers,
          currentDescriptionType: descriptionSlice.currentType,
          currentDescriptionNumber: descriptionSlice.currentNumber,
          onFinishSelectAreaMode: viewModel.finishSelectAreaMode,
          onFinishPipetteMode: viewModel.finishPipetteMode,
          onWordTap: (wordIndex) {
            viewModel.showInfoForWord(
              wordIndex,
              AppLocalizations.of(previewContext)!,
            );
          },
          onVerseTap: (verseIndex) {
            viewModel.showInfoForVerse(
              verseIndex,
              AppLocalizations.of(previewContext)!,
            );
          },
          onStrongNumberTap: (strongNumber) {
            viewModel.showInfoForStrongNumber(
              strongNumber,
              AppLocalizations.of(previewContext)!,
            );
          },
          onRestorePositionAndScale: viewModel.restorePositionAndScale,
          words: selectedPage?.words ?? const [],
          verses: selectedPage?.verses ?? const [],
          selectedVerseIndex:
              descriptionSlice.currentType == DescriptionKind.verse
              ? descriptionSlice.currentNumber
              : null,
        );
      },
    );
  }

  Widget _buildDescriptionView(
    BuildContext context,
    PrimarySourceDetailCoordinator viewModel,
  ) {
    return Builder(
      builder: (descriptionContext) {
        final selectedPage = descriptionContext.select(
          (PrimarySourceSessionCubit cubit) => cubit.state.selectedPage,
        );
        final descriptionSlice = descriptionContext.select((
          PrimarySourceDescriptionCubit cubit,
        ) {
          final state = cubit.state;
          return (
            content: state.content,
            currentType: state.currentType,
            currentNumber: state.currentNumber,
          );
        });
        final modeSlice = descriptionContext.select((
          PrimarySourceViewportCubit cubit,
        ) {
          final state = cubit.state;
          return (
            selectAreaMode: state.selectAreaMode,
            pipetteMode: state.pipetteMode,
          );
        });

        final bool showStrongInfoIcon =
            descriptionSlice.currentType == DescriptionKind.word ||
            descriptionSlice.currentType == DescriptionKind.strongNumber;
        final bool canNavigate =
            _canNavigateDescription(
              currentType: descriptionSlice.currentType,
              currentNumber: descriptionSlice.currentNumber,
              selectedPage: selectedPage,
            ) &&
            !modeSlice.selectAreaMode &&
            !modeSlice.pipetteMode;

        return PrimarySourceDescriptionPanel(
          descriptionContent: descriptionSlice.content,
          onGreekStrongTap: (strongNumber, linkContext) {
            viewModel.showInfoForStrongNumber(
              strongNumber,
              AppLocalizations.of(linkContext)!,
            );
          },
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
            viewModel.navigateDescriptionSelection(
              AppLocalizations.of(descriptionContext)!,
              forward: false,
            );
          },
          onNavigateForward: () {
            viewModel.navigateDescriptionSelection(
              AppLocalizations.of(descriptionContext)!,
              forward: true,
            );
          },
          onHorizontalDragEnd: (details) {
            _handleDescriptionSwipe(details, viewModel);
          },
        );
      },
    );
  }

  Future<void> _openStrongNumberPickerDialog(
    BuildContext dialogContext,
    PrimarySourceDetailCoordinator viewModel,
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

    viewModel.showInfoForStrongNumber(
      pickedStrongNumber,
      AppLocalizations.of(context)!,
    );
  }

  void _tryApplyInitialReference(PrimarySourceDetailCoordinator viewModel) {
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
    required PrimarySourceDetailCoordinator viewModel,
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
    required PrimarySourceDetailCoordinator viewModel,
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
    viewModel.showInfoForWord(wordIndex, AppLocalizations.of(linkContext)!);
  }

  PrimarySource? _findPrimarySourceById(String sourceId) {
    return _referenceResolver.findSourceById(sourceId);
  }

  Widget _buildSplitView(
    BuildContext context,
    PrimarySourceDetailCoordinator viewModel,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    return PrimarySourceSplitView(
      imagePreview: _buildImagePreview(viewModel),
      descriptionPanel: _buildDescriptionView(context, viewModel),
      dividerColor: colorScheme.onSurface,
    );
  }

  Widget _buildToolbar({
    required PrimarySourceDetailCoordinator viewModel,
    required bool isBottom,
    required double dropdownWidth,
    required BuildContext screenContext,
  }) {
    return Builder(
      builder: (toolbarContext) {
        final selectedPage = toolbarContext.select(
          (PrimarySourceSessionCubit cubit) => cubit.state.selectedPage,
        );
        final imageSlice = toolbarContext.select((
          PrimarySourceImageCubit cubit,
        ) {
          final state = cubit.state;
          return (
            localPageLoaded: state.localPageLoaded,
            refreshError: state.refreshError,
          );
        });
        final settingsSlice = toolbarContext.select((
          PrimarySourcePageSettingsCubit cubit,
        ) {
          final state = cubit.state;
          return (
            isNegative: state.isNegative,
            isMonochrome: state.isMonochrome,
            brightness: state.brightness,
            contrast: state.contrast,
            showWordSeparators: state.showWordSeparators,
            showStrongNumbers: state.showStrongNumbers,
            showVerseNumbers: state.showVerseNumbers,
          );
        });
        final viewportSlice = toolbarContext.select((
          PrimarySourceViewportCubit cubit,
        ) {
          final state = cubit.state;
          return (selectedArea: state.selectedArea, tolerance: state.tolerance);
        });

        return PrimarySourceToolbar(
          primarySource: widget.primarySource,
          selectedPage: selectedPage,
          localPageLoaded: imageSlice.localPageLoaded,
          refreshError: imageSlice.refreshError,
          isNegative: settingsSlice.isNegative,
          isMonochrome: settingsSlice.isMonochrome,
          brightness: settingsSlice.brightness,
          contrast: settingsSlice.contrast,
          selectedArea: viewportSlice.selectedArea,
          tolerance: viewportSlice.tolerance,
          showWordSeparators: settingsSlice.showWordSeparators,
          showStrongNumbers: settingsSlice.showStrongNumbers,
          showVerseNumbers: settingsSlice.showVerseNumbers,
          zoomStatusNotifier: viewModel.zoomStatusNotifier,
          imageController: viewModel.imageController,
          isBottom: isBottom,
          dropdownWidth: dropdownWidth,
          onChangeSelectedPage: viewModel.changeSelectedPage,
          onShowCommonInfo: () {
            viewModel.showCommonInfo(AppLocalizations.of(screenContext)!);
          },
          onReloadImage: () async {
            if (selectedPage == null) {
              return;
            }
            await viewModel.loadImage(selectedPage.image, isReload: true);
          },
          onToggleNegative: viewModel.toggleNegative,
          onToggleMonochrome: viewModel.toggleMonochrome,
          onToggleShowWordSeparators: viewModel.toggleShowWordSeparators,
          onToggleShowStrongNumbers: viewModel.toggleShowStrongNumbers,
          onToggleShowVerseNumbers: viewModel.toggleShowVerseNumbers,
          onRemovePageSettings: viewModel.removePageSettings,
          onOpenBrightnessContrastDialog: () {
            _openBrightnessContrastDialog(viewModel, screenContext);
          },
          onOpenReplaceColorDialog: () {
            _openReplaceColorDialog(viewModel, screenContext);
          },
          onSetMenuOpen: viewModel.setMenuOpen,
        );
      },
    );
  }

  Future<void> _openBrightnessContrastDialog(
    PrimarySourceDetailCoordinator viewModel,
    BuildContext screenContext,
  ) {
    return showDialog(
      context: screenContext,
      routeSettings: RouteSettings(name: 'brightness_contrast_dialog'),
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

  Future<void> _openReplaceColorDialog(
    PrimarySourceDetailCoordinator viewModel,
    BuildContext screenContext,
  ) {
    return showDialog(
      context: screenContext,
      routeSettings: RouteSettings(name: 'replace_color_dialog'),
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
                  parentContext: screenContext,
                  onApply: (selectedArea, colorToReplace, newColor, tolerance) {
                    viewModel.applyColorReplacement(
                      selectedArea,
                      colorToReplace,
                      newColor,
                      tolerance,
                    );
                  },
                  onCancel: viewModel.resetColorReplacement,
                  onStartSelectAreaMode: viewModel.startSelectAreaMode,
                  onStartPipetteMode: viewModel.startPipetteMode,
                  readSelectedArea: () => viewModel.selectedArea,
                  readColorToReplace: () => viewModel.colorToReplace,
                  readNewColor: () => viewModel.newColor,
                  readTolerance: () => viewModel.tolerance,
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

  bool _isMobileSwipeNavigationEnabled(
    PrimarySourceDetailCoordinator viewModel,
  ) {
    return isMobile() || viewModel.isMobileWeb;
  }

  void _handleDescriptionSwipe(
    DragEndDetails details,
    PrimarySourceDetailCoordinator viewModel,
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
    viewModel.navigateDescriptionSelection(
      AppLocalizations.of(context)!,
      forward: forward,
    );
  }

  bool _canNavigateDescriptionByArrow(
    PrimarySourceDetailCoordinator viewModel,
  ) {
    return _canNavigateDescription(
      currentType: viewModel.currentDescriptionType,
      currentNumber: viewModel.currentDescriptionNumber,
      selectedPage: viewModel.selectedPage,
    );
  }

  bool _canNavigateDescription({
    required DescriptionKind currentType,
    required int? currentNumber,
    required model.Page? selectedPage,
  }) {
    if (currentNumber == null) {
      return false;
    }

    if (currentType == DescriptionKind.word) {
      return selectedPage?.words.isNotEmpty ?? false;
    }

    if (currentType == DescriptionKind.strongNumber) {
      return true;
    }

    if (currentType == DescriptionKind.verse) {
      return selectedPage?.verses.isNotEmpty ?? false;
    }

    return false;
  }

  void _tryNavigateDescriptionByArrow(
    PrimarySourceDetailCoordinator viewModel, {
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
    viewModel.navigateDescriptionSelection(
      AppLocalizations.of(context)!,
      forward: forward,
    );
  }

  PrimarySourceDetailCoordinator _ensureViewModel(BuildContext context) {
    final current = _viewModel;
    if (current != null) {
      return current;
    }

    final created = PrimarySourceDetailCoordinator(
      PagesRepository(),
      primarySource: widget.primarySource,
      imageCubit: context.read<PrimarySourceImageCubit>(),
      pageSettingsCubit: context.read<PrimarySourcePageSettingsCubit>(),
      descriptionCubit: context.read<PrimarySourceDescriptionCubit>(),
      viewportCubit: context.read<PrimarySourceViewportCubit>(),
      sessionCubit: context.read<PrimarySourceSessionCubit>(),
    );
    _viewModel = created;
    return created;
  }

  void _watchPrimarySourceBlocStates(BuildContext context) {
    context.select(
      (PrimarySourceSessionCubit cubit) => cubit.state.selectedPage,
    );
    context.select((PrimarySourceDescriptionCubit cubit) {
      final state = cubit.state;
      return (
        currentType: state.currentType,
        currentNumber: state.currentNumber,
      );
    });
    context.select((PrimarySourceViewportCubit cubit) {
      final state = cubit.state;
      return (state.pipetteMode, state.selectAreaMode);
    });
  }
}
