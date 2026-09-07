# Этап 7 — текущий HANDOFF, рабочая точка 2026-09-08

> **CURRENT WORK POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Этап 8 и SQLite не начинались. Удалённый LLM-сервис
> на `COMP_NAZARA` по прямому указанию владельца остаётся остановленным и не
> должен запускаться или опрашиваться. Commit/push автоматически не выполнять.

## Состояние репозитория

- Последний commit владельца: `1cfd601` (`Advance stage 7 blind gold
  adjudication workflow [skip ci]`).
- В текущем worktree находятся stage-7 gold workflow, тесты, manifests и
  документация, а также отдельные пользовательские изменения
  `analysis_options.yaml` и `pubspec.lock`; последние не изменять и не
  восстанавливать без прямого указания владельца.
- Полные corpus/review/comparison/adjudication JSONL находятся только в
  gitignored `scripts/bible_module/work/ukrainian_stage_7_20260801/`.

## Неизменяемые входы

- edition/module/code: `ohienko_1988` / `ohienko_1988` / `OH1988`;
- canon/versification/mapping: `protestant_66` / `kjv_protestant` /
  `oh1988-kjv-protestant-v1`;
- target positions: `31 102`;
- stage-6 text SHA-256:
  `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- stage-6 manifest SHA-256:
  `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- stage-6 comments SHA-256:
  `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`;
- production Strong assignments/markers и `resolver_eligible` остаются `0` до
  finalized gold и calibration.

## Текущий результат gold 7.4

1. Все внешние pass-1 результаты `1Sam–Rev` (58 книг) локально
   canonicalized/expanded/checked без исправления смысловых решений догадками:
   1 911 стихов, 39 148 original и 36 248 target-accounting decisions.
2. Вместе с `Gen–Ruth` полный pass 1 объединён и принят workflow:
   2 171 стих, 45 831 original, 41 807 target, 66 reviewer IDs,
   `error_count=0`.
   - merged SHA-256:
     `40a644da0193fc705dd9af9ff5cc63901d2e2e9f3394ac83cc586b21ef37eaee`;
   - validated SHA-256:
     `681dc4fb5265146518aab2dd9b6cd806436a41be655786337e95f18f19becb7b`.
3. Pass 2 и post-blind comparison завершены для `Gen–Isa` (первые 23 книги):
   814 стихов, 19 207 original и 16 692 target decisions. Новые `2Kgs–Isa`
   независимо повторно прошли `gold_compact check`, `error_count=0`.
   Полная цепочка adjudication + independent QC уже принята для `2Kgs–Esth`;
   `Neh` принят после отдельной seven-row consensus correction и повторного QC;
   `Ps` — после отдельной 13-row correction и post-correction QC. Полная
   четырёхчастная цепочка теперь принята для `Gen–Song`. Для `Isa` 1 113 из
   1 365 stable decisions совпали, а 252 расхождения ожидают adjudication.
4. Реализован новый deterministic post-blind
   `ukrainian_stage_7_gold_compare.py`:
   - реальные link/null расхождения отделяются от разной терминологии
     `severity/phenomena`;
   - совпавший alignment сохраняет union phenomena и максимальную severity;
   - adjudication может содержать только exact substantive disagreement set и
     после overlay повторно проходит полное verse-local accounting.
   Единый `check-adjudication-qc` дополнительно требует trusted QC-sidecar SHA,
   exact key/semantic/evidence/text/comment scope, distinct reviewer, полный
   reciprocal grid и нулевые error/uncertain; реальные `Lev`, `Num`, `Josh`
   проходят этот tracked контракт.
5. Сравнение `1Sam–1Kgs`: 5 274 stable decisions, 2 793 alignment agreements,
   2 481 substantive disagreements, 2 413 metadata-only differences. Все 2 481
   расхождение разрешены distinct third adjudication; повторный validator
   подтвердил exact overlay accounting 5 274/5 274. Независимый QC проверил
   1 128 уникальных строк, включая все critical/high и новые/pass-2 решения:
   `error=0`, `uncertain=0`.
