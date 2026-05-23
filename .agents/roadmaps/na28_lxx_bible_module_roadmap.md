# NA28_LXX Bible Module And Strong Dictionary Roadmap

Temporary working document. Delete this file after the `NA28_LXX` Bible module, Strong dictionary occurrence rebuild, tests, acknowledgements, and release notes decision are completed.

## Scope

- [ ] Build one canonical Greek Bible module: `NA28_LXX`.
- [ ] Include only the 66 canonical Protestant Bible books.
- [ ] Use LXX Greek text for the 39 Old Testament books.
- [ ] Use NA28-profile Greek text for the 27 New Testament books.
- [ ] Exclude all apocryphal/deuterocanonical books and additions.
- [ ] Normalize Strong numbers without leading zeroes: `G0746 -> G746`, `H0085 -> H85`.
- [ ] Keep `raw_strong` when the source contains padded Strong numbers.
- [ ] Do not store `word_forms` or `word_form_occurrences` inside Bible modules.
- [ ] Rebuild Strong word forms and all form occurrences once from `NA28_LXX`, then store them in the app Strong dictionary DB/tables.
- [ ] Make every occurrence point to a stable module-independent `canonical_verse_id` and `canonical_ref`.

## Target Outputs

- [ ] `C:\Users\karna\Documents\revelation\db\bible_na28_lxx.sqlite`
- [ ] Optional web copy: `web/db/bible_na28_lxx.sqlite`
- [ ] Updated DB manifest entries, if Bible modules are distributed through the same DB sync flow.
- [ ] Updated Strong dictionary data in the existing project DB model.
- [ ] Import/build scripts under `scripts/`, with repeatable source cache and deterministic output.
- [ ] Updated `scripts/content_tool` Bible tab for creating, opening, editing, validating, and publishing `bible_*.sqlite` modules.
- [ ] Tests for parsing, canon filtering, Strong normalization, verse linking, and dictionary occurrence generation.
- [ ] Acknowledgement entries for all adopted third-party data sources in `assets/data/about_libraries.xml`.

## Phase 1 - Source And License Lock

- [x] Record exact source URLs, module versions, download dates, and source commit hashes where available.
- [x] Create a local source cache directory for reproducible imports, for example `scripts/bible_module/source_cache/`.
- [x] Download STEPBible `TAGNT Mat-Jhn`.
- [x] Download STEPBible `TAGNT Act-Rev`.
- [x] Download STEPBible `TBESG`.
- [x] Download STEPBible `TFLSJ 0-5624`.
- [x] Download STEPBible `TFLSJ extra`.
- [x] Download STEPBible `TEGMC`.
- [x] Download CrossWire SWORD `LXX` module.
- [x] Save each source checksum in a machine-readable manifest.
- [x] Confirm all STEPBible sources are `CC BY 4.0`.
- [x] Confirm CrossWire `LXX` is allowed for this project under `Copyrighted; Free non-commercial distribution`.
- [x] Add a hard build-time guard that refuses to import deuterocanonical/apocryphal books.
- [x] Add a hard build-time guard that refuses to import RVR1960 without explicit permission, if future Spanish work resumes.

## Phase 2 - Canon And Verse Identity

- [x] Define the canonical 66-book list in one source file.
- [x] Assign stable `book_id` values.
- [x] Assign stable `canonical_verse_id` values.
- [x] Define `canonical_ref` in the project reference style, for example `Gen.1.1`, `Mat.1.1`, `Rev.22.21`.
- [x] Store source-native references separately as `native_ref`.
- [x] Store optional OSIS references separately as `osis_ref`.
- [x] Create a canonical verse table that does not depend on any Bible module.
- [x] Decide the exact handling of Psalm titles and Psalm numbering before import.
- [x] Decide the exact handling of LXX Esther canonical text versus Greek additions.
- [x] Decide the exact handling of LXX Daniel canonical text versus Susanna, Bel, and Prayer of Azariah.
- [x] Create explicit exclusion ranges for all non-66-book material found in the SWORD LXX export.
- [x] Create explicit mapping rules for LXX book names to canonical book ids.
- [x] Create explicit mapping rules for Kingdoms/Paraleipomenon names:
  - [x] `1 Kingdoms -> 1 Samuel`
  - [x] `2 Kingdoms -> 2 Samuel`
  - [x] `3 Kingdoms -> 1 Kings`
  - [x] `4 Kingdoms -> 2 Kings`
  - [x] `1 Paraleipomenon -> 1 Chronicles`
  - [x] `2 Paraleipomenon -> 2 Chronicles`
