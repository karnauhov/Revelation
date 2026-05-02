@Tags(['widget'])
import 'dart:async';
import 'dart:io';

import 'package:audioplayers_platform_interface/audioplayers_platform_interface.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_source_screen.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/brightness_contrast_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/image_preview.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_description_panel.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/replace_color_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_rect.dart';
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';
import 'package:revelation/shared/models/verse.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const pathProviderChannel = MethodChannel('plugins.flutter.io/path_provider');

  late AudioplayersPlatformInterface originalAudioPlatform;
  late GlobalAudioplayersPlatformInterface originalGlobalAudioPlatform;
  late _FakeAudioplayersPlatform fakeAudioPlatform;
  late _FakeGlobalAudioplayersPlatform fakeGlobalAudioPlatform;
  late PathProviderPlatform previousPathProvider;
  Directory? tempDir;
  String? documentsPathForTest;

  setUpAll(() {
    originalAudioPlatform = AudioplayersPlatformInterface.instance;
    originalGlobalAudioPlatform = GlobalAudioplayersPlatformInterface.instance;
    fakeAudioPlatform = _FakeAudioplayersPlatform();
    fakeGlobalAudioPlatform = _FakeGlobalAudioplayersPlatform();
    AudioplayersPlatformInterface.instance = fakeAudioPlatform;
    GlobalAudioplayersPlatformInterface.instance = fakeGlobalAudioPlatform;
  });

  tearDownAll(() async {
    AudioplayersPlatformInterface.instance = originalAudioPlatform;
    GlobalAudioplayersPlatformInterface.instance = originalGlobalAudioPlatform;
    await fakeGlobalAudioPlatform.dispose();
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    SharedPreferences.setMockInitialValues(<String, Object>{});
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp(
      'primary_source_screen_test_',
    );
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir!.path);
    documentsPathForTest = tempDir!.path;
    debugDefaultTargetPlatformOverride = null;
    AudioController.resetForTest();
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(pathProviderChannel, (call) async {
          if (call.method == 'getApplicationDocumentsDirectory') {
            return tempDir!.path;
          }
          return null;
        });
  });

  tearDown(() async {
    debugDefaultTargetPlatformOverride = null;
    PathProviderPlatform.instance = previousPathProvider;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(pathProviderChannel, null);
    final dir = tempDir;
    if (dir != null && await dir.exists()) {
      try {
        await dir.delete(recursive: true);
      } on PathAccessException {
        await Future<void>.delayed(const Duration(milliseconds: 50));
        if (await dir.exists()) {
          try {
            await dir.delete(recursive: true);
          } on PathAccessException {
            // Windows can briefly keep image files open after decode; do not
            // fail behavioral tests on best-effort temp cleanup.
          }
        }
      }
    }
    tempDir = null;
    documentsPathForTest = null;
    AudioController.resetForTest();
    await GetIt.I.reset();
  });

  testWidgets('shows image placeholder when no image is loaded', (
    tester,
  ) async {
    await _prepareSurface(tester);
    addTearDown(_suppressOverflowErrors());
    final source = _buildSourceWithoutImages();

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: PrimarySourceScreen(primarySource: source),
        withScaffold: false,
      ),
    );
    await tester.pump();

    final context = _screenContext(tester);
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.image_not_loaded), findsOneWidget);
    expect(find.text(l10n.images_are_missing), findsOneWidget);
  });

  testWidgets(
    'calcPagesListWidth follows source data and toolbar moves to bottom when width is constrained',
    (tester) async {
      await _prepareSurface(tester, size: const Size(3200, 900));
      addTearDown(_suppressOverflowErrors());

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(
            primarySource: _buildSourceWithoutImages(),
          ),
          withScaffold: false,
        ),
      );
      await tester.pump();

      final placeholderState = _screenState(tester);
      final placeholderWidth = placeholderState.calcPagesListWidth(
        _screenContext(tester),
      );
      final wideSource = _buildRichSource(id: 'source-wide', title: 'Wide');
      await _seedLocalImagesInTest(tester, wideSource, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: wideSource),
          withScaffold: false,
        ),
      );
      await _pumpUntilFound(tester, find.byType(PrimarySourceToolbar));

      final longSource = _buildRichSource(
        id: 'source-long',
        title: 'Source with long pages',
        pageNames: const [
          'The longest page name in the widget test suite',
          'B',
        ],
      );
      await _seedLocalImagesInTest(tester, longSource, documentsPathForTest!);
      await _prepareSurface(tester, size: const Size(650, 900));

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: longSource),
          withScaffold: false,
        ),
      );
      await _pumpUntilFound(tester, find.byType(PrimarySourceToolbar));

      final loadedState = _screenState(tester);
      final richWidth = loadedState.calcPagesListWidth(_screenContext(tester));
      final narrowAppBar = tester.widget<AppBar>(find.byType(AppBar));

      expect(richWidth, greaterThan(placeholderWidth));
      expect(narrowAppBar.bottom, isNotNull);
    },
  );

  testWidgets(
    'initial page reference is applied once and reset when the source changes',
    (tester) async {
      await _prepareSurface(tester);
      addTearDown(_suppressOverflowErrors());
      final widgetKey = GlobalKey();
      final firstSource = _buildRichSource(
        id: 'source-a',
        title: 'Source A',
        pageNames: const ['P1', 'P2'],
      );
      final carriedPage = firstSource.pages.last;
      final secondSource = PrimarySource(
        id: 'source-b',
        title: 'Source B',
        date: '',
        content: '',
        quantity: 2,
        material: '',
        textStyle: '',
        found: '',
        classification: '',
        currentLocation: '',
        preview: '',
        maxScale: 5,
        isMonochrome: false,
        pages: <model.Page>[
          carriedPage,
          _buildPage(
            name: 'P3',
            content: 'Content C',
            image: 'folder/source-b_3.png',
            firstWordStrong: 5,
            secondWordStrong: 6,
            verseNumber: 3,
          ),
        ],
        attributes: const <Map<String, String>>[],
        permissionsReceived: true,
      );
      await _seedLocalImagesInTest(tester, firstSource, documentsPathForTest!);
      await _seedLocalImagesInTest(tester, secondSource, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(
            key: widgetKey,
            primarySource: firstSource,
            initialPageName: '  P2  ',
          ),
          withScaffold: false,
        ),
      );
      await _pumpUntilPageSelected(tester, 'P2');

      expect(_sessionCubit(tester).state.selectedPage?.name, 'P2');

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(
            key: widgetKey,
            primarySource: secondSource,
            initialPageName: ' P3 ',
          ),
          withScaffold: false,
        ),
      );
      await _pumpUntilPageSelected(tester, 'P3');

      expect(_sessionCubit(tester).state.selectedPage?.name, 'P3');
    },
  );

  testWidgets(
    'loaded screen executes toolbar callbacks and dialog mode transitions',
    (tester) async {
      await _prepareSurface(tester);
      addTearDown(_suppressOverflowErrors());
      final source = _buildRichSource(id: 'source-dialogs', title: 'Dialogs');
      await _seedLocalImagesInTest(tester, source, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: source),
          withScaffold: false,
        ),
      );
      await _forceLoadFirstPageImage(tester, source);
      await _pumpUntilFound(tester, find.byType(ImagePreview));

      final l10n = AppLocalizations.of(_screenContext(tester))!;
      final pageSettingsCubit = _pageSettingsCubit(tester);
      final viewportCubit = _viewportCubit(tester);

      pageSettingsCubit.applyBrightnessContrast(20, 135);
      viewportCubit.applyColorReplacement(
        selectedArea: const Rect.fromLTWH(5, 6, 30, 20),
        colorToReplace: const Color(0xFF111111),
        newColor: const Color(0xFF222222),
        tolerance: 27,
      );
      await tester.pump();

      _toolbar(tester).onOpenBrightnessContrastDialog();
      await _pumpUntilFound(tester, find.byType(BrightnessContrastDialog));

      await tester.tap(find.text(l10n.reset));
      await _pumpUntilGone(tester, find.byType(BrightnessContrastDialog));
      expect(pageSettingsCubit.state.brightness, 0);
      expect(pageSettingsCubit.state.contrast, 100);

      _toolbar(tester).onOpenReplaceColorDialog();
      await _pumpUntilFound(tester, find.byType(ReplaceColorDialog));

      await tester.tap(find.byTooltip(l10n.area_selection));
      await tester.pump();
      await _pumpUntil(
        tester,
        () => viewportCubit.state.selectAreaMode,
        reason: 'Select-area mode was not activated.',
      );

      expect(find.text(l10n.select_area_header), findsOneWidget);
      expect(_popScope(tester).canPop, isFalse);

      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pump();
      await _pumpUntilFound(tester, find.byType(ReplaceColorDialog));

      expect(viewportCubit.state.selectAreaMode, isFalse);

      await tester.tap(find.byTooltip(l10n.eyedropper).first);
      await tester.pump();
      await _pumpUntil(
        tester,
        () => viewportCubit.state.pipetteMode,
        reason: 'Pipette mode was not activated.',
      );

      expect(find.text(l10n.pick_color_header), findsOneWidget);
      expect(_popScope(tester).canPop, isFalse);

      await tester.sendKeyEvent(LogicalKeyboardKey.backspace);
      await tester.pump();
      await _pumpUntilFound(tester, find.byType(ReplaceColorDialog));

      expect(viewportCubit.state.pipetteMode, isFalse);

      await tester.tap(find.text(l10n.reset).last);
      await _pumpUntilGone(tester, find.byType(ReplaceColorDialog));

      expect(viewportCubit.state.selectedArea, isNull);
      expect(viewportCubit.state.tolerance, 0);
    },
  );

  testWidgets(
    'description panel callbacks enforce in-source link and picker contracts',
    (tester) async {
      await _prepareSurface(tester);
      addTearDown(_suppressOverflowErrors());
      final source = _buildRichSource(
        id: 'source-links',
        title: 'Links',
        pageNames: const ['P1', 'P2'],
      );
      await _seedLocalImagesInTest(tester, source, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: source),
          withScaffold: false,
        ),
      );
      await _forceLoadFirstPageImage(tester, source);
      await _pumpUntilFound(tester, find.byType(PrimarySourceDescriptionPanel));

      expect(_descriptionPanel(tester).descriptionActionsEnabled, isFalse);
      expect(_descriptionPanel(tester).exportPdfDocumentTitle, isNull);

      final sessionCubit = _sessionCubit(tester);
      final descriptionCubit = _descriptionCubit(tester);
      final panelContext = tester.element(
        find.byType(PrimarySourceDescriptionPanel),
      );
      final l10n = AppLocalizations.of(panelContext)!;

      await _invokeWordTap(
        tester,
        _descriptionPanel(tester),
        sourceId: source.id,
        pageName: ' P2 ',
        wordIndex: 1,
        context: panelContext,
      );
      await _pumpUntilPageSelected(tester, 'P2');
      await tester.pump();

      expect(sessionCubit.state.selectedPage?.name, 'P2');
      descriptionCubit.updateDescriptionContent(
        content: 'word description',
        type: DescriptionKind.word,
        number: 1,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).descriptionActionsEnabled, isTrue);
      expect(
        _descriptionPanel(tester).exportPdfDocumentTitle,
        'source-links_P2_word_1',
      );

      await _invokeWordTap(
        tester,
        _descriptionPanel(tester),
        sourceId: '   ',
        pageName: 'P1',
        wordIndex: 0,
        context: panelContext,
      );
      await tester.pump();
      expect(sessionCubit.state.selectedPage?.name, 'P2');

      await _invokeWordTap(
        tester,
        _descriptionPanel(tester),
        sourceId: source.id,
        pageName: 'Missing',
        wordIndex: 0,
        context: panelContext,
      );
      await tester.pump();
      expect(sessionCubit.state.selectedPage?.name, 'P2');

      sessionCubit.setSelectedPage(source.pages.last);
      await tester.pump();
      await _invokeWordTap(
        tester,
        _descriptionPanel(tester),
        sourceId: source.id,
        pageName: null,
        wordIndex: null,
        context: panelContext,
      );
      await _pumpUntilPageSelected(tester, 'P1');

      descriptionCubit.updateDescriptionContent(
        content: 'word description',
        type: DescriptionKind.word,
        number: 0,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).showStrongInfoIcon, isTrue);
      expect(_descriptionPanel(tester).canNavigate, isTrue);
      expect(_descriptionPanel(tester).descriptionActionsEnabled, isTrue);
      expect(
        _descriptionPanel(tester).exportPdfDocumentTitle,
        'source-links_P1_word_0',
      );

      descriptionCubit.updateDescriptionContent(
        content: 'strong description',
        type: DescriptionKind.strongNumber,
        number: 25,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).descriptionActionsEnabled, isTrue);
      expect(_descriptionPanel(tester).exportPdfDocumentTitle, 'G25');

      descriptionCubit.updateDescriptionContent(
        content: 'word description',
        type: DescriptionKind.word,
        number: 0,
      );
      await tester.pump();

      _descriptionPanel(tester).onGreekStrongPickerTap(1, panelContext);
      await _pumpUntilFound(tester, find.byType(StrongNumberPickerDialog));
      await _closeStrongPickerDialog(tester, l10n);

      await tester.runAsync(() async {
        final result = _descriptionPanel(tester).onWordsTap!(
          const <PrimarySourceWordLinkTarget>[
            PrimarySourceWordLinkTarget(
              sourceId: 'missing-source',
              pageName: 'P1',
              wordIndex: 0,
            ),
          ],
          panelContext,
        );
        if (result is Future<void>) {
          unawaited(result);
        }
      });
      await _pumpUntilFound(tester, find.byType(AlertDialog));
      await _pumpUntilFound(
        tester,
        find.text(l10n.primary_source_word_source_unavailable),
      );
      await tester.tap(find.text(l10n.close).last);
      await _pumpUntilGone(tester, find.byType(AlertDialog));

      descriptionCubit.updateDescriptionContent(
        content: 'verse description',
        type: DescriptionKind.verse,
        number: 0,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).showStrongInfoIcon, isFalse);
      expect(_descriptionPanel(tester).canNavigate, isTrue);
      expect(_descriptionPanel(tester).descriptionActionsEnabled, isTrue);
      expect(
        _descriptionPanel(tester).exportPdfDocumentTitle,
        'source-links_Rev_1.1',
      );
    },
  );

  testWidgets(
    'mobile swipe path and lifecycle handlers keep contracts stable',
    (tester) async {
      await _prepareSurface(tester);
      addTearDown(_suppressOverflowErrors());
      final source = _buildRichSource(id: 'source-mobile', title: 'Mobile');
      await _seedLocalImagesInTest(tester, source, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: source),
          withScaffold: false,
        ),
      );
      await _forceLoadFirstPageImage(tester, source);
      await _pumpUntilFound(tester, find.byType(PrimarySourceDescriptionPanel));

      final state = _screenState(tester);
      final sessionCubit = _sessionCubit(tester);
      final descriptionCubit = _descriptionCubit(tester);
      final viewportCubit = _viewportCubit(tester);
      final context = _screenContext(tester);
      final l10n = AppLocalizations.of(context)!;

      descriptionCubit.updateDescriptionContent(
        content: 'word description',
        type: DescriptionKind.word,
        number: 0,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).enableSwipeNavigation, isTrue);
      expect(_descriptionPanel(tester).canNavigate, isTrue);

      _descriptionPanel(tester).onHorizontalDragEnd(
        DragEndDetails(
          primaryVelocity: -100,
          velocity: Velocity(pixelsPerSecond: Offset(-100, 0)),
        ),
      );
      await tester.pump();
      expect(descriptionCubit.state.content, 'word description');

      viewportCubit.startPipetteMode(isColorToReplace: true);
      await tester.pump();
      expect(_descriptionPanel(tester).canNavigate, isFalse);
      expect(_popScope(tester).canPop, isFalse);
      _popScope(tester).onPopInvokedWithResult?.call(false, null);
      await tester.pump();
      expect(viewportCubit.state.pipetteMode, isFalse);

      viewportCubit.startSelectAreaMode();
      await tester.pump();
      expect(_popScope(tester).canPop, isFalse);
      _popScope(tester).onPopInvokedWithResult?.call(false, null);
      await tester.pump();
      expect(viewportCubit.state.selectAreaMode, isFalse);

      unawaited(
        showDialog<void>(
          context: context,
          builder: (_) => const AlertDialog(content: Text('metrics dialog')),
        ),
      );
      await tester.pump();
      expect(find.text('metrics dialog'), findsOneWidget);

      sessionCubit.setMenuOpen(true);
      state.didChangeMetrics();
      await tester.pump();
      await _pumpUntilGone(tester, find.text('metrics dialog'));

      expect(sessionCubit.state.isMenuOpen, isFalse);

      sessionCubit.setSelectedPage(_buildAlienPage());
      await tester.pump();
      await _pumpUntil(
        tester,
        () =>
            sessionCubit.state.selectedPage == source.pages.first &&
            descriptionCubit.state.content == l10n.click_for_info,
        reason: 'Invalid selected page was not corrected.',
      );
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );

  testWidgets(
    'desktop shortcuts gate description navigation by screen state',
    (tester) async {
      await _prepareSurface(tester);
      addTearDown(_suppressOverflowErrors());
      final source = _buildRichSource(id: 'source-desktop', title: 'Desktop');
      await _seedLocalImagesInTest(tester, source, documentsPathForTest!);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceScreen(primarySource: source),
          withScaffold: false,
        ),
      );
      await _forceLoadFirstPageImage(tester, source);
      await _pumpUntilFound(tester, find.byType(PrimarySourceDescriptionPanel));

      final descriptionCubit = _descriptionCubit(tester);
      final viewportCubit = _viewportCubit(tester);

      descriptionCubit.updateDescriptionContent(
        content: 'desktop description',
        type: DescriptionKind.word,
        number: 0,
      );
      await tester.pump();

      expect(_descriptionPanel(tester).enableSwipeNavigation, isFalse);
      expect(_descriptionPanel(tester).canNavigate, isTrue);

      await tester.sendKeyEvent(LogicalKeyboardKey.arrowRight);
      await tester.pump();
      await tester.sendKeyEvent(LogicalKeyboardKey.arrowLeft);
      await tester.pump();

      viewportCubit.startSelectAreaMode();
      await tester.pump();
      await tester.sendKeyEvent(LogicalKeyboardKey.arrowRight);
      await tester.pump();

      expect(viewportCubit.state.selectAreaMode, isTrue);
      expect(find.byType(PrimarySourceScreen), findsOneWidget);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );
}

