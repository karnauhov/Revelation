import 'package:revelation/core/platform/platform_utils.dart';

bool shouldUseHeadForWebDbVersionProbe({
  required Uri uri,
  bool runningOnWeb = true,
}) {
  return !isLocalWebWith(isWebOverride: runningOnWeb, uriOverride: uri);
}