- [x] Add tests proving no non-canonical book can enter `NA28_LXX`.

## Phase 3 - Bible Module Schema

- [x] Create a Drift/SQLite schema for Bible modules.
- [x] Keep this schema symmetric for original-language modules and translation modules.
- [x] Keep token-level tables optional for translations.
- [x] Do not add form occurrence tables to Bible modules.
- [x] Include `db_metadata`.
- [x] Include `bible_modules`.
- [x] Include `module_sources`.
- [x] Include `books`.
- [x] Include `canonical_verses`.
- [x] Include `source_texts`.
- [x] Include `module_verses`.
- [x] Include `module_verse_links`.
- [x] Include `tokens`.
- [x] Include `token_strongs`.
- [x] Include `import_warnings`.
- [x] Include indexes for:
  - [x] `canonical_verses(canonical_ref)`
  - [x] `canonical_verses(sort_key)`
  - [x] `module_verse_links(canonical_verse_id)`
  - [x] `module_verses(source_text_id, sort_key)`
  - [x] `tokens(module_verse_id, token_order)`
  - [x] `token_strongs(strong)`
  - [x] `token_strongs(token_id)`

### Proposed Bible Module Tables

```sql
db_metadata(
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

bible_modules(
  module_id TEXT PRIMARY KEY,
  code TEXT NOT NULL,
  title TEXT NOT NULL,
  language TEXT NOT NULL,
  module_kind TEXT NOT NULL,
  canon TEXT NOT NULL,
  versification TEXT NOT NULL,
  license TEXT NOT NULL,
  source_summary TEXT NOT NULL,
  schema_version INTEGER NOT NULL,
  data_version INTEGER NOT NULL,
  built_at TEXT NOT NULL
);

module_sources(
  source_id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_version TEXT,
  license TEXT NOT NULL,
  checksum_sha256 TEXT NOT NULL,
  import_notes TEXT NOT NULL
);

books(
  book_id INTEGER PRIMARY KEY,
  canonical_code TEXT NOT NULL UNIQUE,
  osis_code TEXT NOT NULL,
  title TEXT NOT NULL,
  testament TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  is_canonical INTEGER NOT NULL
);

canonical_verses(
  canonical_verse_id INTEGER PRIMARY KEY,
  canonical_ref TEXT NOT NULL UNIQUE,
  osis_ref TEXT NOT NULL,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  subverse TEXT NOT NULL DEFAULT '',
  sort_key INTEGER NOT NULL
);

source_texts(
  source_text_id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  code TEXT NOT NULL,
  scope TEXT NOT NULL,
  language TEXT NOT NULL,
  priority INTEGER NOT NULL
);

module_verses(
  module_verse_id INTEGER PRIMARY KEY,
  source_text_id TEXT NOT NULL,
  native_ref TEXT NOT NULL,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  subverse TEXT NOT NULL DEFAULT '',
  text_plain TEXT NOT NULL,
  text_display TEXT NOT NULL,
  tokens_count INTEGER NOT NULL,
  sort_key INTEGER NOT NULL
);

module_verse_links(
  module_verse_id INTEGER NOT NULL,
  canonical_verse_id INTEGER NOT NULL,
  link_kind TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  PRIMARY KEY(module_verse_id, canonical_verse_id)
);

tokens(
  token_id INTEGER PRIMARY KEY,
  module_verse_id INTEGER NOT NULL,
  source_text_id TEXT NOT NULL,
  token_order INTEGER NOT NULL,
  source_ref TEXT NOT NULL,
  text_type TEXT NOT NULL,
  surface TEXT NOT NULL,
  surface_normalized TEXT NOT NULL,
  surface_search TEXT NOT NULL,
  transliteration TEXT NOT NULL,
  lemma TEXT NOT NULL,
  morphology TEXT NOT NULL,
  gloss TEXT NOT NULL,
  raw_json TEXT NOT NULL
);

token_strongs(
  token_strong_id INTEGER PRIMARY KEY,
  token_id INTEGER NOT NULL,
  strong TEXT NOT NULL,
  raw_strong TEXT NOT NULL,
  role TEXT NOT NULL,
  segment_order INTEGER NOT NULL,
  segment_surface TEXT NOT NULL,
  is_primary INTEGER NOT NULL
);

import_warnings(
  warning_id INTEGER PRIMARY KEY,
  source_id TEXT NOT NULL,
  severity TEXT NOT NULL,
  code TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  message TEXT NOT NULL,
  raw_json TEXT NOT NULL
);
```

