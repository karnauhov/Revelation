import 'package:flutter/material.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_reference_info_icon.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';

Future<int?> showPrimarySourceStrongNumberPickerDialog(
  BuildContext context, {
  required List<StrongPickerEntry> entries,
  required int initialStrongNumber,
}) {
  return showDialog<int>(
    context: context,
    routeSettings: const RouteSettings(name: 'strong_number_picker_dialog'),
    builder: (_) => StrongNumberPickerDialog(
      entries: entries,
      initialStrongNumber: initialStrongNumber,
    ),
  );
}

Widget buildStrongDictionaryReferenceInfoIcon({
  required GlobalKey<TooltipState> tooltipKey,
}) {
  return StrongReferenceInfoIcon(tooltipKey: tooltipKey);
}

class PrimarySourceStrongDictionaryEntryView extends StatelessWidget {
  const PrimarySourceStrongDictionaryEntryView({
    required this.strongNumber,
    required this.markdown,
    required this.onStrongTap,
    required this.onStrongPickerTap,
    required this.onNavigateBackward,
    required this.onNavigateForward,
    this.navigationEnabled = true,
    this.exportPdfEnabled = true,
    this.copyEnabled = true,
    super.key,
  });

  final int strongNumber;
  final String markdown;
  final GreekStrongTapHandler onStrongTap;
  final GreekStrongPickerTapHandler onStrongPickerTap;
  final VoidCallback onNavigateBackward;
  final VoidCallback onNavigateForward;
  final bool navigationEnabled;
  final bool exportPdfEnabled;
  final bool copyEnabled;

  @override
  Widget build(BuildContext context) {
    return StrongDictionaryEntryView(
      strongNumber: strongNumber,
      markdown: markdown,
      padding: const EdgeInsets.fromLTRB(8, 2, 8, 8),
      navigationEnabled: navigationEnabled,
      exportPdfEnabled: exportPdfEnabled,
      copyEnabled: copyEnabled,
      backButtonKey: const Key('description_nav_back'),
      forwardButtonKey: const Key('description_nav_forward'),
      onStrongNumberSelected: (selectedStrongNumber) {
        onStrongTap(selectedStrongNumber, context);
      },
      onStrongNumberPickerRequested: (linkContext, selectedStrongNumber) {
        onStrongPickerTap(selectedStrongNumber, linkContext);
      },
      onNavigateBackward: onNavigateBackward,
      onNavigateForward: onNavigateForward,
    );
  }
}
