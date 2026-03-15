@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_description_panel.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_split_view.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'PrimarySourceSplitView uses row in landscape and column in portrait',
    (tester) async {
      await tester.pumpWidget(
        _buildMediaQueryHost(
          size: const Size(900, 500),
          child: const PrimarySourceSplitView(
            imagePreview: SizedBox(),
            descriptionPanel: SizedBox(),
            dividerColor: Colors.black,
          ),
        ),
      );

      expect(
        find.byKey(const Key('primary_source_split_view_row')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('primary_source_split_view_column')),
        findsNothing,
      );

      await tester.pumpWidget(
        _buildMediaQueryHost(
          size: const Size(500, 900),
          child: const PrimarySourceSplitView(
            imagePreview: SizedBox(),
            descriptionPanel: SizedBox(),
            dividerColor: Colors.black,
          ),
        ),
      );

      expect(
        find.byKey(const Key('primary_source_split_view_row')),
        findsNothing,
      );
      expect(
        find.byKey(const Key('primary_source_split_view_column')),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'PrimarySourceDescriptionPanel triggers navigation callbacks when enabled',
    (tester) async {
      int backwardTaps = 0;
      int forwardTaps = 0;
      int dragEndCalls = 0;

      await tester.pumpWidget(
        _buildApp(
          child: PrimarySourceDescriptionPanel(
            descriptionContent: 'Example',
            onGreekStrongTap: (_, __) {},
            onGreekStrongPickerTap: (_, __) {},
            onWordTap: (_, __, ___, ____) async {},
            showStrongInfoIcon: true,
            canNavigate: true,
            enableSwipeNavigation: true,
            referenceTooltipKey: GlobalKey<TooltipState>(),
            onNavigateBackward: () {
              backwardTaps++;
            },
            onNavigateForward: () {
              forwardTaps++;
            },
            onHorizontalDragEnd: (_) {
              dragEndCalls++;
            },
          ),
        ),
      );

      expect(find.byIcon(Icons.info_outline), findsOneWidget);

      await tester.tap(
        find.byKey(const Key('description_nav_back')),
        warnIfMissed: false,
      );
      await tester.tap(
        find.byKey(const Key('description_nav_forward')),
        warnIfMissed: false,
      );
      await tester.pump();

      expect(backwardTaps, 1);
      expect(forwardTaps, 1);

      await tester.drag(
        find.byKey(const Key('description_panel_swipe_zone')),
        const Offset(-120, 0),
      );
      await tester.pump();
      expect(dragEndCalls, 1);
    },
  );

  testWidgets(
    'PrimarySourceDescriptionPanel blocks navigation callbacks when disabled',
    (tester) async {
      int taps = 0;

      await tester.pumpWidget(
        _buildApp(
          child: PrimarySourceDescriptionPanel(
            descriptionContent: 'Example',
            onGreekStrongTap: (_, __) {},
            onGreekStrongPickerTap: (_, __) {},
            onWordTap: (_, __, ___, ____) async {},
            showStrongInfoIcon: false,
            canNavigate: false,
            enableSwipeNavigation: false,
            referenceTooltipKey: GlobalKey<TooltipState>(),
            onNavigateBackward: () {
              taps++;
            },
            onNavigateForward: () {
              taps++;
            },
            onHorizontalDragEnd: (_) {},
          ),
        ),
      );

      await tester.tap(
        find.byKey(const Key('description_nav_back')),
        warnIfMissed: false,
      );
      await tester.tap(
        find.byKey(const Key('description_nav_forward')),
        warnIfMissed: false,
      );
      await tester.pump();

      expect(taps, 0);
      expect(find.byIcon(Icons.info_outline), findsNothing);
    },
  );

  testWidgets(
    'PrimarySourceToolbar shows overflow menu button on constrained width',
    (tester) async {
      final bundle = _createToolbarVmBundle();
      addTearDown(bundle.dispose);

      await tester.pumpWidget(
        _buildApp(
          child: Builder(
            builder: (context) {
              return SizedBox(
                width: 800,
                child: PrimarySourceToolbar(
                  primarySource: bundle.primarySource,
                  selectedPage: bundle.viewModel.selectedPage,
                  localPageLoaded: bundle.viewModel.localPageLoaded,
                  refreshError: bundle.viewModel.refreshError,
                  isNegative: bundle.viewModel.isNegative,
                  isMonochrome: bundle.viewModel.isMonochrome,
                  brightness: bundle.viewModel.brightness,
                  contrast: bundle.viewModel.contrast,
                  selectedArea: bundle.viewModel.selectedArea,
                  tolerance: bundle.viewModel.tolerance,
                  showWordSeparators: bundle.viewModel.showWordSeparators,
                  showStrongNumbers: bundle.viewModel.showStrongNumbers,
                  showVerseNumbers: bundle.viewModel.showVerseNumbers,
                  zoomStatusNotifier: bundle.viewModel.zoomStatusNotifier,
                  imageController: bundle.viewModel.imageController,
                  isBottom: true,
                  dropdownWidth: 760,
                  onChangeSelectedPage: bundle.viewModel.changeSelectedPage,
                  onShowCommonInfo: () {},
                  onReloadImage: () async {},
                  onToggleNegative: bundle.viewModel.toggleNegative,
                  onToggleMonochrome: bundle.viewModel.toggleMonochrome,
                  onToggleShowWordSeparators:
                      bundle.viewModel.toggleShowWordSeparators,
                  onToggleShowStrongNumbers:
                      bundle.viewModel.toggleShowStrongNumbers,
                  onToggleShowVerseNumbers:
                      bundle.viewModel.toggleShowVerseNumbers,
                  onRemovePageSettings: bundle.viewModel.removePageSettings,
                  onOpenBrightnessContrastDialog: () {},
                  onOpenReplaceColorDialog: () {},
                  onSetMenuOpen: bundle.viewModel.setMenuOpen,
                ),
              );
            },
          ),
        ),
      );

      expect(find.byIcon(Icons.more_vert), findsOneWidget);
    },
  );
}

