import 'dart:async';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_sources_state.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/source_item.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/core/platform/platform_utils.dart';

class PrimarySourcesScreen extends StatefulWidget {
  const PrimarySourcesScreen({super.key});

  @override
  State<PrimarySourcesScreen> createState() => _PrimarySourcesScreenState();
}

class _PrimarySourcesScreenState extends State<PrimarySourcesScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void initState() {
    super.initState();
    unawaited(context.read<PrimarySourcesCubit>().loadPrimarySources());
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final PrimarySourcesState state = context.select(
      (PrimarySourcesCubit cubit) => cubit.state,
    );
    final List<PrimarySource> fullSources = state.full;
    final List<PrimarySource> significantSources = state.significant;
    final List<PrimarySource> fragmentsSources = state.fragments;
    final bool isLoading = state.isLoading;
    final bool hasError = state.hasError;

    if (isLoading &&
        fullSources.isEmpty &&
        significantSources.isEmpty &&
        fragmentsSources.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: Text(AppLocalizations.of(context)!.primary_sources_screen),
          foregroundColor: colorScheme.primary,
        ),
        body: Center(
          child: CircularProgressIndicator(color: colorScheme.primary),
        ),
      );
    }
    if (!isLoading &&
        hasError &&
        fullSources.isEmpty &&
        significantSources.isEmpty &&
        fragmentsSources.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: Text(AppLocalizations.of(context)!.primary_sources_screen),
          foregroundColor: colorScheme.primary,
        ),
        body: Center(
          child: ErrorMessage(
            errorMessage: AppLocalizations.of(
              context,
            )!.error_loading_primary_sources,
          ),
        ),
      );
    }

    Widget content = CustomScrollView(
      controller: _scrollController,
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverAppBar(
          pinned: true,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                AppLocalizations.of(context)!.primary_sources_screen,
                style: textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  height: 0.9,
                ),
              ),
              Text(
                AppLocalizations.of(context)!.primary_sources_header,
                style: textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.normal,
                ),
              ),
            ],
          ),
          foregroundColor: colorScheme.primary,
        ),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) {
              if (index == 0) {
                final fullHeader =
                    "${AppLocalizations.of(context)!.full_primary_sources} (${fullSources.length})";
                return _buildSourceHeader(context, fullHeader);
              } else if (index - 1 < fullSources.length) {
                final fullSource = fullSources[index - 1];
                return _buildSourceItem(context, fullSource);
              } else if (index == fullSources.length + 1) {
                final significantHeader =
                    "${AppLocalizations.of(context)!.significant_primary_sources} (${significantSources.length})";
                return _buildSourceHeader(context, significantHeader);
              } else if (index - 2 <
                  fullSources.length + significantSources.length) {
                final significantSource =
                    significantSources[index - 2 - fullSources.length];
                return _buildSourceItem(context, significantSource);
              } else if (index ==
                  fullSources.length + significantSources.length + 2) {
                final fragmentsHeader =
                    "${AppLocalizations.of(context)!.fragments_primary_sources} (${fragmentsSources.length})";
                return _buildSourceHeader(context, fragmentsHeader);
              } else {
                final fragmentsSource =
                    fragmentsSources[index -
                        3 -
                        fullSources.length -
                        significantSources.length];
                return _buildSourceItem(context, fragmentsSource);
              }
            },
            childCount:
                3 +
                fullSources.length +
                significantSources.length +
                fragmentsSources.length,
          ),
        ),
      ],
    );

    if (isDesktop() || isWeb()) {
      content = Listener(
        onPointerDown: (event) {
          if (event.buttons == kPrimaryMouseButton) {
            setState(() {
              _isDragging = true;
              _lastOffset = event.position;
            });
          }
        },
        onPointerMove: (event) {
          if (_isDragging) {
            final dy = event.position.dy - _lastOffset.dy;
            final oldOffset = _scrollController.offset;
            final newOffset = oldOffset - dy;

            _scrollController.jumpTo(
              newOffset.clamp(0.0, _scrollController.position.maxScrollExtent),
            );
            setState(() {
              _lastOffset = event.position;
            });
          }
        },
        onPointerUp: (event) {
          if (event.buttons == 0) {
            setState(() {
              _isDragging = false;
            });
          }
        },
        child: content,
      );
    }

    return Scaffold(body: SizedBox.expand(child: content));
  }

  Widget _buildSourceHeader(BuildContext context, String header) {
    final theme = Theme.of(context);
    final textTheme = theme.textTheme;
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 0.0),
      child: Text(
        header,
        textAlign: TextAlign.center,
        style: textTheme.titleSmall?.copyWith(
          color: colorScheme.onSurfaceVariant,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildSourceItem(BuildContext context, PrimarySource source) {
    return SourceItemWidget(source: source);
  }
}
