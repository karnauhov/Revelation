class WebDbVersionSyncPlan {
  const WebDbVersionSyncPlan({
    required this.versionToken,
    required this.shouldResetLocalDatabase,
  });

  final String? versionToken;
  final bool shouldResetLocalDatabase;

  bool get shouldCommitVersionAfterOpen =>
      versionToken != null && shouldResetLocalDatabase;
}

WebDbVersionSyncPlan planWebDbVersionSync({
  required String? remoteVersionToken,
  required String? localVersionToken,
  bool forceResetLocalDatabase = false,
}) {
  if (remoteVersionToken == null) {
    return const WebDbVersionSyncPlan(
      versionToken: null,
      shouldResetLocalDatabase: false,
    );
  }

  return WebDbVersionSyncPlan(
    versionToken: remoteVersionToken,
    shouldResetLocalDatabase:
        forceResetLocalDatabase || localVersionToken != remoteVersionToken,
  );
}