6. Для накопленной очереди `Gen–Lev` distinct third adjudication структурно
   завершена и повторно провалидирована: `Gen` 230/230 и overlay 1 507,
   `Exod` 130/130 и overlay 1 382, `Lev` 216/216 и overlay 1 395.
   Content-QC разделяет их так:
   - `Gen` полностью принят: 230/230, включая 15 high и 4 new,
     `error=0`, `uncertain=0`;
   - первый `Exod` QC 130/130 дал 124 accepted / 6 error / 0 uncertain.
     Ошибки — три reciprocal пары в `Exod.27.1`, `32.19`, `32.35`, где
     `той/те` ошибочно связано с noun, а согласованный article `הַ/הָ`
     (HTd/H9009) оставлен null. Отдельный fail-closed consensus-correction уже
     создан и структурно принят: exact 9 semantic changes / 3 verses,
     `article→той/те`, `noun→noun`, overlay 1 382/1 382, correction SHA-256
     `ca53be00c26a2ab6d238e1abe495d8a9f306ca91c0493080a1860db38feb4c5a`;
     новый distinct reviewer проверил 130 adjudication + 9 correction + 3
     revalidate-only rows: 142 observations / 136 unique stable IDs, все 42
     high, `error=0`, `uncertain=0`; книга принята, final QC SHA-256
     `d79b394b22c516b814a2017f3660e3018f558c4f3176d40eacbc1b39adc19c67`;
   - `Lev` полностью принят: checkpoint 145/216 возобновлён по exact remaining
     IDs, проверены оставшиеся 71/71, итог 216/216, все 152 high и 10 new,
     `error=0`, `uncertain=0`; QC SHA-256
     `21bb8fc1c6d9f28b84bdffd828616d9093415c1a77c5daa042729d81ed001534`.
7. Для `Num` distinct adjudication разрешила 310/310 substantive disagreement,
   сохранила 1 186 согласованных решений и полный grid 1 496/1 496; отдельный
   independent QC принял все 310 решений, включая 56 high и 22 new, с
   `error=0`, `uncertain=0`. Для `Josh` adjudication 464/464 и отдельный
   independent QC также завершены: все 464 решения, 33 high и 59 new приняты
   с `error=0`, `uncertain=0`. Для `Judg` и `Ruth` adjudication и отдельный
   independent QC полностью завершены: соответственно 562/1 749 и 252/1 585,
   `error=0`, `uncertain=0`.
8. Строгий счётчик владельца (`pass 1 + pass 2 + full adjudication +
   independent QC` без `error`/`uncertain`) равен `22/66`: `Gen`, `Exod`,
   `Lev`, `Num`, `Deut`, `Josh`, `Judg`, `Ruth`, `1Sam`, `2Sam`, `1Kgs`,
   `2Kgs`, `1Chr`, `2Chr`, `Ezra`, `Neh`, `Esth`, `Job`, `Ps`, `Prov`, `Eccl`,
   `Song`.

Versioned доказательства текущей точки:

- `external_gold_pass1_batch_049_066.manifest.json`;
- `external_gold_pass1_batch_009_066.manifest.json`;
- `gold_alignment.pass1.manifest.json`;
- `gold_review_batch_005.manifest.json`;
- `gold_review_batch_009_011.manifest.json`;
- `gold_adjudication_batch_009_011.manifest.json`;
- `gold_review_batch_012_014.manifest.json`;
- `gold_review_batch_015.manifest.json`;
- `gold_review_batch_016.manifest.json`;
- `gold_review_batch_017.manifest.json`;
- `gold_review_batch_018.manifest.json`;
- `gold_review_batch_019.manifest.json`;
- `gold_review_batch_020.manifest.json`;
- `gold_review_batch_021.manifest.json`;
- `gold_review_batch_022.manifest.json`;
- `gold_review_batch_023.manifest.json`;
- `gold_adjudication_batch_001_003.manifest.json`;
- `gold_adjudication_batch_004.manifest.json`;
- `gold_adjudication_batch_005.manifest.json`;
- `gold_adjudication_batch_006.manifest.json`;
- `gold_adjudication_batch_007.manifest.json`;
- `gold_adjudication_batch_008.manifest.json`;
- `gold_adjudication_batch_012.manifest.json`;
- `gold_adjudication_batch_013.manifest.json`;
- `gold_adjudication_batch_014.manifest.json`;
- `gold_adjudication_batch_015.manifest.json`;
- `gold_adjudication_batch_016.manifest.json`;
- `gold_adjudication_batch_017.manifest.json`;
- `gold_adjudication_batch_018.manifest.json`;
- `gold_adjudication_batch_019.manifest.json`;
- `gold_adjudication_batch_020.manifest.json`;
- `gold_adjudication_batch_021.manifest.json`;
- `gold_adjudication_batch_022.manifest.json`.

