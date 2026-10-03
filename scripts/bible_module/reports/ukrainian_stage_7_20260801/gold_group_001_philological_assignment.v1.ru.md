# OH1988 7.4, группа № 1 — исследовательское задание v1

Дата: 2026-10-03. ID: `gold7:philology:group001:assignment:v1:20261003`.
Исполнитель: текущая сессия Codex, роль source research. Внешняя платная
экспертиза не предполагается. [Заключение](gold_group_001_philological_opinion.v1.ru.md)
и [manifest](gold_group_001_philological_opinion.v1.manifest.json).

## Вопрос исследования

Для Nah.1.8, Zeph.2.14, Zeph.3.17, Zech.11.7 и Zech.14.6 установить:
какие связи допускает неизменный selected MT, какие альтернативные леммы
подтверждены лексически, какие оригинальные tokens действительно засвидетельствованы
в данном стихе и где остаётся только ретроверсия. Отдельно решить, можно ли
обосновать сохранённое NULL/addition accounting относительно selected MT,
не выдавая его за доказательство исторического оригинала перевода.

Не требуется установить название точного исторического издания ради самого
названия. Требуются существование token, лемма/Strong и украинский span.
Нельзя объединять эти три утверждения в одно по сходству значения.

## Неизменные входы

- Edition `ohienko_1988`, code `OH1988`, target positions `31 102`.
- Mapping `oh1988-kjv-protestant-v1`; selection/folds неизменны.
- Stage-6 text SHA: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`.
- Stage-6 text manifest SHA: `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`.
- [Исходный групповой checkpoint](gold_group_001_source_resolution.v1.manifest.json),
  SHA `4374135c6b1b3417b4956f1474154ef91a6b316bffeca8ad0e95aa906e904365`.
- [Nah](gold_group_001_Nah.source_resolution.v1.manifest.json),
  [Zeph](gold_group_001_Zeph.source_resolution.v1.manifest.json),
  [Zech](gold_group_001_Zech.source_resolution.v1.manifest.json): exact stable IDs,
  source/target IDs, QC inputs/digests и conditional scopes.
- Полные grids только в ignored `work/ukrainian_stage_7_20260801/`
  `session_group1_20261003/*.bounded_final_grid.v1.jsonl`.

Исследуются ровно 16 frozen uncertain stable decisions; принятые строки
не переобъявляются ошибочными без locus-specific доказательства. Полный список
IDs сохранён в [запросе v1](gold_group_001_owner_request.ru.md) и в manifest
заключения; запрос остаётся историческим артефактом, а не требованием заказать
экспертизу владельцу.

## Метод и проверяемые конкурирующие гипотезы

1. Проверить stage 3/4/5/6 до scoped JSONL; затем physical SHA-locks и stage 7.
2. Для каждого locus сверить MT surface/lemma/morphology/Strong с pinned TAHOT,
   approved controls, точным сканом OH1988 и доступными авторскими примечаниями.
3. Сопоставить три гипотезы: буквальное или допустимое контекстуальное выражение
   selected MT; другое чтение/word division; украинское переоформление,
   допускающее явный NULL относительно selected MT.
4. Прочитать оригинально-языковые versional witnesses и аппарат. Различать
   напечатанный Greek token, предложенный Hebrew token и собственный вывод
   исследователя. Переводные мосты — диагностические, без переноса номера.
5. Проверить весь clause: referent possessive suffix, управление глагола,
   функцию preposition/article, относительное предложение и scope отрицания.
6. Разделить parsing/selection/classification, lexical variants,
   grammar-only variants, link/null/group uncertainty и frozen input damage.
7. Указать решения для всех текущих blockers, степень доказанности и условную
   область повторной проверки при source-layer change. Новый token получает
   собственный stable ID; MT ID не переименовывается в другую лемму.
8. Зафиксировать источники, права, digest локальных входов, rationale,
   supersedes и статус. Выпустить заключение воспроизводимо и проверить locks.

## Результат и граница приёмки

Результат — собственное исследовательское заключение с конкретными рекомендациями,
а не новая independent QC/correction submission. Оно не изменяет frozen QC
вердикты и не увеличивает accepted counter. При достаточных свидетельствах
следующий шаг — предусмотренная контрактом versioned correction/source overlay
и отдельный content QC с фактически независимым от проверяемых решений исполнителем.
Платная третья сторона не является условием контракта. Независимость контекста
и происхождения проверяемых решений надо доказать; одного нового reviewer ID
или новой даты недостаточно.

Если свидетельств недостаточно, сохранить точный пробел и продолжать доступное
исследование. Не заменять его просьбой владельцу найти неизвестный ему документ.
