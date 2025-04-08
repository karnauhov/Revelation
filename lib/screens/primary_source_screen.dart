import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/widgets/image_preview.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class PrimarySourceScreen extends StatefulWidget {
  final PrimarySource primarySource;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  PrimarySourceScreenState createState() => PrimarySourceScreenState();
}

class PrimarySourceScreenState extends State<PrimarySourceScreen> {
  model.Page? selectedPage;
  Uint8List? imageData;
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.primarySource.pages.isNotEmpty) {
      selectedPage = widget.primarySource.pages.first;
      _loadImage(selectedPage!.image);
    }
  }

  @override
  Widget build(BuildContext context) {
    List<model.Page> pages = widget.primarySource.pages;

    return Scaffold(
      appBar: AppBar(
        title: getStyledText(
          widget.primarySource.title,
          Theme.of(context)
              .textTheme
              .headlineSmall
              ?.copyWith(fontWeight: FontWeight.bold),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48.0),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                DropdownButton<model.Page>(
                  value: selectedPage,
                  hint: Text(widget.primarySource.pages.isEmpty
                      ? AppLocalizations.of(context)!.images_are_missing
                      : AppLocalizations.of(context)!.choose_page),
                  onChanged: (model.Page? newPage) {
                    setState(() {
                      selectedPage = newPage;
                      _loadImage(selectedPage!.image);
                    });
                  },
                  items: pages
                      .map<DropdownMenuItem<model.Page>>((model.Page value) {
                    return DropdownMenuItem<model.Page>(
                      value: value,
                      child: Text("${value.name} (${value.content})"),
                    );
                  }).toList(),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: selectedPage != null
                      ? () => _loadImage(selectedPage!.image, isReload: true)
                      : null,
                ),
                IconButton(
                  icon: const Icon(Icons.zoom_in),
                  onPressed: () {
                    // TODO
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.zoom_out),
                  onPressed: () {
                    // TODO
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.fit_screen),
                  onPressed: () {
                    // TODO
                  },
                ),
              ],
            ),
          ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(10.0),
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.black, width: 1.0),
          ),
          child: isLoading
              ? const Center(child: CircularProgressIndicator())
              : imageData != null
                  ? ImagePreview(imageData: imageData!)
                  : Center(
                      child:
                          Text(AppLocalizations.of(context)!.image_not_loaded)),
        ),
      ),
    );
  }

  Future<void> _loadImage(String page, {bool isReload = false}) async {
    setState(() {
      isLoading = true;
    });

    if (isWeb()) {
      await _downloadImage(page);
    } else {
      final localFilePath = await _getLocalFilePath(page);
      final file = File(localFilePath);
      if (!isReload && await file.exists()) {
        final bytes = await file.readAsBytes();
        setState(() {
          imageData = bytes;
          isLoading = false;
        });
      } else {
        await _downloadImage(page);
        await _saveImage(file);
      }
    }
  }

  Future<String> _getLocalFilePath(String page) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$page';
  }

  Future<void> _downloadImage(String page) async {
    try {
      final devider = page.indexOf("/");
      final repository = page.substring(0, devider);
      final image = page.substring(devider + 1);
      final supabase = Supabase.instance.client;
      final Uint8List fileBytes =
          await supabase.storage.from(repository).download(image);

      setState(() {
        imageData = fileBytes;
        isLoading = false;
      });
    } catch (e) {
      log.e('Image downloading error: $e');
      setState(() {
        imageData = null;
        isLoading = false;
      });
    }
  }

  Future<void> _saveImage(File file) async {
    try {
      if (imageData != null) {
        await file.create(recursive: true);
        await file.writeAsBytes(imageData!);
      }
    } catch (e) {
      log.e('Image save error: $e');
    }
  }
}
