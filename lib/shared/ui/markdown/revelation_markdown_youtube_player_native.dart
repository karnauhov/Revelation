import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';
import 'package:revelation/shared/utils/links_utils.dart';

class RevelationMarkdownYoutubeNavigationDecision {
  const RevelationMarkdownYoutubeNavigationDecision._({
    required this.allowInWebView,
    this.externalUrl,
  });

  const RevelationMarkdownYoutubeNavigationDecision.allow()
    : this._(allowInWebView: true);

  const RevelationMarkdownYoutubeNavigationDecision.openExternally(
    String externalUrl,
  ) : this._(allowInWebView: false, externalUrl: externalUrl);

  final bool allowInWebView;
  final String? externalUrl;
}

@visibleForTesting
RevelationMarkdownYoutubeNavigationDecision
resolveRevelationMarkdownYoutubeNavigation({
  required Uri? uri,
  required bool isForMainFrame,
}) {
  if (uri == null || !isForMainFrame || _isLocalPlayerShellUri(uri)) {
    return const RevelationMarkdownYoutubeNavigationDecision.allow();
  }
  return RevelationMarkdownYoutubeNavigationDecision.openExternally(
    uri.toString(),
  );
}

@visibleForTesting
String? resolveRevelationMarkdownYoutubeCreateWindowExternalUrl(Uri? uri) {
  return uri?.toString();
}

@visibleForTesting
String? resolveRevelationMarkdownYoutubeEscapedShellExternalUrl(Uri? uri) {
  if (uri == null || _isLocalPlayerShellUri(uri)) {
    return null;
  }
  return uri.toString();
}

@visibleForTesting
bool shouldSuppressRevelationMarkdownYoutubeExternalLaunch({
  required String externalUrl,
  required String? lastExternalUrl,
  required DateTime? lastExternalLaunchAt,
  required DateTime now,
  Duration dedupeWindow = const Duration(seconds: 1),
}) {
  if (lastExternalUrl != externalUrl || lastExternalLaunchAt == null) {
    return false;
  }
  return now.difference(lastExternalLaunchAt) <= dedupeWindow;
}

Widget buildRevelationMarkdownYoutubePlayer({
  Key? key,
  required RevelationMarkdownYoutubeData video,
}) {
  if (shouldUseRevelationMarkdownYoutubeLinuxFallback(
    isWeb: kIsWeb,
    platform: defaultTargetPlatform,
  )) {
    return _RevelationMarkdownYoutubeLinuxFallbackPlayer(
      key: key,
      video: video,
    );
  }
  return _RevelationMarkdownYoutubeNativePlayer(key: key, video: video);
}

@visibleForTesting
bool shouldUseRevelationMarkdownYoutubeLinuxFallback({
  required bool isWeb,
  required TargetPlatform platform,
}) {
  return !isWeb && platform == TargetPlatform.linux;
}

class _RevelationMarkdownYoutubeLinuxFallbackPlayer extends StatelessWidget {
  const _RevelationMarkdownYoutubeLinuxFallbackPlayer({
    required this.video,
    super.key,
  });

  final RevelationMarkdownYoutubeData video;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final externalUrl = video.originalVideoUri?.toString();
    final theme = Theme.of(context);
    final onTap = externalUrl == null
        ? null
        : () async {
            await launchLink(externalUrl);
          };

