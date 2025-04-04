import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';

class PrimarySourceScreen extends StatefulWidget {
  final PrimarySource primarySource;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  PrimarySourceScreenState createState() => PrimarySourceScreenState();
}

class PrimarySourceScreenState extends State<PrimarySourceScreen> {
  String? selectedImage;
  Uint8List? imageData;
  bool isLoading = false;
  final TransformationController _transformationController =
      TransformationController();

  @override
  void initState() {
    super.initState();
    if (widget.primarySource.images.isNotEmpty) {
      selectedImage = widget.primarySource.images.first;
      loadImage(selectedImage!);
    }
  }

  @override
  Widget build(BuildContext context) {
    List<String> pages = widget.primarySource.images;

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
                DropdownButton<String>(
                  value: selectedImage,
                  hint: Text(widget.primarySource.images.isEmpty
                      ? AppLocalizations.of(context)!.images_are_missing
                      : AppLocalizations.of(context)!.choose_page),
                  onChanged: (String? newPage) {
                    setState(() {
                      selectedImage = newPage;
                      loadImage(selectedImage!);
                    });
                  },
                  items: pages.map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: selectedImage != null
                      ? () => forceReloadImage(selectedImage!)
                      : null,
                ),
                IconButton(
                  icon: const Icon(Icons.zoom_in),
                  onPressed: () {
                    final currentScale =
                        _transformationController.value.getMaxScaleOnAxis();
                    _transformationController.value = Matrix4.identity()
                      ..scale(currentScale * 1.25);
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.zoom_out),
                  onPressed: () {
                    final currentScale =
                        _transformationController.value.getMaxScaleOnAxis();
                    final newScale = currentScale / 1.25;
                    if (newScale >= 1.0) {
                      _transformationController.value = Matrix4.identity()
                        ..scale(newScale);
                    } else {
                      _transformationController.value = Matrix4.identity();
                    }
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.fit_screen),
                  onPressed: () {
                    _transformationController.value = Matrix4.identity();
                  },
                ),
              ],
            ),
          ),
        ),
      ),
      body: Center(
        child: isLoading
            ? const CircularProgressIndicator()
            : imageData != null
                ? MouseRegion(
                    cursor:
                        _transformationController.value.getMaxScaleOnAxis() >
                                1.0
                            ? SystemMouseCursors.grab
                            : MouseCursor.defer,
                    child: InteractiveViewer(
                      transformationController: _transformationController,
                      minScale: 1.0,
                      maxScale: 10.0,
                      child: Image.memory(imageData!),
                    ),
                  )
                : Text(AppLocalizations.of(context)!.image_not_loaded),
      ),
    );
  }

  Future<String> getLocalFilePath(String page) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$page';
  }

  Future<void> loadImage(String page) async {
    setState(() {
      isLoading = true;
    });

    final localFilePath = await getLocalFilePath(page);
    final file = File(localFilePath);

    if (await file.exists()) {
      final bytes = await file.readAsBytes();
      setState(() {
        imageData = bytes;
        isLoading = false;
      });
    } else {
      await _downloadAndSaveImage(page, file);
    }
  }

  Future<void> forceReloadImage(String page) async {
    setState(() {
      isLoading = true;
    });

    final localFilePath = await getLocalFilePath(page);
    final file = File(localFilePath);
    await _downloadAndSaveImage(page, file);
  }

  Future<void> _downloadAndSaveImage(String page, File file) async {
    try {
      final devider = page.indexOf("/");
      final repository = page.substring(0, devider);
      final image = page.substring(devider + 1);
      final supabase = Supabase.instance.client;
      final Uint8List fileBytes =
          await supabase.storage.from(repository).download(image);

      await file.create(recursive: true);
      await file.writeAsBytes(fileBytes);

      setState(() {
        imageData = fileBytes;
        isLoading = false;
      });
    } catch (e) {
      log.e('Image loading error: $e');
      setState(() {
        imageData = null;
        isLoading = false;
      });
    }
  }
}