Future<void> _prepareSurface(
  WidgetTester tester, {
  Size size = const Size(1400, 900),
}) async {
  await tester.binding.setSurfaceSize(size);
  addTearDown(() {
    tester.binding.setSurfaceSize(null);
  });
}

Future<void> _pumpUntil(
  WidgetTester tester,
  bool Function() condition, {
  required String reason,
  int maxFrames = 80,
  Duration step = const Duration(milliseconds: 50),
}) async {
  for (var i = 0; i < maxFrames; i++) {
    await tester.pump(step);
    if (condition()) {
      return;
    }
  }
  fail(reason);
}

Future<void> _pumpUntilFound(
  WidgetTester tester,
  Finder finder, {
  int maxFrames = 80,
}) {
  return _pumpUntil(
    tester,
    () => finder.evaluate().isNotEmpty,
    reason: 'Expected finder to appear: $finder',
    maxFrames: maxFrames,
  );
}

Future<void> _pumpUntilGone(
  WidgetTester tester,
  Finder finder, {
  int maxFrames = 80,
}) {
  return _pumpUntil(
    tester,
    () => finder.evaluate().isEmpty,
    reason: 'Expected finder to disappear: $finder',
    maxFrames: maxFrames,
  );
}

Future<void> _pumpUntilPageSelected(WidgetTester tester, String pageName) {
  return _pumpUntil(
    tester,
    () => _sessionCubit(tester).state.selectedPage?.name == pageName,
    reason: 'Expected selected page to become $pageName.',
  );
}

