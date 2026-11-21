import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/allusion_search/presentation/widgets/allusion_passage_cards.dart';
import 'package:revelation/features/allusion_search/presentation/widgets/allusion_query_toolbar.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/features/topics/presentation/widgets/drawer_content.dart';
import 'package:revelation/l10n/app_localizations.dart';

class AllusionSearchScreen extends StatelessWidget {
  const AllusionSearchScreen({this.cubit, super.key});
  final AllusionSearchCubit? cubit;
  static const iconAssetPath = 'assets/images/UI/search_book.svg';

  @override
  Widget build(BuildContext context) => BlocProvider.value(
    value: cubit ?? AppDi.allusionSearchCubit,
    child: const _SearchPage(),
  );
}

class _SearchPage extends StatefulWidget {
  const _SearchPage();
  @override
  State<_SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<_SearchPage> {
  // PageStorage normally belongs to the route. Keep the scroll offset with
  // this session's search when the user returns through the main menu.
  static final _scrollBuckets = Expando<PageStorageBucket>();
  final _resultsHeading = GlobalKey();
  late final PageStorageBucket _bucket;
  @override
  void initState() {
    super.initState();
    final cubit = context.read<AllusionSearchCubit>();
    _bucket = _scrollBuckets[cubit] ??= PageStorageBucket();
    unawaited(cubit.beginVisit());
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) unawaited(cubit.prepareIndex());
    });
  }

  void _pageFromBottom(int page) {
    unawaited(context.read<AllusionSearchCubit>().setPage(page));
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final target = _resultsHeading.currentContext;
      if (target != null) unawaited(Scrollable.ensureVisible(target));
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final settings = AppDi.settingsCubitOrNull;
    final body = BlocBuilder<AllusionSearchCubit, AllusionSearchState>(
      builder: (context, state) {
        final cubit = context.read<AllusionSearchCubit>();
        final results = state.results;
        final searching = state.status == AllusionStatus.searching;
        return _AllusionWorkspace(
          state: state,
          results: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                key: _resultsHeading,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      l10n.allusion_candidates,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Flexible(
                    child: Text(
                      allusionScopeLabel(l10n, state.query.scope),
                      textAlign: TextAlign.end,
                      style: theme.textTheme.labelSmall,
                    ),
                  ),
                ],
              ),
              if (state.status == AllusionStatus.failure) ...[
                Text(l10n.allusion_failed),
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: TextButton(
                    onPressed: state.verseMap == null
                        ? cubit.ensureLoaded
                        : cubit.search,
                    child: Text(l10n.startup_retry),
                  ),
                ),
              ] else if (searching || state.status == AllusionStatus.loading)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (results == null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Text(l10n.allusion_search_hint),
                ),
              if (results != null && !searching) ...[
                DefaultTabController(
                  key: ValueKey(state.level),
                  initialIndex: state.level.index,
                  length: AllusionLevel.values.length,
                  child: TabBar(
                    isScrollable: true,
                    tabAlignment: TabAlignment.start,
                    labelPadding: const EdgeInsets.symmetric(horizontal: 12),
                    onTap: (i) =>
                        unawaited(cubit.setLevel(AllusionLevel.values[i])),
                    tabs: [
                      for (final level in AllusionLevel.values)
                        Tab(
                          key: ValueKey('allusion_tab_${level.name}'),
                          text:
                              '${_levelLabel(l10n, level)} ${results.forLevel(level).length}',
                        ),
                    ],
                  ),
                ),
                if (state.loadingText)
                  const LinearProgressIndicator(minHeight: 2),
                if (state.matches.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    child: Text(
                      results.sourceNumbers.isEmpty
                          ? l10n.allusion_no_source_words
                          : l10n.allusion_no_results,
                    ),
                  ),
                if (state.pageCount > 1)
                  _Pager(state: state, onPage: cubit.setPage, position: 'top'),
                for (final match in state.visible)
                  AllusionResultCard(
                    key: ValueKey((state.level, match.reference.verseKey)),
                    match: match,
                    state: state,
                  ),
                if (state.pageCount > 1)
                  _Pager(
                    state: state,
                    onPage: _pageFromBottom,
                    position: 'bottom',
                  ),
              ],
            ],
          ),
        );
      },
    );
    // Direct links start at this route. Keep the main menu reachable there too.
    final isEntryRoute = ModalRoute.of(context)?.isFirst ?? false;
    return Scaffold(
      drawer: isEntryRoute ? const AppNavigationDrawer() : null,
      appBar: AppBar(
        foregroundColor: theme.colorScheme.primary,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.allusion_search_screen,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 0.9,
              ),
            ),
            Text(
              l10n.allusion_search_header,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: PageStorage(
          bucket: _bucket,
          child: settings == null
              ? body
              : BlocListener<SettingsCubit, SettingsState>(
                  bloc: settings,
                  listenWhen: (a, b) =>
                      a.settings.defaultBibleModule !=
                          b.settings.defaultBibleModule ||
                      a.settings.selectedLanguage !=
                          b.settings.selectedLanguage,
                  listener: (context, state) => unawaited(
                    context.read<AllusionSearchCubit>().refreshTranslation(
                      preferenceChanged: true,
                    ),
                  ),
                  child: body,
                ),
        ),
      ),
    );
  }
}

