import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:window_manager/window_manager.dart';
import 'drawer_item.dart';
import '../utils/common.dart';

class DrawerContent extends StatefulWidget {
  const DrawerContent({super.key});

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

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: Scrollbar(
              controller: _scrollController,
              child: GestureDetector(
                onVerticalDragStart: _onDragStart,
                onVerticalDragUpdate: _onDragUpdate,
                onVerticalDragEnd: _onDragEnd,
                behavior: HitTestBehavior.opaque,
                child: ListView(
                  controller: _scrollController,
                  padding: EdgeInsets.fromLTRB(0, 4, 0, 0),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    DrawerItem(
                      assetPath: 'assets/images/UI/settings.svg',
                      text: AppLocalizations.of(context)!.settings_screen,
                      onClick: () {
                        Navigator.pop(context);
                        context.push('/settings');
                      },
                    ),
                    const Divider(),
                    DrawerItem(
                      assetPath: 'assets/images/UI/smartphone.svg',
                      text: AppLocalizations.of(context)!.about_screen,
                      onClick: () {
                        Navigator.pop(context);
                        context.push('/about');
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 4.0),
          if (!kIsWeb)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: DrawerItem(
                assetPath: 'assets/images/UI/close.svg',
                text: AppLocalizations.of(context)!.close_app,
                onClick: () {
                  SystemNavigator.pop();
                  if (isDesktop()) {
                    windowManager.close();
                  }
                },
              ),
            ),
        ],
      ),
    );
  }
}