Future<void> _seedLocalImagesInTest(
  WidgetTester tester,
  PrimarySource source,
  String documentsPath,
) async {
  await tester.runAsync(() => _seedLocalImages(source, documentsPath));
}

Future<void> _forceLoadFirstPageImage(
  WidgetTester tester,
  PrimarySource source,
) async {
  await tester.runAsync(
    () => _imageCubit(tester).loadImage(
      page: source.pages.first.image,
      sourceHashCode: source.hashCode,
    ),
  );
  await tester.pump();
}

Future<void> _invokeWordTap(
  WidgetTester tester,
  PrimarySourceDescriptionPanel panel, {
  required String sourceId,
  required String? pageName,
  required int? wordIndex,
  required BuildContext context,
}) async {
  await tester.runAsync(
    () async => panel.onWordTap(sourceId, pageName, wordIndex, context),
  );
}

Future<void> _closeStrongPickerDialog(
  WidgetTester tester,
  AppLocalizations l10n,
) async {
  if (find.text(l10n.close).evaluate().isNotEmpty) {
    await tester.tap(find.text(l10n.close).last);
  } else {
    await tester.tap(find.text(l10n.cancel).last);
  }
  await tester.pump();
  await _pumpUntilGone(tester, find.byType(StrongNumberPickerDialog));
}