## Phase 4 - TAGNT Import

- [ ] Parse headers and skip non-data rows.
- [ ] Parse only data rows matching NT references such as `Mat.1.1#01=NKO`.
- [ ] Parse source reference into:
  - [ ] book code
  - [ ] chapter
  - [ ] verse
  - [ ] token order
  - [ ] text type
- [ ] Import only tokens whose edition list contains `NA28`.
- [ ] Preserve original source row in `tokens.raw_json`.
- [ ] Parse Greek surface text.
- [ ] Strip display punctuation into `surface_search`.
- [ ] Parse transliteration when present in parentheses.
- [ ] Parse `dStrong = Grammar`.
- [ ] Normalize Strong keys:
  - [ ] `G0001 -> G1`
  - [ ] `G0011 -> G11`
  - [ ] `G0976 -> G976`
  - [ ] `G2424G -> G2424`.
- [ ] Store raw padded value in `raw_strong`.
- [ ] Parse morphology into `tokens.morphology`.
- [ ] Parse lemma/gloss from dictionary field.
- [ ] Parse alternate Strong values into `token_strongs(role = 'alt')`.
- [ ] Preserve textual variants in `raw_json` or a future variants table, but do not include non-NA28 tokens in the main NA28 text.
- [ ] Generate `module_verses.text_plain` by joining NA28 tokens in source order.
- [ ] Add tests for Matthew 1:1 token import.
- [ ] Add tests for a verse with TR/Byz-only extra tokens that must not appear in NA28 text.
- [ ] Add tests for a verse with meaning/spelling variants.

## Phase 5 - LXX Import

- [ ] Export CrossWire SWORD `LXX` to an intermediate parseable format.
- [ ] Preserve word-level Strong/morph tags from the SWORD module.
- [ ] Store the exact CrossWire module version in `module_sources`.
- [ ] Map LXX source book names to the 39 canonical OT books.
- [ ] Exclude deuterocanonical/apocryphal books.
- [ ] Exclude Psalm 151.
- [ ] Exclude Odes and Prayer of Manasseh.
- [ ] Exclude Greek additions to Daniel.
- [ ] Exclude Greek additions to Esther unless manually confirmed as canonical Protestant verse text.
- [ ] Parse each verse into `module_verses`.
- [ ] Parse each word into `tokens`.
- [ ] Parse Greek lemma into `tokens.lemma`.
- [ ] Parse morphology into `tokens.morphology`.
- [ ] Parse Strong values into `token_strongs`.
- [ ] Normalize LXX Strong keys without leading zeroes.
- [ ] Add import warnings for missing Strong values.
- [ ] Add import warnings for unparseable morphology.
- [ ] Add import warnings for ambiguous source-native verse mappings.
- [ ] Add tests for Genesis 1:1.
- [ ] Add tests for Psalms numbering.
- [ ] Add tests proving apocryphal books are excluded.
- [ ] Add tests proving Daniel/Esther additions do not enter the canonical module.

## Phase 6 - Lexicon And Morphology Support

- [ ] Import `TBESG` into a source lexicon staging table or dictionary build input.
- [ ] Import `TFLSJ 0-5624`.
- [ ] Import `TFLSJ extra`.
- [ ] Import `TEGMC`.
- [ ] Normalize every Greek Strong number to the same no-leading-zero format.
- [ ] Verify all NT Strong keys from TAGNT resolve to lexicon entries or produce warnings.
- [ ] Verify all LXX Strong keys resolve to lexicon entries or produce warnings.
- [ ] Keep source definitions and morphology explanations separate from Bible module text if they belong to the dictionary DB.

