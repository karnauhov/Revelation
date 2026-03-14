import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'topic_card.dart';

class TopicList extends StatelessWidget {
  const TopicList({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return BlocBuilder<TopicsCatalogCubit, TopicsCatalogState>(
      builder: (context, state) {
        if (state.isLoading) {
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary),
            ),
          );
        }

        if (state.failure != null) {
          return ErrorMessage(
            errorMessage: AppLocalizations.of(context)!.error_loading_topics,
          );
        }

        return Column(
          children: state.topics
              .map(
                (topic) => TopicCard(
                  topic: topic,
                  iconResource: state.iconByKey[topic.idIcon.trim()],
                ),
              )
              .toList(),
        );
      },
    );
  }
}