VoidCallback _suppressOverflowErrors() {
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('A RenderFlex overflowed by')) {
      return;
    }
    if (originalHandler != null) {
      originalHandler(details);
    }
  };

  return () {
    FlutterError.onError = originalHandler;
  };
}

BuildContext _screenContext(WidgetTester tester) {
  return tester.element(find.byType(PrimarySourceScreen));
}

BuildContext _blocContext(WidgetTester tester) {
  return tester.element(find.byType(Scaffold).first);
}

PrimarySourceScreenState _screenState(WidgetTester tester) {
  return tester.state<PrimarySourceScreenState>(
    find.byType(PrimarySourceScreen),
  );
}

PrimarySourceSessionCubit _sessionCubit(WidgetTester tester) {
  return BlocProvider.of<PrimarySourceSessionCubit>(_blocContext(tester));
}

PrimarySourceDescriptionCubit _descriptionCubit(WidgetTester tester) {
  return BlocProvider.of<PrimarySourceDescriptionCubit>(_blocContext(tester));
}

PrimarySourceImageCubit _imageCubit(WidgetTester tester) {
  return BlocProvider.of<PrimarySourceImageCubit>(_blocContext(tester));
}

PrimarySourceViewportCubit _viewportCubit(WidgetTester tester) {
  return BlocProvider.of<PrimarySourceViewportCubit>(_blocContext(tester));
}

