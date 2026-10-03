# Exact consensus correction Nah.1.10 — v1, 2026-10-03

Выполнена новая correction двух решений по sealed proposal
`gold7:correction-proposal:group001:Nah.1.10:v1:20261003`.
[Correction manifest](gold_group_001_Nah.correction.v1.manifest.json), SHA-256
`ffbc5e908839995dcb66b9ed1241af9489ec85c1d932be18e3b0eafff6178e91`,
фиксирует physical inputs/outputs, роли, exact supersedes и воспроизведение.

Изменены только:

- `original:gold7:original:92ee1c43bc08d4efdde3892564674eb1`:
  selected MT `עד`/`H5704`, o002, меняет NULL на `one_to_one` к exact OH1988
  `наче`, t004, `uk7:HIF:004:22:26`;
- `target:gold7:target:d297904ceebe75c4c22eb9a3777fa26f`:
  тот же `наче` меняет function accounting на reciprocal aligned accounting
  к `tahot:dda2e598e3ebfe6da975d39c0a2c4875415531ef57476a7974ce9c1fcd06e594:g01:a01`.

Основание взято из sealed
[independent content QC](gold_group_001_independent_content_qc.v1.ru.md):
[BDB I.3](https://biblehub.com/hebrew/5704.htm) и
[NET Nahum 1:10, note 10](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10)
поддерживают comparative occurrence `עד` в этом стихе. Correction реализует
уже сохранённое definite-error proposal; она не меняет selected source layer.
Maqaf o003 остаётся NULL, `той` t005 остаётся function token; 32 прочих
решения Nah.1.10 и все остальные строки сохранены.

Corrector `codex-consensus-corrector-group001-20261003-isolated01` работал
в отдельном контексте без авторской истории прежних passes/adjudication/
blocking QC/opinion. Role attestation и input locks проверены до полного
чтения work JSONL. Эта роль является автором нового correction и **не является
independent QC собственных исправлений**. Предел независимости — доступная
история выполнения; новый ID или дата сами по себе её не доказывают.

Stage3/4/5/6 checks и root baseline physical audit завершены до полного JSONL.
Live `seal-correction` и `check-correction` дали exit 0; сохранены
[точные CLI команды и результаты](../../work/ukrainian_stage_7_20260801/session_group1_20261003_closure_corrector_01/live_cli_results.v1.json).
132 input и 23 output physical locks, bytes/SHA совпали. Три воспроизведения
всех семи output files byte-identical; четыре manifest copies также совпали.
Full-grid display содержит 1 197 решений / 32 стиха, evidence всех 604 original
tokens и 593 target tokens; все 593 scalar/UTF-8 spans проверены.
Отдельный old→new diff фиксирует ровно две изменённые alignments.

Статус correction — `complete_manual_consensus_correction_pending_independent_qc`.
Пять Nah.1.8 uncertainties и все 16 source-choice blockers группы сохранены.
Требуется distinct actual independent post-correction full-grid content QC;
эта запись не подтверждает acceptance. Gold **36/66**, новых **0**, осталось
**30**. Immutable OH1988 text/comments/mapping/selection/folds, старые reviews
и frozen QC сохранены. NT, runtime/DB, commit/push не выполнялись.

Эта пояснительная запись создана после seal manifest и не входит в его output
locks; sealed manifest не переписывался.