## Активная работа на момент записи

На рабочей точке 2026-09-08 полная четырёхчастная цепочка принята для всех книг
`Gen–Song`, включая correction/re-QC `Neh` и `Ps`. Pass 2/comparison `Isa`
завершены и независимо повторены; 252 substantive disagreement ожидают distinct
adjudication, после которой обязателен отдельный QC. Remote LLM не запущен. По
строгому критерию приняты 22/66 книг.

Работа поставлена на паузу по просьбе владельца. Все подагенты остановлены или
завершены. Попытка начать `Isa` adjudication была прервана до создания каталога
или каких-либо adjudication-артефактов; поэтому её следует начать заново новым
distinct adjudicator по exact 252 comparison disagreements. `Jer` и `Lam` pass 2
ещё не запускались. Точная безопасная точка возобновления: параллельно выполнить
`Isa` adjudication и независимые blind pass 2 для `Jer`/`Lam`, не открывая
pass 1 до заморозки соответствующего pass 2.

Полные выходы находятся только в gitignored
`work/.../gold_review_adjudication/<Book>/`, имеют distinct identities и exact
pass/comparison SHA locks. Повторная structural-проверка выполняется командой:

```powershell
python -m scripts.bible_module.ukrainian_stage_7_gold_compare check-adjudication `
  --pass1 <pass1> --pass2 <pass2> --comparison <comparison> `
  --adjudication <completed-adjudication>
```

Точные pause-артефакты:

- `Gen/qc/qc.adjudication.Gen.shard_001.codex-independent-20260905.jsonl`,
  SHA-256 `44d7ab93e80c00fd449a03d96e20ba5267c0218f8940be0efd6d50ecf7725b95`;
- его manifest SHA-256
  `f15febd45ef2ac7fccae4447d1a51f0a18b88e11304e2447c1e59bbd2369d9d7`;
- `Exod/qc/qc.adjudication.Exod.shard_002.codex-independent-20260905.jsonl`,
  SHA-256 `ad2f377aebf8c5510e2cd70dfb1b62210aa90418eef3d050c821ed1a00f39cca`;
- его manifest SHA-256
  `582947981f4fd29d4a4ef3fc456df5337159432d18abab1c8d4d506a7ce523f6`;
- `Lev/qc/qc.checkpoint.adjudication.shard_003.codex-independent-20260905.json`,
  SHA-256 `2c0e98a4dbaf70dbcef57c932731ba84ff8160109fa6f8d11c8b7a88d2ab2fae`;
- его manifest SHA-256
  `fafe80b9c03968253aba51356f66e0d6ee4b9eb1aa105e9d49dff13c60dde8cd`.
- `Lev/qc/qc.adjudication.Lev.shard_003.codex-independent-20260905.jsonl`,
  SHA-256 `21bb8fc1c6d9f28b84bdffd828616d9093415c1a77c5daa042729d81ed001534`;
- его итоговый manifest SHA-256
  `19e2c36bf34919ebec0cc3f57930ce894614809602dd48aed9d4f9c66ac9c51e`;
- `Exod/correction/Exod.shard_002.consensus_correction.jsonl`, SHA-256
  `ca53be00c26a2ab6d238e1abe495d8a9f306ca91c0493080a1860db38feb4c5a`;
- его manifest SHA-256
  `20fd7ead995709b575018a5afb765a10c9a382fd048764eda73ec798c28fe539`.
- `Exod/qc/qc.final.Exod.shard_002.post-consensus-correction.codex-independent-20260907.jsonl`,
  SHA-256 `d79b394b22c516b814a2017f3660e3018f558c4f3176d40eacbc1b39adc19c67`;
- его manifest SHA-256
  `e6e192709d597099fb464196ef7e695822925a3601b33bb19b6f51acbdf0847e`.
- `Num/qc/qc.adjudication.Num.shard_004.codex-independent-20260907.jsonl`,
  SHA-256 `04873c06dfd6c5182e0d7e73e0e44440290b046561a12d6f2525475bdcb0df15`;
- его manifest SHA-256
  `2401c4fe5c464d7ea6844785f968f4481a46fca69f216b8ec8fd58f9f325f88f`.