PrimarySourcePageSettingsCubit _pageSettingsCubit(WidgetTester tester) {
  return BlocProvider.of<PrimarySourcePageSettingsCubit>(_blocContext(tester));
}

PrimarySourceToolbar _toolbar(WidgetTester tester) {
  return tester.widget<PrimarySourceToolbar>(find.byType(PrimarySourceToolbar));
}

PrimarySourceDescriptionPanel _descriptionPanel(WidgetTester tester) {
  return tester.widget<PrimarySourceDescriptionPanel>(
    find.byType(PrimarySourceDescriptionPanel),
  );
}

PopScope<Object?> _popScope(WidgetTester tester) {
  final finder = find.byWidgetPredicate((widget) => widget is PopScope);
  return tester.widget(finder) as PopScope<Object?>;
}

Future<void> _seedLocalImages(
  PrimarySource source,
  String documentsPath,
) async {
  final appFolder = Directory('$documentsPath/revelation');
  await appFolder.create(recursive: true);

  for (final page in source.pages) {
    final file = File('${appFolder.path}/${page.image}');
    await file.create(recursive: true);
    await file.writeAsBytes(_png1x1);
  }
}

PrimarySource _buildSourceWithoutImages() {
  return PrimarySource(
    id: 'source-1',
    title: 'Source title',
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    attributes: const [],
    permissionsReceived: false,
  );
}

