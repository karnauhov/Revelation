import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/viewmodels/primary_source_view_model.dart';
import 'package:revelation/screens/primary_source/image_preview.dart';

class PrimarySourceScreen extends StatelessWidget {
  final PrimarySource primarySource;

  const PrimarySourceScreen({required this.primarySource, super.key});

  @override
  Widget build(BuildContext context) {
    TextTheme theme = Theme.of(context).textTheme;
    return ChangeNotifierProvider<PrimarySourceViewModel>(
      create: (_) => PrimarySourceViewModel(primarySource: primarySource),
      child: Consumer<PrimarySourceViewModel>(
        builder: (context, viewModel, child) {
          if (primarySource.permissionsReceived &&
              viewModel.selectedPage != null &&
              !primarySource.pages.contains(viewModel.selectedPage)) {
            viewModel.changeSelectedPage(
              primarySource.pages.isNotEmpty ? primarySource.pages.first : null,
            );
          }

          final double width = MediaQuery.of(context).size.width;
          const double threshold1 = 500.0;
          const double threshold2 = 460.0;
          final bool useActions = width > threshold1;

          return Scaffold(
            appBar: AppBar(
              title: getStyledText(
                primarySource.title,
                Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              actions: useActions ? _buildActions(context, viewModel) : null,
              bottom: useActions
                  ? null
                  : PreferredSize(
                      preferredSize: const Size.fromHeight(32.0),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: LayoutBuilder(
                          builder: (context, constraints) {
                            final bool showFullActions =
                                constraints.maxWidth > threshold2;
                            return Row(
                              mainAxisAlignment: MainAxisAlignment.start,
                              children: showFullActions
                                  ? _buildActions(context, viewModel)
                                  : _buildActionsSmall(context, viewModel),
                            );
                          },
                        ),
                      ),
                    ),
            ),
            body: Column(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(10.0, 0, 10, 0),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.black, width: 1.0),
                      ),
                      child: viewModel.isLoading
                          ? const Center(child: CircularProgressIndicator())
                          : viewModel.imageData != null
                              ? ImagePreview(
                                  imageData: viewModel.imageData!,
                                  controller: viewModel.imageController,
                                )
                              : Center(
                                  child: Text(AppLocalizations.of(context)!
                                      .image_not_loaded),
                                ),
                    ),
                  ),
                ),
                if (primarySource.attributes != null &&
                    primarySource.attributes!.isNotEmpty &&
                    primarySource.permissionsReceived)
                  Align(
                    alignment: Alignment.centerRight,
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(10, 0, 10, 2),
                      child: Text.rich(
                        TextSpan(
                          style: theme.bodySmall!.copyWith(fontSize: 10),
                          children: [
                            if (viewModel.isMobileWeb)
                              TextSpan(
                                text:
                                    '⚠️ ${AppLocalizations.of(context)!.low_quality}; ',
                                style: const TextStyle(color: Colors.blue),
                                recognizer: TapGestureRecognizer()
                                  ..onTap = () {
                                    showCustomDialog(MessageType.warningCommon,
                                        param: AppLocalizations.of(context)!
                                            .low_quality_message);
                                  },
                              ),
                            ..._buildLinkSpans(primarySource.attributes!),
                          ],
                        ),
                        maxLines: 5,
                        softWrap: true,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                if (primarySource.attributes == null ||
                    primarySource.attributes!.isEmpty ||
                    !primarySource.permissionsReceived)
                  Text.rich(TextSpan(text: ""))
              ],
            ),
          );
        },
      ),
    );
  }

  List<InlineSpan> _buildLinkSpans(List<Map<String, String>> links) {
    List<InlineSpan> spans = [];
    for (int i = 0; i < links.length; i++) {
      var link = links[i];
      if (link['url'] != null && link['url']!.isNotEmpty) {
        spans.add(
          TextSpan(
            text: link['text'],
            style: const TextStyle(color: Colors.blue),
            recognizer: TapGestureRecognizer()
              ..onTap = () {
                launchLink(link['url']!);
              },
          ),
        );
      } else {
        spans.add(
          TextSpan(
            text: link['text'],
          ),
        );
      }

      if (i < links.length - 1) {
        spans.add(const TextSpan(text: '; '));
      }
    }
    return spans;
  }

  List<Widget> _buildActions(
      BuildContext context, PrimarySourceViewModel viewModel) {
    return [
      DropdownButton<model.Page>(
        value: viewModel.selectedPage,
        hint: Text(
          primarySource.pages.isEmpty || !primarySource.permissionsReceived
              ? AppLocalizations.of(context)!.images_are_missing
              : AppLocalizations.of(context)!.choose_page,
        ),
        onChanged: (model.Page? newPage) {
          if (primarySource.permissionsReceived) {
            viewModel.changeSelectedPage(newPage);
          }
        },
        items: primarySource.permissionsReceived
            ? primarySource.pages
                .map<DropdownMenuItem<model.Page>>((model.Page value) {
                return DropdownMenuItem<model.Page>(
                  value: value,
                  child: _buildDropdownItem(context, viewModel, value),
                );
              }).toList()
            : List.empty(),
      ),
      IconButton(
        icon: viewModel.refreshError
            ? const Icon(Icons.sync_problem)
            : const Icon(Icons.sync),
        tooltip: AppLocalizations.of(context)!.reload_image,
        onPressed: viewModel.primarySource.permissionsReceived &&
                viewModel.selectedPage != null
            ? () => viewModel.loadImage(viewModel.selectedPage!.image,
                isReload: true)
            : null,
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_in),
            tooltip: AppLocalizations.of(context)!.zoom_in,
            onPressed: zoomStatus.canZoomIn
                ? () {
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    viewModel.imageController.zoomIn(viewportCenter);
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out),
            tooltip: AppLocalizations.of(context)!.zoom_out,
            onPressed: zoomStatus.canZoomOut
                ? () {
                    final viewportSize = Size(
                      MediaQuery.of(context).size.width,
                      MediaQuery.of(context).size.height,
                    );
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    viewModel.imageController
                        .zoomOut(viewportCenter, viewportSize);
                  }
                : null,
          );
        },
      ),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return IconButton(
            icon: const Icon(Icons.zoom_out_map),
            tooltip: AppLocalizations.of(context)!.restore_original_scale,
            onPressed: zoomStatus.canReset
                ? () {
                    viewModel.imageController.backToMinScale();
                  }
                : null,
          );
        },
      ),
    ];
  }

  List<Widget> _buildActionsSmall(
      BuildContext context, PrimarySourceViewModel viewModel) {
    return [
      DropdownButton<model.Page>(
        value: viewModel.selectedPage,
        hint: Text(
          primarySource.pages.isEmpty || !primarySource.permissionsReceived
              ? AppLocalizations.of(context)!.images_are_missing
              : AppLocalizations.of(context)!.choose_page,
        ),
        onChanged: (model.Page? newPage) {
          if (primarySource.permissionsReceived) {
            viewModel.changeSelectedPage(newPage);
          }
        },
        items: primarySource.permissionsReceived
            ? primarySource.pages
                .map<DropdownMenuItem<model.Page>>((model.Page value) {
                return DropdownMenuItem<model.Page>(
                  value: value,
                  child: _buildDropdownItem(context, viewModel, value),
                );
              }).toList()
            : List.empty(),
      ),
      const Spacer(),
      ValueListenableBuilder<ZoomStatus>(
        valueListenable: viewModel.zoomStatusNotifier,
        builder: (context, zoomStatus, child) {
          return PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            tooltip: AppLocalizations.of(context)!.menu,
            onSelected: (value) {
              switch (value) {
                case 'refresh':
                  if (viewModel.selectedPage != null &&
                      viewModel.primarySource.permissionsReceived) {
                    viewModel.loadImage(viewModel.selectedPage!.image,
                        isReload: true);
                  }
                  break;
                case 'zoom_in':
                  if (zoomStatus.canZoomIn) {
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    viewModel.imageController.zoomIn(viewportCenter);
                  }
                  break;
                case 'zoom_out':
                  if (zoomStatus.canZoomOut) {
                    final viewportSize = Size(
                      MediaQuery.of(context).size.width,
                      MediaQuery.of(context).size.height,
                    );
                    final viewportCenter = Offset(
                      MediaQuery.of(context).size.width / 2,
                      MediaQuery.of(context).size.height / 2,
                    );
                    viewModel.imageController
                        .zoomOut(viewportCenter, viewportSize);
                  }
                  break;
                case 'reset':
                  if (zoomStatus.canReset) {
                    viewModel.imageController.backToMinScale();
                  }
                  break;
              }
            },
            itemBuilder: (context) => <PopupMenuEntry<String>>[
              PopupMenuItem(
                value: 'refresh',
                enabled: viewModel.selectedPage != null &&
                    viewModel.primarySource.permissionsReceived,
                child: Row(
                  children: [
                    viewModel.refreshError
                        ? const Icon(Icons.sync_problem, color: Colors.black54)
                        : const Icon(Icons.sync, color: Colors.black54),
                    const SizedBox(width: 8),
                    Text(AppLocalizations.of(context)!.reload_image),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'zoom_in',
                enabled: zoomStatus.canZoomIn,
                child: Row(
                  children: [
                    const Icon(Icons.zoom_in, color: Colors.black54),
                    const SizedBox(width: 8),
                    Text(AppLocalizations.of(context)!.zoom_in),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'zoom_out',
                enabled: zoomStatus.canZoomOut,
                child: Row(
                  children: [
                    const Icon(Icons.zoom_out, color: Colors.black54),
                    const SizedBox(width: 8),
                    Text(AppLocalizations.of(context)!.zoom_out),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'reset',
                enabled: zoomStatus.canReset,
                child: Row(
                  children: [
                    const Icon(Icons.zoom_out_map, color: Colors.black54),
                    const SizedBox(width: 8),
                    Text(AppLocalizations.of(context)!.restore_original_scale),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    ];
  }

  Widget _buildDropdownItem(
      BuildContext context, PrimarySourceViewModel viewModel, model.Page page) {
    final bool? loaded = viewModel.localPageLoaded[page.image];
    return Text(
      "${page.name} (${page.content})",
      style: TextStyle(
        color: loaded == null
            ? Colors.grey.shade900
            : (loaded ? Colors.teal.shade900 : Colors.red.shade900),
        fontWeight: page == viewModel.selectedPage
            ? FontWeight.bold
            : FontWeight.normal,
      ),
    );
  }
}
