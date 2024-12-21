import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:revelation/widgets/drawer_content.dart';
import '../widgets/svg_icon_button.dart';

class MainScreen extends StatelessWidget {
  const MainScreen({super.key});

  @override
  Widget build(BuildContext context) {
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
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Text(AppLocalizations.of(context)!.todo),
      ),
    );
  }
}