PrimarySource _buildRichSource({
  required String id,
  required String title,
  List<String> pageNames = const ['P1', 'P2'],
}) {
  final firstPageName = pageNames[0];
  final secondPageName = pageNames[1];

  return PrimarySource(
    id: id,
    title: title,
    date: '',
    content: '',
    quantity: 2,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 5,
    isMonochrome: false,
    pages: <model.Page>[
      _buildPage(
        name: firstPageName,
        content: 'Content A',
        image: 'folder/${id}_1.png',
        firstWordStrong: 1,
        secondWordStrong: 2,
        verseNumber: 1,
      ),
      _buildPage(
        name: secondPageName,
        content: 'Content B',
        image: 'folder/${id}_2.png',
        firstWordStrong: 3,
        secondWordStrong: 4,
        verseNumber: 2,
      ),
    ],
    attributes: const <Map<String, String>>[],
    permissionsReceived: true,
  );
}

model.Page _buildPage({
  required String name,
  required String content,
  required String image,
  required int firstWordStrong,
  required int secondWordStrong,
  required int verseNumber,
}) {
  return model.Page(
    name: name,
    content: content,
    image: image,
    words: <PageWord>[
      PageWord('Word-1', <PageRect>[
        PageRect(0.1, 0.1, 0.2, 0.2),
      ], sn: firstWordStrong),
      PageWord('Word-2', <PageRect>[
        PageRect(0.25, 0.1, 0.35, 0.2),
      ], sn: secondWordStrong),
    ],
    verses: <Verse>[
      Verse(
        chapterNumber: 1,
        verseNumber: verseNumber,
        labelPosition: const Offset(0.1, 0.1),
        wordIndexes: const <int>[0, 1],
      ),
    ],
  );
}