- `Josh/qc/qc.adjudication.Josh.shard_006.codex-independent-20260907.jsonl`,
  SHA-256 `9bf8b729870009bf2131d42fad132b8dbc7703e32cd8dec10008a8b9ce1daba3`;
- его manifest SHA-256
  `d310eb8b3d414e1cd402f47561aaa4e22323b26249f14f79034a3ed12ba6f42c`.
- `Judg/qc/qc.adjudication.Judg.shard_007.codex-independent-20260907.jsonl`,
  SHA-256 `44a7a12195c42aa2fd472edb704a8b9ab5962ada18004391919f57b118854c67`;
- его manifest SHA-256
  `785e0503f0d2ea355c5cac3b7c8e5bef3300c28ba2bf4d6587f0c3ee9da9580e`.
- `Ruth/qc/qc.adjudication.Ruth.shard_008.codex-independent-20260907.jsonl`,
  SHA-256 `b782950a46cd2806254b03f96d698c4d96f3cc33fd81b9ebfd4bdc87c63898b7`;
- его manifest SHA-256
  `ac86a7e26f40c92ff9c15d102208c4c823df90735559095cdc4048274a40667d`.
- `2Kgs/2Kgs.shard_012.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `c9d7cb5d7735c5ca2f681fd38ea7b1a0ff482d4da11155d5438a8365e078913c`;
- его manifest SHA-256
  `7cd6307c69a31353595f4f4273d7894aee7d5fa8ecd27b4b26f41d1dab044e90`.
- `2Kgs/qc/qc.adjudication.2Kgs.shard_012.codex-independent-20260907.jsonl`,
  SHA-256 `4d12c29dcd3318fe1b6847677b803a115d7b360f4cb8ff5deaad1fbe6aa5c39c`;
- его manifest SHA-256
  `1d1c9a14c6e9a75aeb6041d7ad413304844ac362a48976cf03059f77b74bbb8a`.
- `1Chr/1Chr.shard_013.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `4b3a2d93d2219d9a79c5a9a18f1f38e480a78590b315dd6e2b8724992fe70dbd`;
- его manifest SHA-256
  `a89b10b62f102bae709d8ad883699478264dfbdece03100efd299d122d9a4602`.
- `1Chr/qc/completed/1Chr.shard_013.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `2e4880fa62a04b60603943a814475c2d7f1a269ef5ff3e6d4e94fe73856dc9af`;
- его manifest SHA-256
  `a8e2fc4b87fa3288b14c891cf3d34f30064522efe54fb0769a424d1c54b2b0be`.
- `2Chr/2Chr.shard_014.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `cfc78bb386463cc6256cc80b88ed213c29770712c8c6956db5044b78e75fe733`;
- его manifest SHA-256
  `ba1625e95b9238071206c295c7701b15019107303ccb59210b77d45e42f0d256`.
- `2Chr/qc/qc.adjudication.2Chr.shard_014.codex-independent-20260907.jsonl`,
  SHA-256 `43d27d083d8ba1b5bad469f08b2efa2572258560c63ec1a078e465ccb4888d45`;
- его manifest SHA-256
  `8140bbbd82ea4955a0b1c626cf0bd66a1c32c6337f3e619b57c9d83c28121d05`.
- `Ezra/Ezra.shard_015.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `3e80aac71be6868bda3185a73d5cedd20d6350273751b205492c6c941bf822f5`;
- его manifest SHA-256
  `3c493c4abfee4cf092654eff0fb924b4f40471d215105b2ff6ef1e71d225b596`.
- `Ezra/qc/completed/Ezra.shard_015.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `f4765d6260064410a7009114570fed28867caff3b454745cdc6b072c8bff195a`;
- его QC manifest SHA-256
  `fa4bb85dc1f862133ec99cce69f265148e3971c057ee3b14237906d6a6b35527`.
- `Neh/completed/Neh.shard_016.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `32bcb8a7c4378c247560160f837b550aad188559138a4b4285835d2f0caf9874`;
- его manifest SHA-256
  `3febb24494efc20b647d33a6a961ee28f4d74fed6db13b2e51fcc0d8255f9380`.
- `Neh/correction/Neh.shard_016.consensus_correction.jsonl`, SHA-256
  `cea4dad10bda6870ddb6523c283ea0532c16a87061b877ca2b26234e3dc0bac1`;
- его manifest SHA-256
  `463638c46ef1ea8daa3e97a19e811ce28f3d5007256d3c9acf113d1074291a08`.
- `Neh/qc/completed/Neh.shard_016.post-consensus-correction.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `7f7eee3c3e4d43085d78499ba583816373bd51ea211b7a7fef15f9bd71b44b05`;
- его manifest SHA-256
  `32b6909262704351d3a79cde5bc8b27ea638506c6631990d7770947f44e4e6df`.
