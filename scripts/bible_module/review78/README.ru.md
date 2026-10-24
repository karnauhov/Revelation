# OH1988 — development manual review

Локальный workbench показывает 5782 существующих development error cases из taxonomy 7.8: 4311 `B_review`, 1471 `C_unresolved`, 1257 стихов. Это отобранные известные ошибки folds 0–2; по ним нельзя оценивать precision класса или проводить независимый аудит.

Из корня репозитория запустить:

```powershell
python -X utf8 -B -m scripts.bible_module.review78 serve --port 8878
```

Затем открыть [Manual review](http://127.0.0.1:8878). Остановка сервера — `Ctrl+C`. Сервер привязан к `127.0.0.1`, обслуживает только чтение; новых dependencies нет. При запуске проверяются source/input locks, затем при запросах — текущие hashes index/manifest/packet. Source inputs проверяются на старте: открытая сессия относится к этому замороженному snapshot.

В левой колонке выбрать класс, taxonomy и стих/украинское слово. Справа показаны точный OH1988-текст, frozen prediction и каждая ближайшая gold-группа отдельно, включая все ties. Жёлтым выделены недостающие endpoints, красным — лишние endpoints prediction относительно этой конкретной группы. `∅` обозначает пустой набор при сравнении; явный NULL показывается только с исходным relation/null_reason.

Раздел «Конфликтующие hyperedges» сохраняет полные группы всех конфликтующих eligible candidates. Полные n-best decompositions и все historical gold-группы доступны отдельно. Reciprocal shared declarations считаются совместимыми согласно frozen 7.6 contract; они не превращаются в конфликты и не сливаются. Рёбра с deferred endpoints исключены целиком, зарегистрированные deferrals не переоткрываются.

В `Source evidence` доступны generator/input channel, полные evidence/provenance, dependency groups, candidate IDs, original source locators, lemma/morphology/Strong исходного слоя, SHA/commit и точные OH1988 scalar/byte spans. Производные одного источника сохраняют общую dependency group; source Strong не означает нового назначения украинскому тексту.

Заметки reviewer сохраняются в памяти текущей вкладки при переключении случаев. До закрытия вкладки скачать нужные черновики кнопкой «Скачать черновик review». Экспорт содержит reviewer, rationale, полную semantic identity, graph/gold/packet/build digests и признаки `is_label=false`, `is_override=false`. Заметки не записываются сервером и не применяются к gold или production. Автоматического принятия links нет: `A_auto=0`.

Сборка уже выполнена в `scripts/bible_module/work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/build.v1`. Полные packets остаются в gitignored work. Команды `lock` и `build` эксклюзивны и служат воспроизведению протокола; повторная запись существующих outputs запрещена. При изменившемся digest viewer отклоняет запрос, не пересобирает и не меняет решение автоматически.

[Проверенный отчёт](../reports/ukrainian_stage_7_20260801/review78.v1.ru.md) · [предыдущая taxonomy](../reports/ukrainian_stage_7_20260801/precision78_development_taxonomy.v1.ru.md).
