# NA28_LXX Phase 11 Size Audit

Temporary owner-review report for Phase 11 of
`na28_lxx_bible_module_roadmap.md`.

Audit date: 2026-05-30

Audited DB:
`C:\Users\karna\Documents\revelation\db\bible_na28_lxx.sqlite`

Generated with:

```powershell
python -m scripts.bible_module.audit_na28_lxx_size --db "$HOME\Documents\revelation\db\bible_na28_lxx.sqlite" --deep --scenarios --format markdown
```

## Size Summary

- Current file size: 476,852,224 bytes / 454.76 MiB.
- SQLite page size: 4096.
- SQLite page count: 116,419.
- SQLite free pages: 0.
- `PRAGMA user_version`: 1.

Largest isolated table estimates:

| Table | Rows | Isolated size | Text payload |
| --- | ---: | ---: | ---: |
| `tokens` | 632,930 | 364.27 MiB | 295.15 MiB |
| `token_strongs` | 592,448 | 25.63 MiB | 12.04 MiB |
| `module_verses` | 30,460 | 18.18 MiB | 7.78 MiB |
| `import_warnings` | 65,290 | 13.95 MiB | 12.09 MiB |
| `canonical_verses` | 31,102 | 1.77 MiB | 0.52 MiB |
| `module_verse_links` | 30,460 | 1.49 MiB | 0.57 MiB |

Largest text columns:

| Table | Column | Payload |
| --- | --- | ---: |
| `tokens` | `raw_json` | 247.36 MiB |
| `tokens` | `source_text_id` | 9.26 MiB |
| `tokens` | `transliteration` | 7.88 MiB |
| `tokens` | `source_ref` | 7.40 MiB |
| `import_warnings` | `raw_json` | 7.14 MiB |
| `tokens` | `morphology` | 6.91 MiB |
| `tokens` | `lemma` | 5.52 MiB |
| `token_strongs` | `role` | 3.88 MiB |
| `module_verses` | `text_plain` | 3.54 MiB |
| `module_verses` | `text_display` | 3.54 MiB |

Temporary pruning scenario estimates, all made on disposable copies:

| Scenario | Result size | Saved |
| --- | ---: | ---: |
| Drop `import_warnings` | 435.96 MiB | 18.80 MiB |
| Drop only `tokens.raw_json` | 168.17 MiB | 286.59 MiB |
| Drop `tokens.raw_json` and `import_warnings.raw_json` | 160.06 MiB | 294.70 MiB |
| Drop `tokens`, `token_strongs`, and `import_warnings` | 23.64 MiB | 431.12 MiB |
| Compact Phase 12 usage-source token tables | 94.10 MiB | 360.66 MiB |
| Minimum runtime without tokens, warnings, or `text_display` | 15.39 MiB | 439.37 MiB |

## Runtime Contract

Minimum runtime/published Bible module should support:

- opening a verse by stable `canonical_verse_id`;
- resolving `canonical_verse_id` to `canonical_ref` and readable book/chapter/verse data;
- reading one module verse by canonical id for parallel reading;
- browsing by canonical order/book/chapter;
- resolving Strong `usage` v2 bracket ids to verses after Phase 12/13;
- showing module/source/license metadata somewhere in the app or acknowledgements flow.

The minimum contract does not require token-level rows after `greek_words.usage`
has been generated, unless we decide to support runtime interlinear, morphology,
lemma search, or token-level Strong search directly inside the Bible module UI.

## Artifact Recommendation

Recommended owner decision:

1. Keep a full working/source artifact, for example
   `bible_na28_lxx.full.sqlite`, outside the shipped runtime payload.
2. Generate Phase 12 `usage` from the full working artifact or from a compact
   Phase 12 source artifact that keeps only token fields needed for usage.
3. Publish `bible_na28_lxx.sqlite` as a compact runtime artifact.
4. Keep source/license metadata in the runtime DB because it is tiny and useful.
5. Move bulky build diagnostics (`import_warnings.raw_json` and full warning
   rows) to a sidecar report if they are needed after build validation.

Suggested size budget after owner review:

- runtime target: <= 25 MiB if `text_plain` and `text_display` are both kept;
- stretch target: <= 16 MiB if `text_display` is dropped and derived from
  `text_plain` for this Greek module.

## Table And Column Review

Decision labels:

- `runtime keep`: keep in the shipped compact DB.
- `runtime drop`: remove from shipped compact DB.
- `derive`: do not store because it can be derived from retained fields.
- `working only`: keep only in the full source/build DB.
- `sidecar`: move to an import/build report outside the runtime DB.
- `pending`: needs owner decision before destructive pruning.

### `db_metadata`

Purpose: database-level version metadata used by sync, diagnostics, and publish
flows.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `key` | Metadata key, currently `schema_version`, `data_version`, `date`. | runtime keep |
| `value` | Metadata value. | runtime keep |

### `bible_modules`

Purpose: one row describing this module as a distributable Bible module.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `module_id` | Stable internal id, currently `na28_lxx`. | runtime keep |
| `code` | User/manifest-facing code, currently `NA28_LXX`. | runtime keep |
| `title` | Human-readable module title. | runtime keep |
| `language` | Module language code, currently `grc`. | runtime keep |
| `module_kind` | Module type, currently `original_language`. | runtime keep |
| `canon` | Canon descriptor. | runtime keep |
| `versification` | Mapping/versification note. | runtime keep |
| `license` | Compact license summary. | runtime keep |
| `source_summary` | Compact source summary. | runtime keep |
| `schema_version` | Module schema version. | runtime keep |
| `data_version` | Module data version. | runtime keep |
| `built_at` | Build timestamp. | runtime keep |

### `module_sources`

Purpose: exact source/license/checksum metadata for provenance and
acknowledgements.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `source_id` | Stable id for TAGNT, LXX, and supporting sources. | runtime keep |
| `module_id` | Parent module id. | runtime keep |
| `title` | Source title. | runtime keep |
| `source_url` | Exact source page URL. | runtime keep |
| `source_version` | Source version/commit/module version. | runtime keep |
| `license` | Source license text. | runtime keep |
| `checksum_sha256` | Locked source checksum. | runtime keep |
| `import_notes` | Import/provenance notes. | runtime keep or sidecar; size is tiny |

### `books`

Purpose: self-contained 66-book canon list.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `book_id` | Stable canonical book id. | runtime keep |
| `canonical_code` | Project canonical book code, for example `Gen`. | runtime keep |
| `osis_code` | OSIS book code. | runtime keep or derive |
| `title` | English book title. | runtime keep unless app localizes elsewhere |
| `testament` | `OT` or `NT`. | runtime keep |
| `sort_order` | Canonical book order. | runtime keep |
| `is_canonical` | Canonical flag; always 1 for this module. | derive or runtime drop |

### `canonical_verses`

Purpose: stable module-independent verse identity table. This is the key table
for Strong `usage` v2 ids and parallel reading.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `canonical_verse_id` | Stable numeric id used by `usage` v2 payloads. | runtime keep |
| `canonical_ref` | Stable text ref, for example `Gen.1.1`. | runtime keep |
| `osis_ref` | OSIS ref. | runtime keep or derive/drop if not used |
| `book_id` | Link to `books`. | runtime keep |
| `chapter` | Canonical chapter number. | runtime keep |
| `verse` | Canonical verse number. | runtime keep |
| `subverse` | Optional subverse; currently empty. | derive or runtime drop |
| `sort_key` | Canonical order key. | runtime keep |

### `source_texts`

Purpose: identifies source streams within the module: LXX OT and TAGNT NA28 NT.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `source_text_id` | Stable source-text id. | runtime keep |
| `module_id` | Parent module id. | runtime keep |
| `source_id` | Source metadata link. | runtime keep |
| `code` | Short source text code. | runtime keep |
| `scope` | Scope, currently `OT` or `NT`. | runtime keep |
| `language` | Source language. | runtime keep |
| `priority` | Source priority/order. | runtime keep |

### `module_verses`

Purpose: actual verse text rows for this module.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `module_verse_id` | Primary key for module verse rows. | runtime keep |
| `source_text_id` | LXX/TAGNT source stream. | runtime keep |
| `native_ref` | Source-native reference. | runtime keep |
| `book_id` | Book id duplicated from canonical link. | runtime keep or derive |
| `chapter` | Native/canonical chapter number. | runtime keep or derive |
| `verse` | Native/canonical verse number. | runtime keep or derive |
| `subverse` | Optional subverse; currently empty. | derive or runtime drop |
| `text_plain` | Greek verse text for display/search. | runtime keep |
| `text_display` | Display text; currently identical to `text_plain`. | derive or runtime drop |
| `tokens_count` | Number of imported tokens in the verse. | working only or runtime keep for diagnostics |
| `sort_key` | Canonical/source sort order. | runtime keep |