- `Esth/Esth.shard_017.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `3b4aa967045251000e3f142fc09e462076c9e9f5f7df829a56f4ad8707e10345`;
- его manifest SHA-256
  `4fbe485772f8737bb69759c2f282e97f49eba20d21f2e14f973e1ab01c9b4b21`.
- `Esth/qc/qc.adjudication.Esth.shard_017.codex-independent-20260907.jsonl`,
  SHA-256 `14397af3a299b8d5086aa581a4f61fa0a24c7d5649c750f3b7d571349dd7d578`;
- его manifest SHA-256
  `9b7dca7490b9ec13c23c0bcfe0739f3db9908f35034ebfa02e770038fcd2eba8`.
- `Deut/Deut.shard_005.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `04c92f11ed2ec476c61df0db85ba4f2b1835a8f55a68f322179eb9c7d32d05e8`;
- его manifest SHA-256
  `17bb2f95a50416a9ab083cc7766b4ee23322a650f4f3b8e1f669c6afd9192b9f`.
- `Deut/qc/completed/Deut.shard_005.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `3c994118fc83365131d3ebec9a344b9dae63413eb043f59267465fad658603e4`;
- его manifest SHA-256
  `51d8a9f3c8bdc435fda028d64cfe70c7511514430df5ad373a614096db1aa154`.
- `Job/completed/Job.shard_018.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `5a57b7944c5e984043ca2c965b13b55189647b33d6cf49bcbe641f3514f071ed`;
- его manifest SHA-256
  `e2161bbb5d7c8b24584ab5a99ec8c36806d194eef06a0d3a1649b834abeaa3cf`.
- `Job/qc/Job.shard_018.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `0476052c538509df84c9fe47183fdf28f08df54b652868b774a67fb6d7eaf0ee`;
- его manifest SHA-256
  `e89703c825f12ecc1e0986cdbfa7c28f49e5a07c7160cdffc42a51b4cadc5d7a`.
- `Ps/qc/blocking/Ps.shard_019.third_adjudication.blocking_content_qc.codex-20260907.jsonl`,
  SHA-256 `6b3acd2eb81dbbf002b399d3e766ede922f688d3c867efb1d219330d0fe312d7`;
- его blocking-QC manifest SHA-256
  `6ed953cc85d5ed71e260d5750b1ce42224f7cc962651001f03e84a9cd229b744`.
- `Ps/correction/Ps.shard_019.consensus_correction.jsonl`, SHA-256
  `57c57e7d53ab191c0848b97450329f4cce38889603fb1cad331bc6158aba393b`;
- его manifest SHA-256
  `7c68870a0de052fa5a8ab30f40a989bf86fb87cce6462c9bb26ad2c295395e86`.
- `Ps/corrected/Ps.shard_019.pass1-pass2.third_adjudication.corrected-v1.jsonl`,
  SHA-256 `2e1d6495b4daecbdc377dbbc6ecd28c6e9734f017c5a8dbce64062757eb4a1f5`;
- его manifest SHA-256
  `1bcc754d7aa3ec8718e5a770aa9251b66a1aa74db9c22bb30d2e761741561fe4`.
- `Ps/qc/post_correction/Ps.shard_019.post-consensus-correction.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `f5858df011da8de6161b0c58a951cbd21e6febde438c63dfdd12c905984467c5`;
- его manifest SHA-256
  `67e699c420ed9cd33411348717661aec26c50bace60c7199465e32951ee8c143`.
- `Prov/completed/Prov.shard_020.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `206b8b28178ede8fd7d17c5c1b8ee98e0e25a48c996563f37f6fb7e42f2aa31b`;
- его manifest SHA-256
  `5d3371ae86a4187cd45bf24de735691b5e91fafa2cc67af8d50183a019c9559f`.
- `Prov/qc/Prov.shard_020.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `ae11abe38e8d8e3f8eae6bf617286ba21acabe032076fed27e22c5df3b3fa64d`;
- его manifest SHA-256
  `36130c5f2db71dd286c5b7599851f691dcaa7d55be810f374c46d67abba4056c`.