    return Material(
      color: Colors.black,
      child: InkWell(
        onTap: onTap,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.ondemand_video, color: Colors.white, size: 36),
                const SizedBox(height: 10),
                Text(
                  video.title ?? l10n.markdown_youtube_player_title,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RevelationMarkdownYoutubeNativePlayer extends StatefulWidget {
  const _RevelationMarkdownYoutubeNativePlayer({
    required this.video,
    super.key,
  });

  final RevelationMarkdownYoutubeData video;

  @override
  State<_RevelationMarkdownYoutubeNativePlayer> createState() =>
      _RevelationMarkdownYoutubeNativePlayerState();
}

class _RevelationMarkdownYoutubeNativePlayerState
    extends State<_RevelationMarkdownYoutubeNativePlayer> {
  bool _isRestoringExternalNavigation = false;
  String? _lastExternalLaunchUrl;
  DateTime? _lastExternalLaunchAt;

  Future<void> _launchExternalUrlOnce(String externalUrl) async {
    final now = DateTime.now();
    final shouldSuppress =
        shouldSuppressRevelationMarkdownYoutubeExternalLaunch(
          externalUrl: externalUrl,
          lastExternalUrl: _lastExternalLaunchUrl,
          lastExternalLaunchAt: _lastExternalLaunchAt,
          now: now,
        );
    if (shouldSuppress) {
      return;
    }

    _lastExternalLaunchUrl = externalUrl;
    _lastExternalLaunchAt = now;
    await launchLink(externalUrl);
  }

  Future<void> _restorePlayerShellAfterExternalNavigation({
    required InAppWebViewController controller,
    required Uri playerUri,
    required Uri? navigatedUri,
  }) async {
    final externalUrl = resolveRevelationMarkdownYoutubeEscapedShellExternalUrl(
      navigatedUri,
    );
    if (externalUrl == null || _isRestoringExternalNavigation) {
      return;
    }

    _isRestoringExternalNavigation = true;
    try {
      await _launchExternalUrlOnce(externalUrl);
      await controller.stopLoading();

      final currentUrl = await controller.getUrl();
      if (currentUrl != null && _isLocalPlayerShellUri(currentUrl)) {
        return;
      }

      if (await controller.canGoBack()) {
        await controller.goBack();
        return;
      }

      await controller.loadUrl(
        urlRequest: URLRequest(url: WebUri(playerUri.toString())),
      );
    } finally {
      _isRestoringExternalNavigation = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider<_RevelationMarkdownYoutubeNativeCubit>(
      create: (_) => _RevelationMarkdownYoutubeNativeCubit(
        resolvePlayerUri:
            _RevelationMarkdownYoutubeLocalhostServer.buildPlayerUri,
      )..initialize(widget.video),
      child:
          BlocBuilder<
            _RevelationMarkdownYoutubeNativeCubit,
            _RevelationMarkdownYoutubeNativeState
          >(
            builder: (context, state) {
              switch (state.status) {
                case _RevelationMarkdownYoutubeNativeStatus.loading:
                  return const Center(child: CircularProgressIndicator());
                case _RevelationMarkdownYoutubeNativeStatus.failure:
                  return _YoutubeNativeFailureCard(video: widget.video);
                case _RevelationMarkdownYoutubeNativeStatus.ready:
                  final playerUri = state.playerUri;
                  if (playerUri == null) {
                    return _YoutubeNativeFailureCard(video: widget.video);
                  }
                  return InAppWebView(
                    initialUrlRequest: URLRequest(
                      url: WebUri(playerUri.toString()),
                    ),
                    initialSettings: InAppWebViewSettings(
                      isInspectable: kDebugMode,
                      mediaPlaybackRequiresUserGesture: false,
                      allowsInlineMediaPlayback: true,
                      useShouldOverrideUrlLoading: true,
                      supportMultipleWindows: true,
                      javaScriptCanOpenWindowsAutomatically: true,
                      disableVerticalScroll: true,
                      disableHorizontalScroll: true,
                      disallowOverScroll: true,
                      verticalScrollBarEnabled: false,
                      horizontalScrollBarEnabled: false,
                      iframeAllow:
                          'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen',
                      iframeAllowFullscreen: true,
                    ),
                    shouldOverrideUrlLoading:
                        (controller, navigationAction) async {
                          final decision =
                              resolveRevelationMarkdownYoutubeNavigation(
                                uri: navigationAction.request.url,
                                isForMainFrame: navigationAction.isForMainFrame,
                              );
                          if (decision.allowInWebView) {
                            return NavigationActionPolicy.ALLOW;
                          }
                          final externalUrl = decision.externalUrl;
                          if (externalUrl != null) {
                            await _launchExternalUrlOnce(externalUrl);
                          }
                          return NavigationActionPolicy.CANCEL;
                        },
                    onLoadStart: (controller, url) async {
                      await _restorePlayerShellAfterExternalNavigation(
                        controller: controller,
                        playerUri: playerUri,
                        navigatedUri: url?.uriValue,
                      );
                    },
                    onUpdateVisitedHistory:
                        (controller, url, androidIsReload) async {
                          await _restorePlayerShellAfterExternalNavigation(
                            controller: controller,
                            playerUri: playerUri,
                            navigatedUri: url?.uriValue,
                          );
                        },
                    onCreateWindow: (controller, createWindowAction) async {
                      final externalUrl =
                          resolveRevelationMarkdownYoutubeCreateWindowExternalUrl(
                            createWindowAction.request.url,
                          );
                      if (externalUrl != null) {
                        await _launchExternalUrlOnce(externalUrl);
                      }
                      return false;
                    },
                  );
              }
            },
          ),
    );
  }
}

class _YoutubeNativeFailureCard extends StatelessWidget {
  const _YoutubeNativeFailureCard({required this.video});

  final RevelationMarkdownYoutubeData video;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        border: Border.all(color: colorScheme.outlineVariant),
      ),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.play_circle_outline,
                color: colorScheme.onSurfaceVariant,
                size: 32,
              ),
              const SizedBox(height: 12),
              Text(
                l10n.markdown_youtube_unavailable_title,
                textAlign: TextAlign.center,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                l10n.markdown_youtube_unavailable_description,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

enum _RevelationMarkdownYoutubeNativeStatus { loading, ready, failure }

class _RevelationMarkdownYoutubeNativeState {
  const _RevelationMarkdownYoutubeNativeState._({
    required this.status,
    this.playerUri,
  });

  const _RevelationMarkdownYoutubeNativeState.loading()
    : this._(status: _RevelationMarkdownYoutubeNativeStatus.loading);

  const _RevelationMarkdownYoutubeNativeState.ready({required Uri playerUri})
    : this._(
        status: _RevelationMarkdownYoutubeNativeStatus.ready,
        playerUri: playerUri,
      );

  const _RevelationMarkdownYoutubeNativeState.failure()
    : this._(status: _RevelationMarkdownYoutubeNativeStatus.failure);

  final _RevelationMarkdownYoutubeNativeStatus status;
  final Uri? playerUri;

  @override
  bool operator ==(Object other) {
    return other is _RevelationMarkdownYoutubeNativeState &&
        other.status == status &&
        other.playerUri == playerUri;
  }

  @override
  int get hashCode => Object.hash(status, playerUri);
}

class _RevelationMarkdownYoutubeNativeCubit
    extends Cubit<_RevelationMarkdownYoutubeNativeState> {
  _RevelationMarkdownYoutubeNativeCubit({required this.resolvePlayerUri})
    : super(const _RevelationMarkdownYoutubeNativeState.loading());

  final Future<Uri> Function(RevelationMarkdownYoutubeData video)
  resolvePlayerUri;

  Future<void> initialize(RevelationMarkdownYoutubeData video) async {
    emit(const _RevelationMarkdownYoutubeNativeState.loading());
    try {
      final playerUri = await resolvePlayerUri(video);
      if (isClosed) {
        return;
      }
      emit(_RevelationMarkdownYoutubeNativeState.ready(playerUri: playerUri));
    } catch (_) {
      if (isClosed) {
        return;
      }
      emit(const _RevelationMarkdownYoutubeNativeState.failure());
    }
  }
}

class _RevelationMarkdownYoutubeLocalhostServer {
  static const int _port = 8787;
  static const String _documentRoot = 'assets';
  static const String _playerPath =
      '/data/markdown/markdown_youtube_player.html';

  static final InAppLocalhostServer _server = InAppLocalhostServer(
    port: _port,
    documentRoot: _documentRoot,
    shared: true,
  );
  static Future<void>? _startFuture;

  static Future<Uri> buildPlayerUri(RevelationMarkdownYoutubeData video) async {
    _startFuture ??= _startServer();
    await _startFuture;

    return Uri(
      scheme: 'http',
      host: 'localhost',
      port: _port,
      path: _playerPath,
      queryParameters: <String, String>{
        'videoId': video.videoId,
        'title': video.title ?? '',
        if (video.startAtSeconds > 0) 'start': '${video.startAtSeconds}',
      },
    );
  }

  static Future<void> _startServer() async {
    if (_server.isRunning()) {
      return;
    }
    try {
      await _server.start();
    } catch (_) {
      _startFuture = null;
      rethrow;
    }
  }
}

bool _isLocalPlayerShellUri(Uri uri) {
  return uri.scheme == 'http' && uri.host.toLowerCase() == 'localhost';
}
