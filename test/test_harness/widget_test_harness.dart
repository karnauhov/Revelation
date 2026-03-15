import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/l10n/app_localizations.dart';

Widget buildLocalizedTestApp({
  required Widget child,
  Locale locale = const Locale('en'),
  bool withScaffold = true,
}) {
  return MaterialApp(
    locale: locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: withScaffold ? Scaffold(body: child) : child,
  );
}

Future<BuildContext> pumpLocalizedContext(
  WidgetTester tester, {
  Locale locale = const Locale('en'),
}) async {
  late BuildContext context;
  await tester.pumpWidget(
    buildLocalizedTestApp(
      locale: locale,
      child: Builder(
        builder: (buildContext) {
          context = buildContext;
          return const SizedBox.shrink();
        },
      ),
      withScaffold: false,
    ),
  );
  await tester.pump();
  return context;
}

Future<BuildContext> pumpContext(WidgetTester tester) async {
  late BuildContext context;
  await tester.pumpWidget(
    MaterialApp(
      home: Builder(
        builder: (buildContext) {
          context = buildContext;
          return const SizedBox.shrink();
        },
      ),
    ),
  );
  await tester.pump();
  return context;
}