- `Eccl` pass-2 raw SHA-256
  `1aac79eac5b30a2df0aecb5bab95cf7aa8fcd3e1d44825b5c73eec47231aff32`;
- его manifest SHA-256
  `dc09fd4a912cfbb5f600d49c94aee18146791854bb8a14a650aa146fcaf9ce2b`;
- `Eccl.pass1-pass2.disagreements.jsonl` SHA-256
  `4bc6dbad205ac2fd93c9c01f74f1e46245e0009697d2bee634644d92ce7d7ca4`;
- его manifest SHA-256
  `f5e4463510c05b7a14b6d020a7e2380adcf23ee0e78e5be94f13b726630460bd`.
- `Eccl/completed/Eccl.shard_021.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `b18d6ca49544007d45d9f5517ce26eda2ec2476e9582062b4e559280ed0c39d2`;
- его manifest SHA-256
  `d80dbfb5b4711dcaa8576fd3bd88255aa533a5ad03ae873980a0a49d5b737628`.
- `Eccl/qc/Eccl.shard_021.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `0a25f883b696b97fb8004ef695207669d7310e18b869babc64ffa6e681c39522`;
- его manifest SHA-256
  `e7267c93aa0d95bdcceaedf42a5b68c87888eb12d794177bf4ddbfc09a757614`.
- `Song` pass-2 raw SHA-256
  `220a39ac8483677ead60de7e3d02adca4f31928caac4117b3e69b589b7a991a1`;
- его manifest SHA-256
  `87d121822c84b9a635ccd0cadf111a2880a9866e5e6b5ba1ce9056fbf299338b`;
- `Song.pass1-pass2.disagreements.jsonl` SHA-256
  `f6677da6af5c4576ae1bfd5a152637a2fd3601fdf5c84747a952d5f7a9b559bc`;
- его manifest SHA-256
  `9f5dc704caa6be1ef5c66914ba7dea54f71ca0cd0ca339c1a9436a9f3f0e39c8`.
- `Song/completed/Song.shard_022.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `a0b625232bde7b8ab4082eb87bb0490de05c0a329df647eec8710896f150f48e`;
- его manifest SHA-256
  `f6cf521807b4c8dd14d6223d08e8f6d2bc2f95501e7618aa3389380268ef01f4`.
- `Song/qc/completed/Song.shard_022.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `9dd78e3168910fe0f7acd652272cb51238daebe0d8261f9b71887efd3a0997b2`;
- его manifest SHA-256
  `854b3250cf4988e50b8404cc1ece93fd361e57d6e592de51f99fb4addd5271a6`.
- `Isa` pass-2 raw SHA-256
  `5d186e7cb068d03e0ff6a79587f2e881472b7c9de723d85e4f0e3ab72e7fdc45`;
- его manifest SHA-256
  `2b7d4d11c472676f5aa1e2dea69de09fe84c7a2640130d3e0f1a8d684044df7d`;
- `Isa.pass1-pass2.disagreements.jsonl` SHA-256
  `a6cd14b1053f389ccdf6b1835836b0ab005aa5dcc21c557c867482dccc6b53cd`;
- его manifest SHA-256
  `f97cb0646e40354fcb69dcd731cf6d94429b91497db59e032112104b460d75e8`.

## Проверки текущего сеанса

- обязательные stage 3/4/5/6 `--check` — PASS;
- `python -m unittest` для gold/compact/shards/external — PASS, 36 tests;
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  399 tests;
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, 30 tests;
- forbidden-pattern and docs-sync checks — PASS;
- current Flutter `3.47.2` / Dart `3.13.2`: `dart format .` attempted to change
  four out-of-scope tests and `flutter analyze` reported 8 pre-existing
  warnings after automatic dependency/config migration; all unintended tracked
  edits were restored. Analyzer remains a final blocker, not a stage-7 code
  regression;
- `flutter test --no-pub` completed the full repository suite: `918` tests
  passed and `2` pre-existing Strong-dictionary widget tests failed because the
  expected preview strings were absent; a focused rerun reproduced `1` pass / `2`
  failures. Stage 7 changed no Flutter source/test/dependency;
