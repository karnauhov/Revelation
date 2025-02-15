import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/widgets/error_message.dart';
import 'library_card.dart';
import '../models/library_info.dart';
import '../utils/common.dart';

class LibraryList extends StatefulWidget {
  const LibraryList({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _LibraryListState createState() => _LibraryListState();
}

class _LibraryListState extends State<LibraryList> {
  late Future<List<LibraryInfo>> _librariesFuture;

  @override
  void initState() {
    super.initState();
    _librariesFuture =
        parseLibraries(rootBundle, 'assets/data/about_libraries.xml');
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<LibraryInfo>>(
      future: _librariesFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final libraries = snapshot.data!;
          return Column(
            children: libraries
                .map((library) => LibraryCard(library: library))
                .toList(),
          );
        } else if (snapshot.hasError) {
          return ErrorMessage(
              errorMessage:
                  AppLocalizations.of(context)!.error_loading_libraries);
        } else {
          return CircularProgressIndicator();
        }
      },
    );
  }
}
