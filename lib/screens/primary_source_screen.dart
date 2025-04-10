import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/utils/image_preview_controller.dart';
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
  late ImagePreviewController _imageController;
  final Map<String, bool> localPageLoaded = {};

  @override
  void initState() {
    super.initState();
    _imageController = ImagePreviewController(widget.primarySource.maxScale);
    if (widget.primarySource.pages.isNotEmpty) {
      selectedPage = widget.primarySource.pages.first;
      _loadImage(selectedPage!.image);
    }
    _checkLocalPages();
  }

  @override
  Widget build(BuildContext context) {
    if (selectedPage != null &&
        !widget.primarySource.pages.contains(selectedPage)) {
      selectedPage = widget.primarySource.pages.isNotEmpty
          ? widget.primarySource.pages.first
          : null;
    }

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
            child: LayoutBuilder(
              builder: (context, constraints) {
                const double minWidthForFullActions = 390.0;
                if (constraints.maxWidth > minWidthForFullActions) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      DropdownButton<model.Page>(
                        value: selectedPage,
                        hint: Text(
                          widget.primarySource.pages.isEmpty
                              ? AppLocalizations.of(context)!.images_are_missing
                              : AppLocalizations.of(context)!.choose_page,
                        ),
                        onChanged: (model.Page? newPage) {
                          setState(() {
                            selectedPage = newPage;
                          });
                          if (newPage != null) {
                            _loadImage(newPage.image);
                          }
                        },
                        items: widget.primarySource.pages
                            .map<DropdownMenuItem<model.Page>>(
                          (model.Page value) {
                            return DropdownMenuItem<model.Page>(
                              value: value,
                              child: _buildDropdownItem(value),
                            );
                          },
                        ).toList(),
                      ),
                      IconButton(
                        icon: const Icon(Icons.refresh),
                        tooltip: AppLocalizations.of(context)!.reload_image,
                        onPressed: selectedPage != null
                            ? () =>
                                _loadImage(selectedPage!.image, isReload: true)
                            : null,
                      ),
                      IconButton(
                        icon: const Icon(Icons.zoom_in),
                        tooltip: AppLocalizations.of(context)!.zoom_in,
                        onPressed: () {
                          if (imageData != null) {
                            final viewportCenter = Offset(
                              MediaQuery.of(context).size.width / 2,
                              MediaQuery.of(context).size.height / 2,
                            );
                            _imageController.zoomIn(viewportCenter);
                          }
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.zoom_out),
                        tooltip: AppLocalizations.of(context)!.zoom_out,
                        onPressed: () {
                          if (imageData != null) {
                            final viewportSize = Size(
                              MediaQuery.of(context).size.width,
                              MediaQuery.of(context).size.height,
                            );
                            final viewportCenter = Offset(
                              MediaQuery.of(context).size.width / 2,
                              MediaQuery.of(context).size.height / 2,
                            );
                            _imageController.zoomOut(
                                viewportCenter, viewportSize);
                          }
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.zoom_out_map),
                        tooltip: AppLocalizations.of(context)!
                            .restore_original_scale,
                        onPressed: () {
                          if (imageData != null) {
                            _imageController.backToMinScale();
                          }
                        },
                      ),
                    ],
                  );
                } else {
                  return Row(
                    children: [
                      DropdownButton<model.Page>(
                        value: selectedPage,
                        hint: Text(
                          widget.primarySource.pages.isEmpty
                              ? AppLocalizations.of(context)!.images_are_missing
                              : AppLocalizations.of(context)!.choose_page,
                        ),
                        onChanged: (model.Page? newPage) {
                          setState(() {
                            selectedPage = newPage;
                          });
                          if (newPage != null) {
                            _loadImage(newPage.image);
                          }
                        },
                        items: widget.primarySource.pages
                            .map<DropdownMenuItem<model.Page>>(
                          (model.Page value) {
                            return DropdownMenuItem<model.Page>(
                              value: value,
                              child: _buildDropdownItem(value),
                            );
                          },
                        ).toList(),
                      ),
                      const Spacer(),
                      PopupMenuButton<String>(
                        icon: const Icon(Icons.more_vert),
                        tooltip: AppLocalizations.of(context)!.menu,
                        onSelected: (value) {
                          switch (value) {
                            case 'refresh':
                              if (selectedPage != null) {
                                _loadImage(selectedPage!.image, isReload: true);
                              }
                              break;
                            case 'zoom_in':
                              if (imageData != null) {
                                final viewportCenter = Offset(
                                  MediaQuery.of(context).size.width / 2,
                                  MediaQuery.of(context).size.height / 2,
                                );
                                _imageController.zoomIn(viewportCenter);
                              }
                              break;
                            case 'zoom_out':
                              if (imageData != null) {
                                final viewportSize = Size(
                                  MediaQuery.of(context).size.width,
                                  MediaQuery.of(context).size.height,
                                );
                                final viewportCenter = Offset(
                                  MediaQuery.of(context).size.width / 2,
                                  MediaQuery.of(context).size.height / 2,
                                );
                                _imageController.zoomOut(
                                    viewportCenter, viewportSize);
                              }
                              break;
                            case 'reset':
                              if (imageData != null) {
                                _imageController.backToMinScale();
                              }
                              break;
                          }
                        },
                        itemBuilder: (context) => [
                          PopupMenuItem(
                            value: 'refresh',
                            child: Row(
                              children: [
                                const Icon(Icons.refresh,
                                    color: Colors.black54),
                                const SizedBox(width: 8),
                                Text(
                                    AppLocalizations.of(context)!.reload_image),
                              ],
                            ),
                          ),
                          PopupMenuItem(
                            value: 'zoom_in',
                            child: Row(
                              children: [
                                const Icon(Icons.zoom_in,
                                    color: Colors.black54),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!.zoom_in),
                              ],
                            ),
                          ),
                          PopupMenuItem(
                            value: 'zoom_out',
                            child: Row(
                              children: [
                                const Icon(Icons.zoom_out,
                                    color: Colors.black54),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!.zoom_out),
                              ],
                            ),
                          ),
                          PopupMenuItem(
                            value: 'reset',
                            child: Row(
                              children: [
                                const Icon(Icons.zoom_out_map,
                                    color: Colors.black54),
                                const SizedBox(width: 8),
                                Text(AppLocalizations.of(context)!
                                    .restore_original_scale),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  );
                }
              },
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
                  ? ImagePreview(
                      imageData: imageData!,
                      controller: _imageController,
                    )
                  : Center(
                      child:
                          Text(AppLocalizations.of(context)!.image_not_loaded),
                    ),
        ),
      ),
    );
  }

  Future<void> _checkLocalPages() async {
    if (isWeb()) {
      for (var page in widget.primarySource.pages) {
        setState(() {
          localPageLoaded[page.image] = true;
        });
      }
    } else {
      for (var page in widget.primarySource.pages) {
        final localFilePath = await _getLocalFilePath(page.image);
        final exists = await File(localFilePath).exists();
        setState(() {
          localPageLoaded[page.image] = exists;
        });
      }
    }
  }

  Widget _buildDropdownItem(model.Page page) {
    Color textColor = (localPageLoaded[page.image] ?? false)
        ? Colors.teal.shade900
        : Colors.red.shade900;
    FontWeight fontWeight =
        (page == selectedPage) ? FontWeight.bold : FontWeight.normal;
    return Text(
      "${page.name} (${page.content})",
      style: TextStyle(color: textColor, fontWeight: fontWeight),
    );
  }

  Future<void> _loadImage(String page, {bool isReload = false}) async {
    setState(() {
      isLoading = true;
    });

    if (isWeb()) {
      await _downloadImage(page);
      setState(() {
        localPageLoaded[page] = true;
      });
    } else {
      final localFilePath = await _getLocalFilePath(page);
      final file = File(localFilePath);
      if (!isReload && await file.exists()) {
        final bytes = await file.readAsBytes();
        setState(() {
          imageData = bytes;
          isLoading = false;
          localPageLoaded[page] = true;
        });
      } else {
        await _downloadImage(page);
        await _saveImage(file);
        setState(() {
          localPageLoaded[page] = true;
        });
      }
    }
  }

  Future<String> _getLocalFilePath(String page) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$page';
  }

  Future<void> _downloadImage(String page) async {
    try {
      final divider = page.indexOf("/");
      final repository = page.substring(0, divider);
      final image = page.substring(divider + 1);
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