- `python -m py_compile` для изменённых gold modules — PASS;
- локальный `gold_compact check` для `1Sam`, `2Sam`, `1Kgs` — PASS;
- локальный `gold_compact check` для `2Kgs`, `1Chr`, `2Chr`, `Ezra` — PASS;
- `check-adjudication` для `Gen`, `Exod`, `Lev` — PASS structural; content-QC
  после отдельного `Exod` correction принят для всех трёх;
- отдельная root-проверка `Exod` final QC: exact 142 observations / 136 unique
  keys, corrected semantics, 18 input SHA locks, role independence, canonical
  serialization и full grid 1 382/1 382 — PASS;
- отдельная root-проверка `Num` QC: exact 310/310 stable keys and semantics,
  all input SHA locks, canonical serialization, reviewer independence и full
  grid 1 496/1 496 — PASS;
- отдельная root-проверка `Josh` QC: exact 464/464 stable keys and semantics,
  all input SHA locks, canonical serialization, reviewer independence и full
  grid 1 566/1 566 — PASS;
- отдельная root-проверка `Judg` QC: trusted sidecar SHA, exact 562/562 unique
  stable keys and semantics, explicit alignment/semantic selection counts,
  canonical serialization, reviewer independence и full grid 1 749/1 749 — PASS;
- отдельная root-проверка `Ruth` QC: accepted-v3/v2 input locks, exact 252/252
  unique stable keys and semantics, canonical serialization, reviewer
  independence и full grid 1 585/1 585 — PASS;
- все 18 versioned accepted book/batch manifests через shard 022: canonical
  deterministic serialization и физическое совпадение `225/225` output SHA
  locks — PASS;
- `Prov` independent QC: 164/164 accepted, 5 critical, 93 high, 11 new,
  grid 813/813, `error=0`, `uncertain=0`; generic validator дважды и 10/10
  физических SHA-lock — PASS FOR THIS BOOK;
- blind pass 2/comparison `Eccl`: 32/32 стихов, 780 original + 625 target,
  `gold_compact check` с `error_count=0`; из 1 405 stable decisions 970
  совпали, 435 переданы adjudication; root comparison byte-identical и 4/4
  физических SHA-lock; adjudication и independent QC 435/435, grid 1 405/1 405,
  `error=0`, `uncertain=0`, root 10/10 SHA audit — PASS FOR THIS BOOK;
- `Song` adjudication и independent QC: 609/609, 207 компонентов, все 21
  critical, 142 high и 109 declared-new, grid 1 200/1 200, `error=0`,
  `uncertain=0`; double validator и root 10/10 SHA audit — PASS FOR THIS BOOK;
- blind pass 2/comparison `Isa`: 34/34 стиха, 716 original + 649 target,
  compact check дважды; 1 113 agreements / 252 disagreements, root comparison
  byte-identical и 4/4 SHA locks — PASS / ADJUDICATION GATE;
- полный Flutter-набор повторён, но остаётся красным по двум указанным
  out-of-scope тестам; после стабилизации окружения/исходного Flutter baseline
  он должен быть чисто повторён перед закрытием этапа.

## Точная следующая последовательность

1. Завершить distinct adjudication и отдельный independent QC `Isa` (023),
   используя уже принятые blind pass 2/comparison.
2. Перед дальнейшим merge перепроверять exact SHA locks всех versioned
   `gold_review_batch_*` и `gold_adjudication_batch_*` manifests.
3. После каждого pass 2 выполнить локальный `gold_compact check`, post-blind
   compare, distinct adjudication и QC. Повторять book batches до `Rev`.
4. После всех 66 книг объединить pass 2, проверить reviewer independence,
   выполнить `ingest-pass2`, global comparison, собрать exact global
   adjudication и только затем `finalize/check-final`.
6. После finalized gold оценить legacy и новые методы, выполнить calibration
   A/B/C, B/C review, overrides и лишь затем Strong markup с exact 31 102
   text/comment round-trip.
7. Не начинать этап 8, не создавать SQLite, не менять Flutter/content tool/DB.

## Remote LLM

Remote pilot остаётся candidate-only и запечатан в
`local_llm_remote_pilot_checkpoint.manifest.json`; разрешающего verdict нет.
Не запускать `Start`, `BenchmarkAll` или `RunWeekQueue`, пока владелец снова
явно не сообщит, что компьютер доступен.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`