### `module_verse_links`

Purpose: maps each module verse to stable canonical verse identity.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `module_verse_id` | Module verse id. | runtime keep |
| `canonical_verse_id` | Stable canonical verse id. | runtime keep |
| `link_kind` | Link type; currently always `exact`. | runtime keep for future modules or derive |
| `note` | Link note; mostly duplicates `native_ref`. | sidecar or runtime drop |

### `tokens`

Purpose: token-level working/source table used for Strong usage generation,
source audit, and possible future interlinear/morphology features.

Runtime after Phase 12 does not need this table for the minimum contract.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `token_id` | Stable token row id. | working only; keep in Phase 12 source |
| `module_verse_id` | Parent verse id. | working only; keep in Phase 12 source |
| `source_text_id` | Redundant source stream id. | working only; derive from verse |
| `token_order` | Token order in verse. | working only; keep in Phase 12 source |
| `source_ref` | Source token reference. | working only or sidecar |
| `text_type` | TAGNT/source text type marker. | working only |
| `surface` | Display surface form. | working only; keep in Phase 12 source |
| `surface_normalized` | Normalized surface form. | working only; keep in Phase 12 source |
| `surface_search` | Search/comparison surface form. | working only; keep in Phase 12 source |
| `transliteration` | Transliteration. | working only |
| `lemma` | Lemma. | working only unless future runtime lemma search is approved |
| `morphology` | Morphology code. | working only unless future runtime morphology UI is approved |
| `gloss` | Source gloss. | working only |
| `raw_json` | Full source row payload. | sidecar or full working DB only; drop from runtime |

### `token_strongs`

Purpose: token-to-Strong mapping used by Phase 12 usage generation.

Runtime after Phase 12 does not need this table for the minimum contract.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `token_strong_id` | Strong link row id. | working only |
| `token_id` | Parent token id. | working only; keep in Phase 12 source |
| `strong` | Normalized Strong key, no leading zeroes. | working only; keep in Phase 12 source |
| `raw_strong` | Source Strong key, possibly padded. | working only or sidecar |
| `role` | `primary` or `alt`. | working only; keep in Phase 12 source |
| `segment_order` | Segment order for multi-Strong tags. | working only |
| `segment_surface` | Segment surface text. | working only |
| `is_primary` | Boolean primary flag. | working only; keep in Phase 12 source |

### `import_warnings`

Purpose: build/import diagnostics. Useful for validation, but not needed by the
runtime app after the module has passed validation.

| Column | Purpose | Recommended decision |
| --- | --- | --- |
| `warning_id` | Warning row id. | sidecar |
| `source_id` | Warning source id. | sidecar |
| `severity` | Warning severity. | sidecar |
| `code` | Warning code. | sidecar |
| `source_ref` | Source reference. | sidecar |
| `message` | Human-readable warning. | sidecar |
| `raw_json` | Raw warning payload. | sidecar |

## Index Review

| Index | Purpose | Recommended decision |
| --- | --- | --- |
| `idx_canonical_verses_canonical_ref` | Lookup canonical ids/refs by text ref. | runtime keep |
| `idx_canonical_verses_sort_key` | Browse canonical order. | runtime keep |
| `idx_module_verse_links_canonical_verse_id` | Main runtime lookup: canonical id -> module verse. | runtime keep |
| `idx_module_verses_source_text_sort_key` | Browse module verses by source/order. | runtime keep |
| `idx_tokens_module_verse_token_order` | Token order lookup. | working only |
| `idx_token_strongs_strong` | Strong -> tokens lookup. | working only after Phase 12 |
| `idx_token_strongs_token_id` | Token -> Strong join lookup. | working only after Phase 12 |
| `sqlite_autoindex_*` | Primary/unique indexes created by SQLite. | follows retained tables |

## Recommended Next Owner Decisions

1. Confirm two artifacts: full working/source DB plus compact runtime DB.
2. Confirm whether runtime may drop `tokens`, `token_strongs`, and
   `import_warnings` after Phase 12 usage is generated.
3. Confirm whether runtime may drop `module_verses.text_display` because it is
   currently identical to `text_plain`.
4. Confirm whether runtime keeps `books.osis_code`, `canonical_verses.osis_ref`,
   `subverse`, `module_verse_links.link_kind`, and `module_verse_links.note`.
5. Confirm runtime size budget: recommended <= 25 MiB, stretch <= 16 MiB.