Widget _buildApp({required Widget child}) {
  return buildLocalizedTestApp(child: child);
}

Widget _buildMediaQueryHost({required Size size, required Widget child}) {
  return Directionality(
    textDirection: TextDirection.ltr,
    child: MediaQuery(
      data: MediaQueryData(size: size),
      child: Material(
        child: SizedBox(width: size.width, height: size.height, child: child),
      ),
    ),
  );
}

class _ToolbarVmBundle {
  final PrimarySource source;
  final PrimarySourceDetailCoordinator viewModel;
  final List<BlocBase<Object?>> cubits;

  _ToolbarVmBundle({
    required this.source,
    required this.viewModel,
    required this.cubits,
  });

  PrimarySource get primarySource => source;

  Future<void> dispose() async {
    viewModel.dispose();
    for (final cubit in cubits) {
      await cubit.close();
    }
  }
}

_ToolbarVmBundle _createToolbarVmBundle() {
  final source = _buildPrimarySource();
  final imageCubit = PrimarySourceImageCubit(
    source: source,
    isWeb: false,
    isMobileWeb: false,
    autoInitialize: false,
  );
  final pageSettingsCubit = PrimarySourcePageSettingsCubit(
    PrimarySourcePageSettingsOrchestrator(PagesRepository()),
  );
  final descriptionCubit = PrimarySourceDescriptionCubit();
  final viewportCubit = PrimarySourceViewportCubit();
  final sessionCubit = PrimarySourceSessionCubit(source: source);

  final viewModel = PrimarySourceDetailCoordinator(
    PagesRepository(),
    primarySource: source,
    imageCubit: imageCubit,
    pageSettingsCubit: pageSettingsCubit,
    descriptionCubit: descriptionCubit,
    viewportCubit: viewportCubit,
    sessionCubit: sessionCubit,
  );

  return _ToolbarVmBundle(
    source: source,
    viewModel: viewModel,
    cubits: [
      imageCubit,
      pageSettingsCubit,
      descriptionCubit,
      viewportCubit,
      sessionCubit,
    ],
  );
}

PrimarySource _buildPrimarySource() {
  return PrimarySource(
    id: 'toolbar-test-source',
    title: 'Toolbar Test Source',
    date: '',
    content: '',
    quantity: 1,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1.0,
    isMonochrome: false,
    pages: const <model.Page>[],
    attributes: const <Map<String, String>>[],
    permissionsReceived: false,
  );
}