## Phase 7 - Strong Dictionary Target Model

- [ ] Decide whether to replace `GreekWords`/`GreekDescs` or add new Strong dictionary tables beside them.
- [ ] Keep localized dictionary descriptions separate from non-localized Strong occurrence data.
- [ ] Use normalized Strong as the stable key.
- [ ] Store all attested forms from `NA28_LXX`.
- [ ] Store complete occurrence lists for each form.
- [ ] Store occurrence links by `canonical_verse_id` and `canonical_ref`.
- [ ] Keep enough token context to display the exact form in the dictionary.
- [ ] Do not duplicate Bible verse text inside dictionary occurrence tables.

### Proposed Dictionary Occurrence Tables

```sql
strong_entries(
  strong TEXT PRIMARY KEY,
  raw_primary_strong TEXT NOT NULL,
  language TEXT NOT NULL,
  lemma TEXT NOT NULL,
  transliteration TEXT NOT NULL,
  gloss TEXT NOT NULL,
  morphology TEXT NOT NULL,
  source_lexicon TEXT NOT NULL
);

strong_forms(
  strong TEXT NOT NULL,
  form TEXT NOT NULL,
  normalized_form TEXT NOT NULL,
  search_form TEXT NOT NULL,
  occurrences_count INTEGER NOT NULL,
  PRIMARY KEY(strong, normalized_form)
);

strong_form_occurrences(
  strong TEXT NOT NULL,
  normalized_form TEXT NOT NULL,
  canonical_verse_id INTEGER NOT NULL,
  canonical_ref TEXT NOT NULL,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  token_order INTEGER NOT NULL,
  source_module_code TEXT NOT NULL,
  source_text_code TEXT NOT NULL,
  surface TEXT NOT NULL,
  lemma TEXT NOT NULL,
  morphology TEXT NOT NULL,
  PRIMARY KEY(strong, normalized_form, canonical_verse_id, token_order)
);
```

## Phase 8 - Strong Forms And Occurrence Builder

- [ ] Read only `NA28_LXX` tokens.
- [ ] Use only `token_strongs.is_primary = 1` for default occurrence counts.
- [ ] Decide whether alternate Strong tags should create secondary occurrence records.
- [ ] Normalize token surface forms consistently.
- [ ] Generate `strong_forms`.
- [ ] Generate `strong_form_occurrences`.
- [ ] Verify every occurrence has a valid `canonical_verse_id`.
- [ ] Verify every occurrence has a valid `canonical_ref`.
- [ ] Verify `occurrences_count` equals the number of occurrence rows.
- [ ] Add a spot-check test for `G746` in `Gen.1.1`.
- [ ] Add a spot-check test for `G976` in `Mat.1.1`.
- [ ] Add a test that `G0746` never appears as a stored primary key.
- [ ] Add a test that searching by `G746` finds rows imported from `G0746`.
- [ ] Add tests for words occurring multiple times in one verse.
- [ ] Add tests for words with several surface forms.

## Phase 9 - Parallel Reading Contract

- [ ] Define a Bible module discovery API.
- [ ] Define a query that opens one `canonical_verse_id` across selected modules.
- [ ] Ensure `NA28_LXX`, KJV, RST, and future Spanish modules can all use the same `module_verse_links` contract.
- [ ] For translation modules, require at minimum:
  - [ ] `bible_modules`
  - [ ] `module_sources`
  - [ ] `books`
  - [ ] `canonical_verses`
  - [ ] `source_texts`
  - [ ] `module_verses`
  - [ ] `module_verse_links`
- [ ] Make `tokens` and `token_strongs` optional for translation modules.
- [ ] Add a test fixture with one verse in `NA28_LXX`, KJV, RST, and Spanish-like mock module.
- [ ] Verify the same `canonical_verse_id` returns all selected module verses.

## Phase 10 - Database Integration

- [ ] Decide whether `bible_na28_lxx.sqlite` is managed by the current common/localized DB sync flow or a new Bible module sync flow.
- [ ] If managed by the current sync flow, update manifest generation.
- [ ] If managed separately, create a Bible module manifest.
- [ ] Add `db_metadata.schema_version`.
- [ ] Add `db_metadata.data_version`.
- [ ] Add `db_metadata.date`.
- [ ] Add app-side version loader support for Bible module databases.
- [ ] Add native file sync support if the module is downloadable.
- [ ] Add web DB URI/manifest support if the module is available on web.
- [ ] Ensure large DB downloads do not block startup.
- [ ] Ensure missing Bible module DB fails gracefully.