class _AllusionWorkspace extends StatelessWidget {
  const _AllusionWorkspace({required this.state, required this.results});

  final AllusionSearchState state;
  final Widget results;

  @override
  Widget build(BuildContext context) {
    final scale = MediaQuery.textScalerOf(context).scale(14) / 14;
    // At the breakpoint the form has room for two filter rows and the
    // result cards retain at least 550 logical pixels at standard text size.
    final minScale = scale < 1 ? 1.0 : scale;
    return LayoutBuilder(
      builder: (context, constraints) {
        final split = constraints.maxWidth >= 1040 * minScale;
        final source = [
          if (state.verseMap != null) ...[
            AllusionQueryToolbar(state: state, inSidePanel: split),
            const SizedBox(height: 12),
            AllusionSourcePreview(state: state),
          ],
        ];
        const padding = EdgeInsets.fromLTRB(12, 14, 12, 16);
        if (!split) {
          return SingleChildScrollView(
            key: const PageStorageKey('allusion_search_scroll'),
            padding: padding,
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 900),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    ...source,
                    if (source.isNotEmpty) const SizedBox(height: 22),
                    results,
                  ],
                ),
              ),
            ),
          );
        }

        final width = constraints.maxWidth.clamp(0.0, 1680 * minScale);
        final sourceWidth = (width * 0.39).clamp(
          456 * minScale,
          600 * minScale,
        );
        return Center(
          child: SizedBox(
            width: width,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: sourceWidth,
                  child: SingleChildScrollView(
                    key: const PageStorageKey('allusion_source_scroll'),
                    primary: false,
                    padding: padding,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: source,
                    ),
                  ),
                ),
                const VerticalDivider(width: 1),
                Expanded(
                  child: SingleChildScrollView(
                    key: const PageStorageKey('allusion_results_scroll'),
                    primary: false,
                    padding: padding,
                    child: results,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

String _levelLabel(AppLocalizations l10n, AllusionLevel level) =>
    switch (level) {
      AllusionLevel.verse => l10n.allusion_verses,
      AllusionLevel.chapter => l10n.allusion_chapters,
      AllusionLevel.book => l10n.allusion_books,
    };

class _Pager extends StatelessWidget {
  const _Pager({
    required this.state,
    required this.onPage,
    required this.position,
  });
  final AllusionSearchState state;
  final ValueChanged<int> onPage;
  final String position;
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Wrap(
      alignment: WrapAlignment.end,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        IconButton(
          key: ValueKey('allusion_prev_$position'),
          tooltip: l10n.bible_search_previous_page,
          onPressed: state.page == 0 ? null : () => onPage(state.page - 1),
          icon: const Icon(Icons.chevron_left),
        ),
        Text(
          l10n.bible_search_page_label(state.page + 1, state.pageCount),
          style: Theme.of(context).textTheme.labelMedium,
        ),
        IconButton(
          key: ValueKey('allusion_next_$position'),
          tooltip: l10n.bible_search_next_page,
          onPressed: state.page + 1 >= state.pageCount
              ? null
              : () => onPage(state.page + 1),
          icon: const Icon(Icons.chevron_right),
        ),
      ],
    );
  }
}
