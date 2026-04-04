{{flutter_js}}
{{flutter_build_config}}

(() => {
  const loader = document.getElementById('app-loader');
  const loaderTitle = document.getElementById('app-loader-title');
  const loaderSubtitle = document.getElementById('app-loader-subtitle');
  const loaderVersion = document.getElementById('app-loader-version');
  const loaderProgress = document.getElementById('app-loader-progress');
  const loaderProgressFill = document.getElementById('app-loader-progress-fill');
  const loaderProgressText = document.getElementById('app-loader-progress-text');
  const flutterReadySelector = 'flutter-view, flt-glass-pane';
  const loaderManifestUrl = 'loader_manifest.json';
  const loaderStartTimeMs = nowMs();
  const basePath = normalizeBasePath(new URL(document.baseURI).pathname);

  // Keep this list in sync with AppLocalizations.languages() in
  // lib/core/localization/localization.dart.
  const supportedWebLoaderLocales = ['en', 'es', 'ru', 'uk'];

  // IMPORTANT: these web loader strings are separate from ARB/localization_lookup.
  // When a new locale is added in the app, add its translation here too.
  const copyByLocale = {
    en: {
      appName: 'Revelation',
      loadingWebApp: 'Loading web application...',
      loadingFailed: 'We could not finish loading the app.',
      errorHint: 'Please refresh the page and try again.',
      progressAriaLabel: 'Web app loading progress',
      versionPrefix: 'Version',
      versionFallback: 'Version -- (--)',
    },
    es: {
      appName: 'Apocalipsis',
      loadingWebApp: 'Descargando la aplicación web...',
      loadingFailed: 'No pudimos completar la carga de la aplicación.',
      errorHint: 'Actualice la página e inténtelo de nuevo.',
      progressAriaLabel: 'Progreso de carga de la aplicación web',
      versionPrefix: 'Version',
      versionFallback: 'Version -- (--)',
    },
    ru: {
      appName: 'Откровение',
      loadingWebApp: 'Загружаем веб-приложение...',
      loadingFailed: 'Не удалось завершить загрузку приложения.',
      errorHint: 'Пожалуйста, обновите страницу и попробуйте снова.',
      progressAriaLabel: 'Прогресс загрузки веб-приложения',
      versionPrefix: 'Версия',
      versionFallback: 'Версия -- (--)',
    },
    uk: {
      appName: "Об'явлення",
      loadingWebApp: 'Завантажуємо веб-застосунок...',
      loadingFailed: 'Не вдалося завершити завантаження застосунку.',
      errorHint: 'Будь ласка, оновіть сторінку та спробуйте ще раз.',
      progressAriaLabel: 'Прогрес завантаження веб-застосунку',
      versionPrefix: 'Версія',
      versionFallback: 'Версія -- (--)',
    },
  };

  validateCopyCoverage();

  const locale = resolveLocale();
  const copy = copyByLocale[locale] ?? copyByLocale.en;
  document.documentElement.lang = locale;

  if (loaderTitle) {
    loaderTitle.textContent = copy.appName;
  }

  if (loaderSubtitle) {
    loaderSubtitle.textContent = copy.loadingWebApp;
  }

  if (loaderProgress) {
    loaderProgress.setAttribute('aria-label', copy.progressAriaLabel);
  }

  if (loaderVersion) {
    loaderVersion.textContent = copy.versionFallback;
  }

  let currentProgressPercent = 3;
  renderProgress(currentProgressPercent);

  let loaderManifest = null;
  let navigationDocument = null;
  const requiredResourcesByPath = new Map();
  const optionalResourcesByPath = new Map();
  const optionalGroupMaxBytes = new Map();
  const selectedOptionalPathByGroup = new Map();
  const externalResourcesByUrl = new Map();
  const externalMatchGroupsById = new Map();
  const selectedExternalResourcesByGroup = new Map();
  const countedResourceKeys = new Set();
  const observedResourceSizesByKey = new Map();
  const completedResourceSamples = [];
  let loadedTrackedBytes = 0;
  let processedPerformanceEntries = 0;
  let totalCompletedSampleBytes = 0;
  let totalCompletedSampleDurationMs = 0;
  let activePredictionWindow = null;
  let progressFrameRequestId = null;
  let lastRenderedFrameMs = loaderStartTimeMs;

  void Promise.all([loadVersionInfo(copy), loadLoaderManifest()]).then(
    ([versionText, manifest]) => {
      if (loaderVersion && versionText) {
        loaderVersion.textContent = versionText;
      }
      setLoaderManifest(manifest);
    },
  );

  let loaderCanDismiss = false;
  let loaderDismissed = false;
  let observer;
  const serviceWorkerVersion =
    parseServiceWorkerVersion(`{{flutter_service_worker_version}}`) ??
    'revelation-files-cache-v1';
  requestProgressFrame();

  _flutter.loader.load({
    serviceWorkerSettings: {
      serviceWorkerVersion,
      serviceWorkerUrl:
        `revelation_files_cache_sw.js?v=${encodeURIComponent(serviceWorkerVersion)}`,
    },
    onEntrypointLoaded: async (engineInitializer) => {
      try {
        const appRunner = await engineInitializer.initializeEngine();
        await appRunner.runApp();
        loaderCanDismiss = true;
        observeFlutterReady();
        requestAnimationFrame(() =>
            requestAnimationFrame(dismissLoaderWhenFlutterReady));
      } catch (_) {
        handleBootstrapFailure();
      }
    },
  });

  function resolveLocale() {
    const languageTag = (
      (Array.isArray(navigator.languages) && navigator.languages[0]) ||
      navigator.language ||
      'en'
    ).toLowerCase();

    if (languageTag.startsWith('es')) {
      return 'es';
    }
    if (languageTag.startsWith('ru')) {
      return 'ru';
    }
    if (languageTag.startsWith('uk')) {
      return 'uk';
    }
    return 'en';
  }

  async function loadVersionInfo(currentCopy) {
    try {
      const response = await fetch('version.json', { cache: 'no-store' });
      if (!response.ok) {
        return null;
      }

      const payload = await response.json();
      const version = normalizeField(payload.version);
      const buildNumber = normalizeField(payload.build_number);
      if (!version || !buildNumber) {
        return null;
      }

      return `${currentCopy.versionPrefix} ${version} (${buildNumber})`;
    } catch (_) {
      return null;
    }
  }

  function normalizeField(value) {
    if (typeof value !== 'string') {
      return '';
    }
    return value.trim();
  }

  function parseServiceWorkerVersion(rawValue) {
    const normalized = String(rawValue ?? '').trim();
    if (
      normalized.length === 0 ||
      normalized === 'null' ||
      /^\{\{[^}]+\}\}$/.test(normalized)
    ) {
      return null;
    }

    const quotedMatch = normalized.match(/^"([^"]+)"/);
    if (quotedMatch) {
      return quotedMatch[1];
    }

    return normalized.replace(/^"|"$/g, '');
  }

  async function loadLoaderManifest() {
    try {
      const response = await fetch(loaderManifestUrl, { cache: 'no-store' });
      if (!response.ok) {
        return null;
      }
      const payload = await response.json();
      return normalizeLoaderManifest(payload);
    } catch (_) {
      return null;
    }
  }

  function normalizeLoaderManifest(payload) {
    if (!payload) {
      return null;
    }

    const schemaVersion = normalizePositiveInt(payload.schema_version);
    const requiredResources = normalizeResourceList(payload.required_resources);
    const optionalGroups = normalizeOptionalGroups(payload.optional_groups);

    if (schemaVersion === 1) {
      if (requiredResources.length === 0 && optionalGroups.length === 0) {
        return null;
      }
      return {
        navigationDocument: null,
        requiredResources,
        optionalGroups,
        externalResources: [],
        externalMatchGroups: [],
      };
    }

    if (schemaVersion !== 2) {
      return null;
    }

    const normalizedNavigationDocument = normalizeSingleResource(
      payload.navigation_document,
    );
    const externalResources = normalizeExternalResourceList(
      payload.external_resources,
    );
    const externalMatchGroups = normalizeExternalMatchGroups(
      payload.external_match_groups,
    );

    if (
      !normalizedNavigationDocument &&
      requiredResources.length === 0 &&
      optionalGroups.length === 0 &&
      externalResources.length === 0 &&
      externalMatchGroups.length === 0
    ) {
      return null;
    }

    return {
      navigationDocument: normalizedNavigationDocument,
      requiredResources,
      optionalGroups,
      externalResources,
      externalMatchGroups,
    };
  }

  function normalizeSingleResource(value) {
    const path = normalizeManifestPath(value?.path);
    const sizeBytes = normalizePositiveInt(value?.size_bytes);
    if (!path || sizeBytes <= 0) {
      return null;
    }
    return { path, sizeBytes };
  }

  function normalizeResourceList(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const resources = [];
    for (const item of listValue) {
      const path = normalizeManifestPath(item?.path);
      const sizeBytes = normalizePositiveInt(item?.size_bytes);
      if (!path || sizeBytes <= 0) {
        continue;
      }
      resources.push({ path, sizeBytes });
    }

    return resources;
  }

  function normalizeOptionalGroups(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const optionalGroups = [];
    for (const optionalGroupRaw of listValue) {
      const groupId = normalizeGroupId(optionalGroupRaw?.id);
      if (!groupId) {
        continue;
      }

      const candidates = normalizeResourceList(optionalGroupRaw?.candidates);
      if (candidates.length === 0) {
        continue;
      }

      const declaredMaxCandidateBytes = normalizePositiveInt(
        optionalGroupRaw?.max_candidate_bytes,
      );
      let maxCandidateBytes = declaredMaxCandidateBytes;
      if (maxCandidateBytes <= 0) {
        for (const candidate of candidates) {
          if (candidate.sizeBytes > maxCandidateBytes) {
            maxCandidateBytes = candidate.sizeBytes;
          }
        }
      }

      if (maxCandidateBytes <= 0) {
        continue;
      }

      optionalGroups.push({
        id: groupId,
        maxCandidateBytes,
        candidates,
      });
    }

    return optionalGroups;
  }

  function normalizeExternalResourceList(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const resources = [];
    for (const item of listValue) {
      const url = normalizeAbsoluteManifestUrl(item?.url);
      const sizeBytes = normalizePositiveInt(item?.size_bytes);
      if (!url || sizeBytes <= 0) {
        continue;
      }
      resources.push({ url, sizeBytes });
    }

    return resources;
  }

  function normalizeExternalMatchGroups(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const groups = [];
    for (const groupValue of listValue) {
      const groupId = normalizeGroupId(groupValue?.id);
      const urlPrefixes = normalizeAbsoluteManifestUrlList(groupValue?.url_prefixes);
      const extensions = normalizeExtensions(groupValue?.extensions);
      const maxMatches = Math.max(
        1,
        normalizePositiveInt(groupValue?.max_matches) || 1,
      );
      const maxCandidateBytes = normalizePositiveInt(
        groupValue?.max_candidate_bytes,
      );

      if (!groupId || urlPrefixes.length === 0 || maxCandidateBytes <= 0) {
        continue;
      }

      groups.push({
        id: groupId,
        urlPrefixes,
        extensions,
        maxMatches,
        maxCandidateBytes,
      });
    }

    return groups;
  }

  function normalizeManifestPath(rawPath) {
    if (typeof rawPath !== 'string') {
      return '';
    }

    let normalized = rawPath.trim().replaceAll('\\', '/');
    while (normalized.startsWith('/')) {
      normalized = normalized.slice(1);
    }
    return normalized;
  }

  function normalizeAbsoluteManifestUrl(rawUrl) {
    if (typeof rawUrl !== 'string' || rawUrl.trim() === '') {
      return '';
    }

    try {
      const parsedUrl = new URL(rawUrl, window.location.href);
      parsedUrl.hash = '';
      return parsedUrl.href;
    } catch (_) {
      return '';
    }
  }

  function normalizeAbsoluteManifestUrlList(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const urls = [];
    for (const item of listValue) {
      const normalizedUrl = normalizeAbsoluteManifestUrl(item);
      if (normalizedUrl) {
        urls.push(normalizedUrl);
      }
    }
    return urls;
  }

  function normalizeExtensions(listValue) {
    if (!Array.isArray(listValue)) {
      return [];
    }

    const extensions = [];
    for (const item of listValue) {
      if (typeof item !== 'string' || item.trim() === '') {
        continue;
      }

      const normalized = item.trim().toLowerCase();
      extensions.push(normalized.startsWith('.') ? normalized : `.${normalized}`);
    }
    return extensions;
  }

  function normalizeGroupId(rawId) {
    if (typeof rawId !== 'string') {
      return '';
    }
    return rawId.trim();
  }

  function setLoaderManifest(manifest) {
    loaderManifest = manifest;
    navigationDocument = manifest?.navigationDocument ?? null;
    requiredResourcesByPath.clear();
    optionalResourcesByPath.clear();
    optionalGroupMaxBytes.clear();
    selectedOptionalPathByGroup.clear();
    externalResourcesByUrl.clear();
    externalMatchGroupsById.clear();
    selectedExternalResourcesByGroup.clear();
    countedResourceKeys.clear();
    observedResourceSizesByKey.clear();
    completedResourceSamples.length = 0;
    loadedTrackedBytes = 0;
    processedPerformanceEntries = 0;
    totalCompletedSampleBytes = 0;
    totalCompletedSampleDurationMs = 0;
    activePredictionWindow = null;

    if (!loaderManifest) {
      return;
    }

    for (const requiredResource of loaderManifest.requiredResources) {
      requiredResourcesByPath.set(requiredResource.path, requiredResource.sizeBytes);
    }

    for (const optionalGroup of loaderManifest.optionalGroups) {
      optionalGroupMaxBytes.set(optionalGroup.id, optionalGroup.maxCandidateBytes);
      for (const candidate of optionalGroup.candidates) {
        optionalResourcesByPath.set(candidate.path, {
          groupId: optionalGroup.id,
          sizeBytes: candidate.sizeBytes,
        });
      }
    }

    for (const externalResource of loaderManifest.externalResources) {
      externalResourcesByUrl.set(externalResource.url, externalResource.sizeBytes);
    }

    for (const externalMatchGroup of loaderManifest.externalMatchGroups) {
      externalMatchGroupsById.set(externalMatchGroup.id, externalMatchGroup);
    }

    collectLoadedBytesFromPerformance();
  }

  function requestProgressFrame() {
    if (progressFrameRequestId != null) {
      return;
    }

    progressFrameRequestId = window.requestAnimationFrame((frameTimeMs) => {
      progressFrameRequestId = null;
      tickProgress(frameTimeMs);
      if (!loaderDismissed && loader) {
        requestProgressFrame();
      }
    });
  }

  function tickProgress(frameTimeMs) {
    collectLoadedBytesFromPerformance();
    const targetProgress = computeTargetProgress(frameTimeMs);
    animateProgressTo(targetProgress, frameTimeMs);
  }

  function observeLoadedBytes(resourceKey, loadedBytes, timingSample) {
    const normalizedSize = normalizePositiveInt(loadedBytes);
    if (!resourceKey || normalizedSize <= 0 || countedResourceKeys.has(resourceKey)) {
      return false;
    }

    countedResourceKeys.add(resourceKey);
    observedResourceSizesByKey.set(resourceKey, normalizedSize);
    loadedTrackedBytes += normalizedSize;
    recordCompletedResourceSample(normalizedSize, timingSample);
    return true;
  }

  function recordCompletedResourceSample(loadedBytes, timingSample) {
    const normalizedSize = normalizePositiveInt(loadedBytes);
    if (normalizedSize <= 0) {
      return;
    }

    const completedAtMs = normalizePositiveMs(timingSample?.completedAtMs) || nowMs();
    const durationMs =
      normalizePositiveMs(timingSample?.durationMs) ||
      estimateResourceDurationMs(normalizedSize);
    const effectiveDurationMs = clamp(durationMs, 24, 12000);

    completedResourceSamples.push({
      bytes: normalizedSize,
      durationMs: effectiveDurationMs,
      startAtMs: Math.max(0, completedAtMs - effectiveDurationMs),
      endAtMs: completedAtMs,
    });
    totalCompletedSampleBytes += normalizedSize;
    totalCompletedSampleDurationMs += effectiveDurationMs;

    while (completedResourceSamples.length > 24) {
      const removedSample = completedResourceSamples.shift();
      totalCompletedSampleBytes -= removedSample?.bytes ?? 0;
      totalCompletedSampleDurationMs -= removedSample?.durationMs ?? 0;
    }

    restartPredictionWindow();
  }

  function estimateResourceDurationMs(loadedBytes) {
    const throughputBytesPerMs = computeAverageObservedThroughputBytesPerMs();
    if (throughputBytesPerMs > 0) {
      return loadedBytes / throughputBytesPerMs;
    }
    return 420;
  }

  function createTimingSample(entry) {
    return {
      completedAtMs: resolveEntryCompletedAtMs(entry),
      durationMs: resolveEntryDurationMs(entry),
    };
  }

  function resolveEntryCompletedAtMs(entry) {
    const responseEndMs = normalizePositiveMs(entry?.responseEnd);
    if (responseEndMs > 0) {
      return responseEndMs;
    }

    const startTimeMs = normalizePositiveMs(entry?.startTime);
    const durationMs = normalizePositiveMs(entry?.duration);
    if (startTimeMs > 0 && durationMs > 0) {
      return startTimeMs + durationMs;
    }

    return nowMs();
  }

  function resolveEntryDurationMs(entry) {
    const responseEndMs = normalizePositiveMs(entry?.responseEnd);
    const startTimeMs = normalizePositiveMs(entry?.startTime);
    if (responseEndMs > 0 && startTimeMs >= 0 && responseEndMs >= startTimeMs) {
      return responseEndMs - startTimeMs;
    }

    return normalizePositiveMs(entry?.duration);
  }

  function collectLoadedBytesFromPerformance() {
    if (!loaderManifest || typeof performance === 'undefined') {
      return;
    }

    if (navigationDocument && !countedResourceKeys.has('navigation_document')) {
      const navigationEntries = performance.getEntriesByType('navigation');
      if (Array.isArray(navigationEntries) && navigationEntries.length > 0) {
        const navigationBytes = resolveLoadedBytes(
          navigationEntries[0],
          navigationDocument.sizeBytes,
        );
        observeLoadedBytes(
          'navigation_document',
          navigationBytes,
          createTimingSample(navigationEntries[0]),
        );
      }
    }

    const entries = performance.getEntriesByType('resource');
    if (!Array.isArray(entries) || entries.length === 0) {
      return;
    }

    for (let i = processedPerformanceEntries; i < entries.length; i += 1) {
      const entry = entries[i];
      const descriptor = normalizeResourceDescriptor(entry.name);
      if (!descriptor) {
        continue;
      }

      if (descriptor.sameOriginPath) {
        const requiredSize = requiredResourcesByPath.get(descriptor.sameOriginPath);
        if (requiredSize) {
          observeLoadedBytes(
            `local:${descriptor.sameOriginPath}`,
            resolveLoadedBytes(entry, requiredSize),
            createTimingSample(entry),
          );
          continue;
        }

        const optionalResource = optionalResourcesByPath.get(descriptor.sameOriginPath);
        if (optionalResource) {
          const selectedPath = selectedOptionalPathByGroup.get(optionalResource.groupId);
          if (!selectedPath) {
            selectedOptionalPathByGroup.set(
              optionalResource.groupId,
              descriptor.sameOriginPath,
            );
          }

          if (
            selectedOptionalPathByGroup.get(optionalResource.groupId) !==
            descriptor.sameOriginPath
          ) {
            continue;
          }

          observeLoadedBytes(
            `local:${descriptor.sameOriginPath}`,
            resolveLoadedBytes(entry, optionalResource.sizeBytes),
            createTimingSample(entry),
          );
          continue;
        }
      }

      const externalSize = externalResourcesByUrl.get(descriptor.absoluteUrl);
      if (externalSize) {
        observeLoadedBytes(
          `external:${descriptor.absoluteUrl}`,
          resolveLoadedBytes(entry, externalSize),
          createTimingSample(entry),
        );
        continue;
      }

      const externalMatchGroup = matchExternalMatchGroup(descriptor);
      if (!externalMatchGroup) {
        continue;
      }

      let selectedResources = selectedExternalResourcesByGroup.get(
        externalMatchGroup.id,
      );
      if (!selectedResources) {
        selectedResources = [];
        selectedExternalResourcesByGroup.set(externalMatchGroup.id, selectedResources);
      }

      if (
        selectedResources.some((resource) => resource.url === descriptor.absoluteUrl) ||
        selectedResources.length >= externalMatchGroup.maxMatches
      ) {
        continue;
      }

      const resolvedBytes = resolveLoadedBytes(
        entry,
        externalMatchGroup.maxCandidateBytes,
      );
      selectedResources.push({
        url: descriptor.absoluteUrl,
        sizeBytes: resolvedBytes,
      });
      observeLoadedBytes(
        `external-group:${externalMatchGroup.id}:${descriptor.absoluteUrl}`,
        resolvedBytes,
        createTimingSample(entry),
      );
    }

    processedPerformanceEntries = entries.length;
    ensurePredictionWindow();
  }

  function resolveLoadedBytes(entry, fallbackBytes) {
    const decodedBodySize = normalizePositiveInt(entry.decodedBodySize);
    if (decodedBodySize > 0) {
      return decodedBodySize;
    }

    const encodedBodySize = normalizePositiveInt(entry.encodedBodySize);
    if (encodedBodySize > 0) {
      return encodedBodySize;
    }

    const transferSize = normalizePositiveInt(entry.transferSize);
    if (transferSize > 0) {
      return transferSize;
    }

    return fallbackBytes;
  }

  function computeAverageObservedThroughputBytesPerMs() {
    if (totalCompletedSampleBytes <= 0 || totalCompletedSampleDurationMs <= 0) {
      return 0;
    }

    const globalThroughputBytesPerMs =
      totalCompletedSampleBytes / totalCompletedSampleDurationMs;
    const recentSamples = completedResourceSamples.slice(-6);

    let recentBytes = 0;
    let recentDurationMs = 0;
    for (const recentSample of recentSamples) {
      recentBytes += recentSample.bytes;
      recentDurationMs += recentSample.durationMs;
    }

    if (recentBytes <= 0 || recentDurationMs <= 0) {
      return globalThroughputBytesPerMs;
    }

    const recentThroughputBytesPerMs = recentBytes / recentDurationMs;
    return clamp(
      globalThroughputBytesPerMs * 0.68 + recentThroughputBytesPerMs * 0.32,
      globalThroughputBytesPerMs * 0.7,
      Math.max(globalThroughputBytesPerMs, recentThroughputBytesPerMs) * 1.2,
    );
  }

  function estimatePredictionParallelism() {
    const recentSamples = completedResourceSamples.slice(-8);
    if (recentSamples.length < 2) {
      return 1;
    }

    let earliestStartAtMs = Number.POSITIVE_INFINITY;
    let latestEndAtMs = 0;
    let totalDurationMs = 0;
    for (const recentSample of recentSamples) {
      earliestStartAtMs = Math.min(earliestStartAtMs, recentSample.startAtMs);
      latestEndAtMs = Math.max(latestEndAtMs, recentSample.endAtMs);
      totalDurationMs += recentSample.durationMs;
    }

    const wallSpanMs = Math.max(1, latestEndAtMs - earliestStartAtMs);
    return clamp(totalDurationMs / wallSpanMs, 1, 3);
  }

  function ensurePredictionWindow() {
    if (activePredictionWindow || completedResourceSamples.length === 0) {
      return;
    }

    restartPredictionWindow();
  }

  function restartPredictionWindow() {
    const pendingQueue = buildPendingPredictionQueue();
    if (pendingQueue.length === 0) {
      activePredictionWindow = null;
      return;
    }

    const throughputBytesPerMs = computeAverageObservedThroughputBytesPerMs();
    if (throughputBytesPerMs <= 0) {
      activePredictionWindow = null;
      return;
    }

    const parallelism = estimatePredictionParallelism();
    const predictedBytesPerMs = throughputBytesPerMs * parallelism;
    const targetChunkBytes =
      predictedBytesPerMs * computePredictionWindowMs(parallelism, pendingQueue.length);
    const bytesBudget = selectPredictionChunkBytes(
      pendingQueue,
      targetChunkBytes,
      parallelism,
    );

    if (bytesBudget <= 0) {
      activePredictionWindow = null;
      return;
    }

    activePredictionWindow = {
      startConfirmedBytes: loadedTrackedBytes,
      startTimeMs: nowMs(),
      bytesBudget,
      expectedDurationMs: clamp(
        bytesBudget / Math.max(predictedBytesPerMs, 0.01),
        260,
        2400,
      ),
    };
  }

  function computePredictionWindowMs(parallelism, pendingItemCount) {
    return clamp(
      560 + (parallelism - 1) * 140 + Math.min(160, pendingItemCount * 8),
      480,
      980,
    );
  }

  function buildPendingPredictionQueue() {
    const queue = [];

    if (navigationDocument && !countedResourceKeys.has('navigation_document')) {
      pushPendingPredictionItem(
        queue,
        'navigation_document',
        navigationDocument.sizeBytes,
        5,
      );
    }

    for (const [path, sizeBytes] of requiredResourcesByPath.entries()) {
      pushPendingPredictionItem(
        queue,
        `local:${path}`,
        sizeBytes,
        getLocalResourcePriority(path),
      );
    }

    for (const [groupId, groupMaxBytes] of optionalGroupMaxBytes.entries()) {
      const selectedPath = selectedOptionalPathByGroup.get(groupId);
      if (selectedPath) {
        const selectedResource = optionalResourcesByPath.get(selectedPath);
        pushPendingPredictionItem(
          queue,
          `local:${selectedPath}`,
          selectedResource?.sizeBytes ?? groupMaxBytes,
          getLocalResourcePriority(selectedPath),
        );
        continue;
      }

      pushPendingPredictionItem(
        queue,
        `optional-group:${groupId}`,
        groupMaxBytes,
        getOptionalGroupPriority(groupId),
      );
    }

    for (const [url, sizeBytes] of externalResourcesByUrl.entries()) {
      pushPendingPredictionItem(
        queue,
        `external:${url}`,
        sizeBytes,
        getExternalResourcePriority(url),
      );
    }

    for (const externalMatchGroup of externalMatchGroupsById.values()) {
      const selectedResources = selectedExternalResourcesByGroup.get(
        externalMatchGroup.id,
      ) ?? [];
      const remainingMatches = Math.max(
        0,
        externalMatchGroup.maxMatches - selectedResources.length,
      );

      for (let index = 0; index < remainingMatches; index += 1) {
        pushPendingPredictionItem(
          queue,
          `external-group:${externalMatchGroup.id}:pending:${index}`,
          externalMatchGroup.maxCandidateBytes,
          getExternalMatchGroupPriority(externalMatchGroup.id),
        );
      }
    }

    queue.sort((left, right) => {
      if (left.priority !== right.priority) {
        return left.priority - right.priority;
      }
      return right.sizeBytes - left.sizeBytes;
    });

    return queue;
  }

  function pushPendingPredictionItem(queue, resourceKey, sizeBytes, priority) {
    if (countedResourceKeys.has(resourceKey)) {
      return;
    }

    const normalizedSize = normalizePositiveInt(sizeBytes);
    if (normalizedSize <= 0) {
      return;
    }

    queue.push({
      key: resourceKey,
      sizeBytes: normalizedSize,
      priority,
    });
  }

  function selectPredictionChunkBytes(pendingQueue, targetChunkBytes, parallelism) {
    if (!Array.isArray(pendingQueue) || pendingQueue.length === 0) {
      return 0;
    }

    const softTargetBytes = Math.max(pendingQueue[0].sizeBytes, targetChunkBytes);
    const firstPriority = pendingQueue[0].priority;
    const maxItems = Math.max(2, Math.round(parallelism * 3));

    let chunkBytes = pendingQueue[0].sizeBytes;
    let chunkItems = 1;

    for (let index = 1; index < pendingQueue.length; index += 1) {
      const pendingItem = pendingQueue[index];
      const priorityGap = pendingItem.priority - firstPriority;
      const alreadyNearTarget = chunkBytes >= softTargetBytes * 0.9;
      const crossedPriorityBoundary =
        priorityGap >= 18 && chunkBytes >= softTargetBytes * 0.55;
      const reachedItemLimit =
        chunkItems >= maxItems && chunkBytes >= softTargetBytes * 0.55;

      if (crossedPriorityBoundary || reachedItemLimit) {
        break;
      }

      if (alreadyNearTarget && pendingItem.sizeBytes > softTargetBytes * 0.2) {
        break;
      }

      chunkBytes += pendingItem.sizeBytes;
      chunkItems += 1;

      if (chunkBytes >= softTargetBytes * 1.1) {
        break;
      }
    }

    return chunkBytes;
  }

  function getLocalResourcePriority(path) {
    const normalizedPath = String(path ?? '').toLowerCase();

    if (normalizedPath === 'main.dart.js') {
      return 10;
    }
    if (
      normalizedPath.includes('canvaskit') ||
      normalizedPath.includes('skwasm')
    ) {
      return 20;
    }
    if (normalizedPath.includes('assetmanifest')) {
      return 28;
    }
    if (normalizedPath.endsWith('fontmanifest.json')) {
      return 32;
    }
    if (
      normalizedPath.endsWith('.ttf') ||
      normalizedPath.endsWith('.otf') ||
      normalizedPath.endsWith('.woff') ||
      normalizedPath.endsWith('.woff2')
    ) {
      return 38;
    }
    if (normalizedPath.includes('splash')) {
      return 44;
    }
    if (normalizedPath.endsWith('loader_manifest.json')) {
      return 52;
    }
    if (normalizedPath.endsWith('version.json')) {
      return 56;
    }
    if (normalizedPath.endsWith('manifest.json')) {
      return 60;
    }
    if (normalizedPath.includes('/icons/')) {
      return 82;
    }
    if (normalizedPath.endsWith('favicon.ico') || normalizedPath.endsWith('favicon.png')) {
      return 84;
    }

    return 66;
  }

  function getOptionalGroupPriority(groupId) {
    switch (groupId) {
      case 'renderer_js':
        return 18;
      case 'renderer_wasm':
        return 22;
      case 'asset_manifest':
        return 28;
      case 'pwa_icon':
        return 82;
      default:
        return 70;
    }
  }

  function getExternalResourcePriority(url) {
    const normalizedUrl = String(url ?? '').toLowerCase();
    if (normalizedUrl.includes('firebase-app.js')) {
      return 24;
    }
    if (
      normalizedUrl.includes('firebase-auth.js') ||
      normalizedUrl.includes('firebase-firestore.js') ||
      normalizedUrl.includes('firebase-storage.js')
    ) {
      return 26;
    }
    if (normalizedUrl.includes('accounts.google.com/gsi/client')) {
      return 34;
    }
    return 50;
  }

  function getExternalMatchGroupPriority(groupId) {
    if (groupId === 'google_hosted_font') {
      return 40;
    }
    return 58;
  }

  function computePredictedTrackedBytes(frameTimeMs) {
    ensurePredictionWindow();
    if (!activePredictionWindow) {
      return loadedTrackedBytes;
    }

    const elapsedMs = Math.max(
      0,
      (normalizePositiveMs(frameTimeMs) || nowMs()) - activePredictionWindow.startTimeMs,
    );
    const predictedBytes =
      activePredictionWindow.bytesBudget *
      clamp(
        elapsedMs / activePredictionWindow.expectedDurationMs,
        0,
        1,
      );

    return Math.max(
      loadedTrackedBytes,
      activePredictionWindow.startConfirmedBytes + predictedBytes,
    );
  }

  function normalizePositiveMs(value) {
    if (typeof value === 'number' && Number.isFinite(value) && value > 0) {
      return value;
    }

    if (typeof value === 'string' && value.trim() !== '') {
      const parsed = Number(value);
      if (Number.isFinite(parsed) && parsed > 0) {
        return parsed;
      }
    }

    return 0;
  }

  function clamp(value, minValue, maxValue) {
    return Math.min(maxValue, Math.max(minValue, value));
  }

  function nowMs() {
    if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
      return performance.now();
    }
    return Date.now();
  }

  function normalizePositiveInt(value) {
    if (typeof value === 'number' && Number.isFinite(value) && value > 0) {
      return Math.round(value);
    }

    if (typeof value === 'string' && value.trim() !== '') {
      const parsed = Number(value);
      if (Number.isFinite(parsed) && parsed > 0) {
        return Math.round(parsed);
      }
    }

    return 0;
  }

  function normalizeBasePath(pathname) {
    let normalized = pathname || '/';
    if (!normalized.startsWith('/')) {
      normalized = `/${normalized}`;
    }
    if (!normalized.endsWith('/')) {
      normalized = `${normalized}/`;
    }
    return normalized;
  }

  function normalizeResourceDescriptor(resourceUrl) {
    try {
      const parsedUrl = new URL(resourceUrl, window.location.href);
      parsedUrl.hash = '';

      let sameOriginPath = null;
      if (parsedUrl.origin === window.location.origin) {
        let pathname = parsedUrl.pathname;
        if (pathname.startsWith(basePath)) {
          pathname = pathname.slice(basePath.length);
        }
        while (pathname.startsWith('/')) {
          pathname = pathname.slice(1);
        }
        if (pathname) {
          sameOriginPath = decodeURIComponent(pathname);
        }
      }

      return {
        absoluteUrl: parsedUrl.href,
        sameOriginPath,
        pathname: decodeURIComponent(parsedUrl.pathname || ''),
      };
    } catch (_) {
      return null;
    }
  }

  function matchExternalMatchGroup(descriptor) {
    const pathnameLower = descriptor.pathname.toLowerCase();

    for (const externalMatchGroup of externalMatchGroupsById.values()) {
      if (
        !externalMatchGroup.urlPrefixes.some((prefix) =>
          descriptor.absoluteUrl.startsWith(prefix),
        )
      ) {
        continue;
      }

      if (
        externalMatchGroup.extensions.length > 0 &&
        !externalMatchGroup.extensions.some((extension) =>
          pathnameLower.endsWith(extension),
        )
      ) {
        continue;
      }

      return externalMatchGroup;
    }

    return null;
  }

  function computeTargetProgress(frameTimeMs) {
    const currentFrameTimeMs = normalizePositiveMs(frameTimeMs) || nowMs();
    const fallbackFloor = Math.min(
      36,
      4 + (currentFrameTimeMs - loaderStartTimeMs) / 240,
    );
    let targetProgress = fallbackFloor;

    const measuredProgress = computeMeasuredProgress(currentFrameTimeMs);
    if (measuredProgress == null) {
      const timedFallbackProgress = Math.min(
        88,
        6 + (currentFrameTimeMs - loaderStartTimeMs) / 115,
      );
      targetProgress = Math.max(targetProgress, timedFallbackProgress);
    } else {
      targetProgress = Math.max(targetProgress, measuredProgress);
    }

    if (loaderCanDismiss) {
      targetProgress = Math.max(targetProgress, 98);
    }
    if (loaderDismissed) {
      targetProgress = 100;
    }

    return Math.min(100, targetProgress);
  }

  function computeMeasuredProgress(frameTimeMs) {
    if (!loaderManifest) {
      return null;
    }

    const expectedTotalBytes = computeExpectedTotalBytes();
    if (expectedTotalBytes <= 0) {
      return null;
    }

    const predictedTrackedBytes = computePredictedTrackedBytes(frameTimeMs);
    const progressRatio = Math.min(1, predictedTrackedBytes / expectedTotalBytes);
    return 4 + progressRatio * 90;
  }

  function computeExpectedTotalBytes() {
    let expectedTotalBytes = 0;

    if (navigationDocument) {
      expectedTotalBytes +=
        observedResourceSizesByKey.get('navigation_document') ??
        navigationDocument.sizeBytes;
    }

    for (const [path, sizeBytes] of requiredResourcesByPath.entries()) {
      expectedTotalBytes +=
        observedResourceSizesByKey.get(`local:${path}`) ?? sizeBytes;
    }

    for (const [groupId, groupMaxBytes] of optionalGroupMaxBytes.entries()) {
      const selectedPath = selectedOptionalPathByGroup.get(groupId);
      if (!selectedPath) {
        expectedTotalBytes += groupMaxBytes;
        continue;
      }

      const selectedResource = optionalResourcesByPath.get(selectedPath);
      expectedTotalBytes +=
        observedResourceSizesByKey.get(`local:${selectedPath}`) ??
        selectedResource?.sizeBytes ??
        groupMaxBytes;
    }

    for (const [url, sizeBytes] of externalResourcesByUrl.entries()) {
      expectedTotalBytes +=
        observedResourceSizesByKey.get(`external:${url}`) ?? sizeBytes;
    }

    for (const externalMatchGroup of externalMatchGroupsById.values()) {
      const selectedResources = selectedExternalResourcesByGroup.get(
        externalMatchGroup.id,
      ) ?? [];

      for (const selectedResource of selectedResources) {
        expectedTotalBytes +=
          observedResourceSizesByKey.get(
            `external-group:${externalMatchGroup.id}:${selectedResource.url}`,
          ) ?? selectedResource.sizeBytes;
      }

      const remainingMatches = Math.max(
        0,
        externalMatchGroup.maxMatches - selectedResources.length,
      );
      expectedTotalBytes += remainingMatches * externalMatchGroup.maxCandidateBytes;
    }

    return expectedTotalBytes;
  }

  function animateProgressTo(targetProgress, frameTimeMs) {
    const currentFrameTimeMs = normalizePositiveMs(frameTimeMs) || nowMs();
    const frameDeltaMs = clamp(currentFrameTimeMs - lastRenderedFrameMs, 8, 64);
    lastRenderedFrameMs = currentFrameTimeMs;

    if (targetProgress <= currentProgressPercent) {
      renderProgress(currentProgressPercent);
      return;
    }

    const delta = targetProgress - currentProgressPercent;
    const smoothingMs = loaderCanDismiss ? 92 : 165;
    const interpolation = 1 - Math.exp(-frameDeltaMs / smoothingMs);
    const rawStep = delta * interpolation;
    const minimumStep = (loaderCanDismiss ? 0.22 : 0.05) * (frameDeltaMs / 16.67);
    const maximumStep = (loaderCanDismiss ? 2.6 : 1.15) * (frameDeltaMs / 16.67);
    const step = clamp(rawStep, minimumStep, maximumStep);
    currentProgressPercent = Math.min(targetProgress, currentProgressPercent + step);
    renderProgress(currentProgressPercent);
  }

  function renderProgress(progressPercent) {
    const clampedProgress = Math.max(0, Math.min(100, progressPercent));
    const roundedProgress = Math.round(clampedProgress);

    if (loaderProgressFill) {
      loaderProgressFill.style.width = `${clampedProgress.toFixed(2)}%`;
    }

    if (loaderProgressText) {
      loaderProgressText.textContent = `${roundedProgress}%`;
    }

    if (loaderProgress) {
      loaderProgress.setAttribute('aria-valuenow', `${roundedProgress}`);
    }
  }

  function setProgressImmediate(progressPercent) {
    currentProgressPercent = Math.max(0, Math.min(100, progressPercent));
    renderProgress(currentProgressPercent);
  }

  function stopProgressTimer() {
    if (progressFrameRequestId != null) {
      window.cancelAnimationFrame(progressFrameRequestId);
      progressFrameRequestId = null;
    }
  }

  function validateCopyCoverage() {
    for (const localeKey of supportedWebLoaderLocales) {
      const localeCopy = copyByLocale[localeKey];
      if (
        !localeCopy ||
        !localeCopy.appName ||
        !localeCopy.loadingWebApp ||
        !localeCopy.loadingFailed ||
        !localeCopy.errorHint ||
        !localeCopy.progressAriaLabel ||
        !localeCopy.versionPrefix ||
        !localeCopy.versionFallback
      ) {
        console.warn(
          `[web-loader] Missing translation for locale "${localeKey}". ` +
            'Add copy in web/flutter_bootstrap.js when adding a new app locale.',
        );
      }
    }
  }

  function handleBootstrapFailure() {
    if (loaderDismissed) {
      return;
    }

    stopProgressTimer();
    if (loaderSubtitle) {
      loaderSubtitle.textContent = copy.loadingFailed;
    }
    if (loaderProgressText) {
      loaderProgressText.textContent = copy.errorHint;
    }
  }

  function observeFlutterReady() {
    if (!loader || loaderDismissed) {
      return;
    }

    if (!observer) {
      observer = new MutationObserver(dismissLoaderWhenFlutterReady);
      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    }
  }

  function dismissLoaderWhenFlutterReady() {
    if (
      !loaderCanDismiss ||
      loaderDismissed ||
      !document.querySelector(flutterReadySelector)
    ) {
      return;
    }

    loaderDismissed = true;
    stopProgressTimer();
    setProgressImmediate(100);
    observer?.disconnect();
    document.body.classList.add('app-loaded');
    window.setTimeout(() => loader?.remove(), 320);
  }
})();
