# Ukrainian stage 7 evidence-alignment fixtures

All text and alignment records in this directory are invented for tests and
dedicated to the public domain under CC0-1.0. They contain no OH1988 verse
text and no text copied from an original-language or translation corpus.

Book/reference-shaped identifiers are synthetic metadata used only to test
parsing, versification and stable-ID contracts.

SPDX-License-Identifier: CC0-1.0

`candidate_generator_cases.json` covers complete manual bridge groups,
non-positional repeated-token alternatives, rejected partial/cross-verse
bridges, zero-vote legacy rows, direct named-entity transliteration and direct
Strong-description lexical evidence.

`contextual_alignment_cases.json` covers an invented multilingual contextual
observation, strict bidirectional thresholding, an excluded unknown subword,
and connected one-to-one/many-to-many candidates. The ancient-script and
Ukrainian words are isolated invented test vocabulary, not copied verses.

`statistical_alignment_cases.json` covers invented parallel token types for
out-of-fold IBM Model 1 training, bidirectional mutual-best symmetrization,
reordering, repetition, exact ties, compounds and an unseen held-out pair.

`gold_compact_review_cases.json` covers explicit compact many-to-many review
answers, verse-local `oNNN`/`tNNN` indices, target nulls, and both full-packet
and frozen-shard expansion/merge contracts with reviewer provenance.

`external_wrapper_normalization_cases.json` covers the one permitted external
ChatGPT wrapper migration: byte-exact metadata, unchanged answer-free context,
verbatim `groups`/`target_nulls`, reviewer provenance, and fail-closed rejection
of context edits or extra answer channels.

`textual_render_contract_cases.json` covers five invented post-candidate
textual-overlay shapes, including three no-render alternatives, one selected
primary component, one Strong-equivalent alternative group, and their exact
finalized-gold hyperedge/target-accounting joins.

`author_comment_evidence_cases.json` covers invented author-note language,
transliteration, grammar, textual-variant and zero-vote evidence contracts.