## Phase 11 - Content Tool Bible Tab Architecture

Current `scripts/content_tool` findings to preserve:

- The app entry point is `TopicContentTool` in `scripts/content_tool/app.py`.
- The UI is built in `CoreUiMixin._build_ui`.
- The main notebook already has a `bibles_section`.
- The current Bible tab is only a placeholder created through `_build_future_section`.
- Common DB, localized DB, publish, metadata, manifest, and release publication logic live mostly in `CoreDbMixin`.
- Strong dictionary editing currently lives in `StrongsMixin` and uses `greek_words` in `revelation.sqlite` plus localized `greek_descs`.
- Publish and manifest flows currently collect only `revelation*.sqlite`.
- Localized DB discovery currently collects only `revelation_*.sqlite`.

Planned implementation:

- [ ] Add `scripts/content_tool/mixins/bibles.py`.
- [ ] Export `BiblesMixin` from `scripts/content_tool/mixins/__init__.py`.
- [ ] Add `BiblesMixin` to `TopicContentTool` before `CoreDbMixin` and `CoreUiMixin`.
- [ ] Replace the placeholder `_build_future_section(self.bibles_section, ...)` with `_build_bibles_section(self.bibles_section)`.
- [ ] Keep Bible module state separate from the current selected localized DB.
- [ ] Add a separate `bible_connection`.
- [ ] Add a separate `current_bible_db_path`.
- [ ] Add a separate `bible_db_files` map discovered from `bible_*.sqlite`.
- [ ] Add `BibleModuleSummary`, `BibleBookSummary`, `BibleVerseSummary`, `BibleTokenSummary`, `BibleStrongSummary`, and `BibleImportWarningSummary` dataclasses to `models.py`.
- [ ] Add Bible close/clear/load helpers without interfering with `_close_local_connection`.
- [ ] Update `_close_connection` so it also closes the Bible DB connection.
- [ ] Update `_clear_all_db_views` so it clears Bible tab state.
- [ ] Update `_refresh_db_list` so it refreshes localized DBs, common DB, and Bible module DBs independently.
- [ ] Update `_update_section_db_labels` so the Bible tab displays the selected Bible module DB, not the selected localized DB.
- [ ] Update `_update_ui_availability` and `_set_editor_controls_enabled` to include Bible widgets.
- [ ] Ensure opening the content tool does not mutate `bible_*.sqlite` timestamps.
- [ ] Ensure switching Bible modules prompts about unsaved Bible edits without forcing a localized article save.

## Phase 12 - Content Tool Bible Module UI And Editing

Goal: the `Библии` tab must be the main desktop UI for creating and maintaining `bible_na28_lxx.sqlite`, and later any `bible_*.sqlite` module.

- [ ] Add a top Bible module toolbar:
  - [ ] working DB folder label
  - [ ] Bible module selector
  - [ ] refresh modules
  - [ ] create empty module
  - [ ] import/build `NA28_LXX`
  - [ ] backup selected module
  - [ ] validate selected module
  - [ ] rebuild Strong forms/occurrences from selected module
- [ ] Add a left navigation pane:
  - [ ] module list
  - [ ] 66-book tree
  - [ ] chapter selector
  - [ ] verse list
  - [ ] filters by canonical ref, native ref, surface form, lemma, Strong, morphology, warning status
- [ ] Add right-side tabs:
  - [ ] module metadata
  - [ ] sources
  - [ ] books/canon
  - [ ] verses
  - [ ] tokens
  - [ ] Strong links
  - [ ] import warnings
  - [ ] build/import report
- [ ] In metadata tab, edit `bible_modules` and `module_sources` fields.
- [ ] In books/canon tab, show exactly the 66 canonical books and lock accidental apocrypha insertion.
- [ ] In verses tab, edit:
  - [ ] `native_ref`
  - [ ] `canonical_verse_id` link
  - [ ] `text_plain`
  - [ ] `text_display`
  - [ ] `tokens_count`
  - [ ] `sort_key`
