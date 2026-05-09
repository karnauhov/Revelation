import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'drawer_item.dart';

class DrawerContent extends StatefulWidget {
  final VoidCallback onItemClicked;
  const DrawerContent({super.key, required this.onItemClicked});

  @visibleForTesting
  static bool Function() isWebForTest = isWeb;

  @visibleForTesting
  static bool Function() isDesktopForTest = isDesktop;

  @visibleForTesting
  static Future<bool> Function() closeDesktopWindowForTest = closeDesktopWindow;

  @visibleForTesting
  static void resetPlatformTestOverrides() {
    isWebForTest = isWeb;
    isDesktopForTest = isDesktop;
    closeDesktopWindowForTest = closeDesktopWindow;
  }

  @override
  // ignore: library_private_types_in_public_api
  _DrawerContentState createState() => _DrawerContentState();
}

class _DrawerContentState extends State<DrawerContent> {
  final ScrollController _scrollController = ScrollController();
  bool _isDragging = false;
  Offset _lastDragPosition = Offset.zero;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onDragStart(DragStartDetails details) {
    setState(() {
      _isDragging = true;
      _lastDragPosition = details.globalPosition;
    });
  }

  void _onDragUpdate(DragUpdateDetails details) {
    if (_isDragging) {
      final dy = details.globalPosition.dy - _lastDragPosition.dy;
      _scrollController.jumpTo(_scrollController.offset - dy);
      setState(() {
        _lastDragPosition = details.globalPosition;
      });
    }
  }

  void _onDragEnd(DragEndDetails details) {
    setState(() {
      _isDragging = false;
    });
  }

  void _openRoute(BuildContext context, String route) {
    widget.onItemClicked();
    Navigator.pop(context);
    context.push(route);
  }

  DrawerItem _buildNavigationItem({
    required String assetPath,
    required String text,
    required String route,
  }) {
    return DrawerItem(
      assetPath: assetPath,
      text: text,
      onClick: () => _openRoute(context, route),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final dividerColor = colorScheme.onSurface.withValues(alpha: 0.12);
    final l10n = AppLocalizations.of(context)!;

    return SafeArea(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: Scrollbar(
              controller: _scrollController,
              thumbVisibility: true,
              child: GestureDetector(
                onVerticalDragStart: _onDragStart,
                onVerticalDragUpdate: _onDragUpdate,
                onVerticalDragEnd: _onDragEnd,
                behavior: HitTestBehavior.opaque,
                child: ListView(
                  controller: _scrollController,
                  padding: const EdgeInsets.fromLTRB(0, 4, 0, 0),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/papyrus.svg',
                      text: l10n.primary_sources_screen,
                      route: '/primary_sources',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/dictionary.svg',
                      text: l10n.strongs_dictionary_screen,
                      route: '/strongs_dictionary',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/search_book.svg',
                      text: l10n.allusion_search_screen,
                      route: '/allusion_search',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/bible.svg',
                      text: l10n.bible_screen,
                      route: '/bible',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/structure.svg',
                      text: l10n.revelation_structure_screen,
                      route: '/revelation_structure',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/history.svg',
                      text: l10n.historical_background_screen,
                      route: '/historical_background',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/candle.svg',
                      text: l10n.practical_faith_screen,
                      route: '/practical_faith',
                    ),
                    Divider(color: dividerColor),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/settings.svg',
                      text: l10n.settings_screen,
                      route: '/settings',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/about.svg',
                      text: l10n.about_screen,
                      route: '/about',
                    ),
                    _buildNavigationItem(
                      assetPath: 'assets/images/UI/get_app.svg',
                      text: l10n.download,
                      route: '/download',
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 4.0),
          if (!DrawerContent.isWebForTest())
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: DrawerItem(
                assetPath: 'assets/images/UI/close.svg',
                text: AppLocalizations.of(context)!.close_app,
                onClick: () {
                  widget.onItemClicked();
                  if (DrawerContent.isDesktopForTest()) {
                    unawaited(() async {
                      final closed =
                          await DrawerContent.closeDesktopWindowForTest();
                      if (!closed) {
                        SystemNavigator.pop();
                      }
                    }());
                    return;
                  }
                  SystemNavigator.pop();
                },
              ),
            ),
        ],
      ),
    );
  }
}
