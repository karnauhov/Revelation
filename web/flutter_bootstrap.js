// @ts-nocheck
{{flutter_js}}
{{flutter_build_config}}

(() => {
  const loader = document.getElementById('app-loader');
  const title = document.getElementById('app-loader-title');
  const subtitle = document.getElementById('app-loader-subtitle');
  const status = document.getElementById('app-loader-status');
  const progress = document.getElementById('app-loader-progress');
  const progressFill = document.getElementById('app-loader-progress-fill');
  const progressText = document.getElementById('app-loader-progress-text');

  const copyByLocale = {
    en: {
      appName: 'Revelation',
      startupTitle: 'Launching the app...',
      stagePreparing: 'Preparing Revelation',
      stageDownloading: 'Downloading the web app',
      stageStarting: 'Starting the application engine',
      stageOpening: 'Opening Revelation',
      stageError: 'We could not finish loading the app.',
      progressLabel: 'Step {current} of {total}',
      errorHint: 'Please refresh the page and try again.',
    },
    es: {
      appName: 'Apocalipsis',
      startupTitle: 'Iniciando la aplicación...',
      stagePreparing: 'Preparando Apocalipsis',
      stageDownloading: 'Descargando la aplicación web',
      stageStarting: 'Iniciando el motor de la aplicación',
      stageOpening: 'Abriendo Apocalipsis',
      stageError: 'No pudimos completar la carga de la aplicación.',
      progressLabel: 'Paso {current} de {total}',
      errorHint: 'Actualice la página e inténtelo de nuevo.',
    },
    ru: {
      appName: 'Откровение',
      startupTitle: 'Запуск приложения...',
      stagePreparing: 'Подготавливаем Откровение',
      stageDownloading: 'Загружаем веб-приложение',
      stageStarting: 'Запускаем движок приложения',
      stageOpening: 'Открываем Откровение',
      stageError: 'Не удалось завершить загрузку приложения.',
      progressLabel: 'Шаг {current} из {total}',
      errorHint: 'Пожалуйста, обновите страницу и попробуйте снова.',
    },
    uk: {
      appName: "Об'явлення",
      startupTitle: 'Запуск застосунку...',
      stagePreparing: "Підготовлюємо Об'явлення",
      stageDownloading: 'Завантажуємо веб-застосунок',
      stageStarting: 'Запускаємо рушій застосунку',
      stageOpening: "Відкриваємо Об'явлення",
      stageError: 'Не вдалося завершити завантаження застосунку.',
      progressLabel: 'Крок {current} із {total}',
      errorHint: 'Будь ласка, оновіть сторінку та спробуйте ще раз.',
    },
  };

  const stages = {
    preparing: { progress: 12, step: 1, statusKey: 'stagePreparing' },
    downloading: { progress: 42, step: 2, statusKey: 'stageDownloading' },
    starting: { progress: 74, step: 3, statusKey: 'stageStarting' },
    opening: { progress: 96, step: 4, statusKey: 'stageOpening' },
    error: { progress: 100, step: 4, statusKey: 'stageError', error: true },
  };

  const flutterReadySelector = 'flutter-view, flt-glass-pane';
  const totalStages = 4;
  const locale = resolveLocale();
  const copy = copyByLocale[locale];
  let loaderCanDismiss = false;
  let loaderDismissed = false;
  let observer;

  applyCopy(copy);
  setLoaderStage('downloading');

  _flutter.loader.load({
    serviceWorkerSettings: {
      serviceWorkerVersion: String(
          '{{flutter_service_worker_version}}'.replace(/^"|"$/g, '')),
    },
    onEntrypointLoaded: async function (engineInitializer) {
      try {
        setLoaderStage('starting');
        const appRunner = await engineInitializer.initializeEngine();
        setLoaderStage('opening');
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
    const language = navigator.language.toLowerCase();
    if (language.startsWith('es')) {
      return 'es';
    }
    if (language.startsWith('ru')) {
      return 'ru';
    }
    if (language.startsWith('uk')) {
      return 'uk';
    }
    return 'en';
  }

  function applyCopy(currentCopy) {
    document.documentElement.lang = locale;
    if (title) {
      title.textContent = currentCopy.appName;
    }
    if (subtitle) {
      subtitle.textContent = currentCopy.startupTitle;
    }
  }

  function setLoaderStage(stageKey) {
    const stage = stages[stageKey];
    if (!stage) {
      return;
    }

    if (status) {
      status.textContent = copy[stage.statusKey];
    }
    if (progressFill) {
      progressFill.style.width = `${stage.progress}%`;
    }
    if (progress) {
      progress.setAttribute('aria-valuenow', `${stage.progress}`);
    }
    if (progressText) {
      progressText.textContent = stage.error
          ? copy.errorHint
          : copy.progressLabel
                .replace('{current}', `${stage.step}`)
                .replace('{total}', `${totalStages}`);
    }
    if (loader) {
      loader.dataset.stage = stageKey;
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
    observer?.disconnect();
    document.body.classList.add('app-loaded');
    window.setTimeout(() => loader?.remove(), 360);
  }

  function handleBootstrapFailure() {
    if (loaderDismissed) {
      return;
    }
    setLoaderStage('error');
  }
})();