- [ ] Add a "rebuild verse text from tokens" action.
- [ ] Add a "sync tokens_count" action.
- [ ] In tokens tab, edit:
  - [ ] token order
  - [ ] surface
  - [ ] normalized/search forms preview
  - [ ] transliteration
  - [ ] lemma
  - [ ] morphology
  - [ ] gloss
  - [ ] source ref
  - [ ] text type
- [ ] Keep `raw_json` visible but read-only by default.
- [ ] In Strong links tab, edit token Strong rows:
  - [ ] normalized `strong`
  - [ ] source `raw_strong`
  - [ ] role
  - [ ] segment order
  - [ ] segment surface
  - [ ] primary flag
- [ ] Add a Strong normalization preview in the editor: `G0746 -> G746`.
- [ ] Reject saved Strong keys with leading zeroes in `strong`.
- [ ] Allow padded source values only in `raw_strong`.
- [ ] Add token-level validation before save.
- [ ] Add verse-level validation before save.
- [ ] Add module-level validation before publish.
- [ ] Store manual edits transactionally and touch `db_metadata` only after successful commit.
- [ ] Add a per-module backup before destructive import/rebuild operations.
- [ ] Add a diff/preview dialog before applying a full `NA28_LXX` rebuild over an existing module.
- [ ] Add an import wizard for `NA28_LXX`:
  - [ ] choose source cache folder
  - [ ] validate source checksums
  - [ ] choose target module path
  - [ ] dry-run import
  - [ ] show counts by source, book, verse, token, Strong, warning
  - [ ] apply import
  - [ ] write import report into the DB and as a sidecar log file
- [ ] Add a Strong dictionary rebuild action:
  - [ ] read selected `bible_na28_lxx.sqlite`
  - [ ] preview number of Strong entries, forms, and occurrences
  - [ ] show destructive changes to current dictionary tables
  - [ ] backup affected DB files
  - [ ] apply replacement/update to Strong dictionary tables
  - [ ] touch common/localized DB metadata as needed
  - [ ] reload the Strong tab after completion
- [ ] Add read-only safety mode for generated-source fields, with an explicit "unlock manual edit" confirmation.
- [ ] Add status bar messages and message-log entries for Bible actions.

## Phase 13 - Content Tool Bible Publish And Manifest Flow

Current publish/release flow must be generalized beyond `revelation*.sqlite`.

- [ ] Add a DB family resolver, for example:
  - [ ] `common`: `revelation.sqlite`
  - [ ] `localized`: `revelation_<lang>.sqlite`
  - [ ] `bible`: `bible_*.sqlite`
- [ ] Add `BIBLE_DB_SCHEMA_VERSION`.
- [ ] Update `_db_schema_version_for_path` to return Bible schema version for `bible_*.sqlite`.
- [ ] Update `_mark_local_db_manifest_dirty` to include `bible_*.sqlite`.
- [ ] Update `_refresh_local_db_manifest_for_dir` to include both `revelation*.sqlite` and `bible_*.sqlite`, unless a separate Bible manifest is chosen.
- [ ] Update `_copy_to_web_db` source file discovery to include `bible_*.sqlite`.
- [ ] Update `_prepare_release_publish` source file discovery to include `bible_*.sqlite`.
- [ ] Update extra target DB detection so stale `bible_*.sqlite` files in `web/db` are reported.
- [ ] Keep `_find_localized_dbs_with_enabled_tests` limited to localized `revelation_*.sqlite`.
- [ ] Update confirmation dialogs so changed Bible tables are shown clearly.
- [ ] Update Git commit message builders to mention Bible module DB changes.
- [ ] Update Supabase publish path handling for Bible DB files.
- [ ] Decide whether Bible modules share `web/db/manifest.json` or get `web/db/bible_manifest.json`.
- [ ] If sharing `manifest.json`, update app-side manifest parsing to tolerate Bible DB entries while preserving current common/localized behavior.
- [ ] If using `bible_manifest.json`, add a separate content-tool writer, release comparison, Supabase upload, and app-side loader.
- [ ] Add a warning if a Bible module DB lacks required `db_metadata`.
- [ ] Add a warning if a Bible module DB fails module-level validation before publish.
- [ ] Ensure publish never silently strips large Bible DB files from the manifest.
- [ ] Add tests for `bible_na28_lxx.sqlite` manifest entries.
- [ ] Add tests for publish-plan comparison with Bible DB files.
- [ ] Add tests for release publish including Bible DB files.
- [ ] Add tests that localized test-article warnings do not inspect Bible DB files.
- [ ] Add tests that `db_metadata` touch and manifest refresh work for `bible_*.sqlite`.

