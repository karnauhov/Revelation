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

const webDbLocalVersionTokenNamespace = 'web-storage-reset-v2';

String buildLocalWebDbVersionToken(String remoteVersionToken) =>
    '$webDbLocalVersionTokenNamespace|$remoteVersionToken';

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

  final expectedLocalVersionToken = buildLocalWebDbVersionToken(
    remoteVersionToken,
  );

  return WebDbVersionSyncPlan(
    versionToken: remoteVersionToken,
    shouldResetLocalDatabase:
        forceResetLocalDatabase ||
        localVersionToken != expectedLocalVersionToken,
  );
}
