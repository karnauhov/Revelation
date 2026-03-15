@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/presentation/screens/topic_screen.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

import '../../../../test_harness/fakes/fake_settings_repository.dart';
import '../../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('TopicScreen shows error when language is empty', (tester) async {
    final settingsCubit = SettingsCubit(
      FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: '',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    await tester.pumpWidget(_buildApp(settingsCubit, const TopicScreen()));
    await tester.pumpAndSettle();

    expect(find.byType(ErrorMessage), findsOneWidget);
    expect(find.byType(MarkdownBody), findsNothing);
  });

  testWidgets('TopicScreen renders markdown when route is empty', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    await tester.pumpWidget(_buildApp(settingsCubit, const TopicScreen()));
    await tester.pumpAndSettle();

    expect(find.byType(ErrorMessage), findsNothing);
    expect(find.byType(MarkdownBody), findsOneWidget);
  });
}

Widget _buildApp(SettingsCubit settingsCubit, Widget child) {
  return BlocProvider<SettingsCubit>.value(
    value: settingsCubit,
    child: buildLocalizedTestApp(
      locale: const Locale('en'),
      child: child,
      withScaffold: false,
    ),
  );
}