## Phase 14 - App Code Integration

- [ ] Add `lib/infra/db/bible/` Drift database definitions.
- [ ] Generate Drift code with `dart run build_runner build --delete-conflicting-outputs`.
- [ ] Add repository/gateway interfaces under the existing module boundaries.
- [ ] Add application services for:
  - [ ] Bible module discovery
  - [ ] verse lookup by `canonical_verse_id`
  - [ ] Strong occurrence lookup by normalized Strong
  - [ ] parallel verse lookup across modules
- [ ] Keep UI out of scope until DB and services are stable.
- [ ] Use BLoC/Cubit when presentation work begins.
- [ ] Do not pass `BuildContext` into services or blocs.

## Phase 15 - Tests And Quality Gates

- [ ] Add parser unit tests.
- [ ] Add source-cache manifest tests.
- [ ] Add Bible schema tests.
- [ ] Add canonical verse mapping tests.
- [ ] Add LXX canon-filter tests.
- [ ] Add TAGNT NA28-filter tests.
- [ ] Add Strong normalization tests.
- [ ] Add Strong dictionary occurrence generation tests.
- [ ] Add repository/service tests for verse lookup.
- [ ] Add repository/service tests for parallel lookup.
- [ ] Add content-tool Bible tab UI construction tests where feasible.
- [ ] Add content-tool Bible DB discovery tests.
- [ ] Add content-tool Bible editor save/reload tests.
- [ ] Add content-tool Bible validation tests.
- [ ] Add content-tool Bible publish/manifest tests.
- [ ] Run `dart format .`.
- [ ] Run `flutter analyze`.
- [ ] Run `flutter test`.
- [ ] Run `dart run scripts/check_forbidden_patterns.dart`.
- [ ] Run `rg "package:provider|ChangeNotifier|notifyListeners" lib test` if presentation/state code is touched.
- [ ] Run `rg "BuildContext" lib/features --glob "**/application/**/*.dart" --glob "**/presentation/bloc/**/*.dart"` if state/presentation code is touched.

## Phase 16 - Content Validation

- [ ] Count imported books: exactly 66.
- [ ] Count OT books: exactly 39.
- [ ] Count NT books: exactly 27.
- [ ] Verify no apocryphal/deuterocanonical book exists in `books`.
- [ ] Verify no apocryphal/deuterocanonical source ref exists in `module_verses`.
- [ ] Verify every `module_verse` links to at least one `canonical_verse`.
- [ ] Verify every `canonical_verse` expected in the 66-book canon has a module verse or a documented warning.
- [ ] Verify every token belongs to a valid module verse.
- [ ] Verify every primary Strong occurrence uses the no-leading-zero format.
- [ ] Verify `strong_form_occurrences` can open a verse in `NA28_LXX`.
- [ ] Verify `strong_form_occurrences` can open the same verse in a mock translation module.
- [ ] Produce an import report with counts and warning summaries.

## Phase 17 - Acknowledgements

- [ ] Add adopted third-party Bible data sources to `assets/data/about_libraries.xml`.
- [ ] Keep acknowledgements limited to sources actually redistributed or used as bundled/generated app data.
- [ ] Use exact source pages and exact license pages where available.
- [ ] Do not add entries for temporary scripts or internal generated files.
- [ ] Add/update localized acknowledgement display text only if current app architecture requires it.
- [ ] Add tests if acknowledgement parsing expectations change.

### Planned Acknowledgement Entries

Use this as the source checklist when updating `assets/data/about_libraries.xml`.

