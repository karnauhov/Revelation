import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/widgets/drawer_content.dart';
import '../utils/common.dart';
import '../viewmodels/main_view_model.dart';
import '../widgets/svg_icon_button.dart';
import '../widgets/topic_list.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MainViewModel(),
      child: Consumer<MainViewModel>(
        builder: (context, viewModel, child) {
          Widget content = SafeArea(
            child: SingleChildScrollView(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(8, 0, 8, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const TopicList(),
                    ],
                  )
                ],
              ),
            ),
          );

          // Scroll Handling for Desktop and Web
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
                  _scrollController.jumpTo(_scrollController.offset - dy);
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

          return Scaffold(
            appBar: AppBar(
              title: const Text(''),
              leading: Padding(
                padding: const EdgeInsets.fromLTRB(0, 4, 4, 4),
                child: Builder(
                  builder: (context) => SvgIconButton(
                    assetPath: 'assets/images/UI/menu.svg',
                    tooltip: AppLocalizations.of(context)!.menu,
                    size: 24,
                    onPressed: () {
                      Scaffold.of(context).openDrawer();
                    },
                  ),
                ),
              ),
            ),
            drawer: const Drawer(
              child: DrawerContent(),
            ),
            body: SizedBox.expand(
              child: content,
            ),
          );
        },
      ),
    );
  }
}
