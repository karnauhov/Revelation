import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/common_widgets/error_message.dart';
import 'package:revelation/screens/about/recommended_card.dart';
import '../../models/recommended_info.dart';
import '../../utils/common.dart';

class RecommendedList extends StatefulWidget {
  const RecommendedList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _RecommendedListState createState() => _RecommendedListState();
}

class _RecommendedListState extends State<RecommendedList> {
  late Future<List<RecommendedInfo>> _recommendedFuture;

  @override
  void initState() {
    super.initState();
    _recommendedFuture = parseRecommended(
      rootBundle,
      'assets/data/about_recommended.xml',
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return FutureBuilder<List<RecommendedInfo>>(
      future: _recommendedFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final recommendations = snapshot.data!;
          return Column(
            children: recommendations
                .map(
                  (recommendation) =>
                      RecommendedCard(recommended: recommendation),
                )
                .toList(),
          );
        } else if (snapshot.hasError) {
          return ErrorMessage(
            errorMessage: AppLocalizations.of(
              context,
            )!.error_loading_recommendations,
          );
        } else {
          return Center(
            child: CircularProgressIndicator(color: colorScheme.primary),
          );
        }
      },
    );
  }
}
