import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/common_widgets/error_message.dart';
import 'institution_card.dart';
import '../../models/institution_info.dart';
import '../../utils/common.dart';

class InstitutionList extends StatefulWidget {
  const InstitutionList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _InstitutionListState createState() => _InstitutionListState();
}

class _InstitutionListState extends State<InstitutionList> {
  late Future<List<InstitutionInfo>> _institutionsFuture;

  @override
  void initState() {
    super.initState();
    _institutionsFuture =
        parseInstitutions(rootBundle, 'assets/data/about_institutions.xml');
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<InstitutionInfo>>(
      future: _institutionsFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final institutions = snapshot.data!;
          return Column(
            children: institutions
                .map((institution) => InstitutionCard(institution: institution))
                .toList(),
          );
        } else if (snapshot.hasError) {
          return ErrorMessage(
              errorMessage:
                  AppLocalizations.of(context)!.error_loading_institutions);
        } else {
          return CircularProgressIndicator();
        }
      },
    );
  }
}