```xml
<library>
    <name>@BibleData STEPBible-Data</name>
    <idIcon>dictionary</idIcon>
    <license>Creative Commons Attribution 4.0 International (CC BY 4.0)</license>
    <officialSite>https://github.com/STEPBible/STEPBible-Data</officialSite>
    <licenseLink>https://creativecommons.org/licenses/by/4.0/</licenseLink>
</library>
<library>
    <name>@BibleData TAGNT - Translators Amalgamated Greek NT</name>
    <idIcon>dictionary</idIcon>
    <license>Creative Commons Attribution 4.0 International (CC BY 4.0)</license>
    <officialSite>https://github.com/STEPBible/STEPBible-Data/tree/master/Translators%20Amalgamated%20OT%2BNT</officialSite>
    <licenseLink>https://creativecommons.org/licenses/by/4.0/</licenseLink>
</library>
<library>
    <name>@BibleData TBESG - Translators Brief Lexicon of Extended Strongs for Greek</name>
    <idIcon>dictionary</idIcon>
    <license>Creative Commons Attribution 4.0 International (CC BY 4.0)</license>
    <officialSite>https://github.com/STEPBible/STEPBible-Data/tree/master/Lexicons</officialSite>
    <licenseLink>https://creativecommons.org/licenses/by/4.0/</licenseLink>
</library>
<library>
    <name>@BibleData TFLSJ - Translators Formatted Full LSJ Bible Lexicon</name>
    <idIcon>dictionary</idIcon>
    <license>Creative Commons Attribution 4.0 International (CC BY 4.0)</license>
    <officialSite>https://github.com/STEPBible/STEPBible-Data/tree/master/Lexicons</officialSite>
    <licenseLink>https://creativecommons.org/licenses/by/4.0/</licenseLink>
</library>
<library>
    <name>@BibleData TEGMC - Translators Expansion of Greek Morphology Codes</name>
    <idIcon>dictionary</idIcon>
    <license>Creative Commons Attribution 4.0 International (CC BY 4.0)</license>
    <officialSite>https://github.com/STEPBible/STEPBible-Data/tree/master/Morphology%20codes</officialSite>
    <licenseLink>https://creativecommons.org/licenses/by/4.0/</licenseLink>
</library>
<library>
    <name>@BibleData CrossWire LXX - Septuagint, Morphologically Tagged Rahlfs'</name>
    <idIcon>dictionary</idIcon>
    <license>Copyrighted; Free non-commercial distribution</license>
    <officialSite>https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=LXX</officialSite>
    <licenseLink>https://www.crosswire.org/sword/copyright/ModInfoCopyright.jsp?modName=LXX</licenseLink>
</library>
<library>
    <name>@BibleData CCAT LXX Morphological Data</name>
    <idIcon>dictionary</idIcon>
    <license>Scholarly and educational use; redistributed through CrossWire LXX terms</license>
    <officialSite>http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/</officialSite>
    <licenseLink>https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=LXX</licenseLink>
</library>
```

## Phase 18 - Documentation And Cleanup

- [ ] Decide whether the Bible module architecture needs permanent RU/EN architecture docs.
- [ ] If permanent architecture docs are added, update RU/EN twin documents together.
- [ ] If permanent docs are added, update README navigation according to repository rules.
- [ ] Add a changelog entry only if the finished work is user-visible in the release.
- [ ] Remove this temporary roadmap file after completion.
- [ ] Confirm `.github/change_checklist.md` is satisfied for the final change set.

## Completion Definition

- [ ] `bible_na28_lxx.sqlite` can be built from a clean source cache.
- [ ] The module contains exactly the 66 canonical books.
- [ ] The module contains LXX OT and NA28 NT text.
- [ ] Strong numbers are stored without leading zeroes.
- [ ] The updated Strong dictionary contains every attested form from `NA28_LXX`.
- [ ] Every Strong form occurrence links to a stable `canonical_verse_id`.
- [ ] The same `canonical_verse_id` can open the matching verse in other Bible modules.
- [ ] The content tool Bible tab can open, edit, validate, rebuild, and backup `bible_na28_lxx.sqlite`.
- [ ] The content tool publish and release flows include `bible_*.sqlite` files intentionally and visibly.
- [ ] Tests and quality gates pass.
- [ ] Acknowledgements are updated for all redistributed third-party data sources.
- [ ] The temporary roadmap is deleted.