model.Page _buildAlienPage() {
  return model.Page(
    name: 'Alien',
    content: 'Detached',
    image: 'folder/alien.png',
    words: const <PageWord>[],
    verses: const <Verse>[],
  );
}

final Uint8List _png1x1 = _loadSolidPng(16, 16, const Color(0xFFFFFFFF));

class _FakeAudioplayersPlatform extends AudioplayersPlatformInterface {
  final Map<String, StreamController<AudioEvent>> _controllers =
      <String, StreamController<AudioEvent>>{};

  @override
  Future<void> create(String playerId) async {
    _controllers[playerId] = StreamController<AudioEvent>.broadcast();
  }

  @override
  Stream<AudioEvent> getEventStream(String playerId) {
    return _controllers[playerId]?.stream ?? const Stream<AudioEvent>.empty();
  }

  @override
  Future<void> dispose(String playerId) async {
    await _controllers.remove(playerId)?.close();
  }

  @override
  Future<void> pause(String playerId) async {}

  @override
  Future<void> stop(String playerId) async {}

  @override
  Future<void> resume(String playerId) async {}

  @override
  Future<void> release(String playerId) async {}

  @override
  Future<void> seek(String playerId, Duration position) async {
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.seekComplete),
    );
  }

  @override
  Future<void> setBalance(String playerId, double balance) async {}

  @override
  Future<void> setVolume(String playerId, double volume) async {}

  @override
  Future<void> setReleaseMode(String playerId, ReleaseMode releaseMode) async {}

  @override
  Future<void> setPlaybackRate(String playerId, double playbackRate) async {}

  @override
  Future<void> setSourceUrl(
    String playerId,
    String url, {
    bool? isLocal,
    String? mimeType,
  }) async {
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.prepared, isPrepared: true),
    );
  }

  @override
  Future<void> setSourceBytes(
    String playerId,
    Uint8List bytes, {
    String? mimeType,
  }) async {
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.prepared, isPrepared: true),
    );
  }

  @override
  Future<void> setAudioContext(
    String playerId,
    AudioContext audioContext,
  ) async {}

  @override
  Future<void> setPlayerMode(String playerId, PlayerMode playerMode) async {}

  @override
  Future<int?> getDuration(String playerId) async => null;

  @override
  Future<int?> getCurrentPosition(String playerId) async => null;

  @override
  Future<void> emitLog(String playerId, String message) async {}

  @override
  Future<void> emitError(String playerId, String code, String message) async {}
}

class _FakeGlobalAudioplayersPlatform
    implements GlobalAudioplayersPlatformInterface {
  final StreamController<GlobalAudioEvent> _controller =
      StreamController<GlobalAudioEvent>.broadcast();

  @override
  Stream<GlobalAudioEvent> getGlobalEventStream() => _controller.stream;

  @override
  Future<void> init() async {}

  @override
  Future<void> setGlobalAudioContext(AudioContext ctx) async {}

  @override
  Future<void> emitGlobalLog(String message) async {}

  @override
  Future<void> emitGlobalError(String code, String message) async {}

  Future<void> dispose() async {
    await _controller.close();
  }
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}

Uint8List _loadSolidPng(int width, int height, Color color) {
  final image = img.Image(width: width, height: height);
  final pixel = img.ColorRgba8(
    (color.r * 255).round(),
    (color.g * 255).round(),
    (color.b * 255).round(),
    (color.a * 255).round(),
  );
  img.fill(image, color: pixel);
  return Uint8List.fromList(img.encodePng(image));
}
