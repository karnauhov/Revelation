/* Pure contracts shared with browser tests; no storage or network writes. */
(function (root) {
  "use strict";
  class LatestRequest {
    constructor() { this.revision = 0; }
    begin() { return ++this.revision; }
    current(token) { return token === this.revision; }
  }
  function filterCases(cases, query, reviewClass, category) {
    const q = query.trim().toLocaleLowerCase();
    return cases.filter(c => (!reviewClass || c.final_class === reviewClass) &&
      (!category || (category === "conflict" ? c.conflict_count > 0 : c.structural.includes(category))) &&
      (!q || `${c.target_ref} ${c.target_label} ${c.case_id}`.toLocaleLowerCase().includes(q)));
  }
  function makeDraft(payload, reviewer, verdict, rationale) {
    const allowed = ["needs_review", "incomplete_group", "extra_participant", "conflicting_groups", "unresolved"];
    if (!reviewer.trim() || !rationale.trim() || !allowed.includes(verdict)) throw new Error("Укажите reviewer и обоснование.");
    if (!payload.packet_sha256 || !payload.build_manifest_sha256 || payload.case.A_auto !== 0) throw new Error("Нет действующего source binding.");
    const c = payload.case;
    return {version: "review78-note-v1", status: "review_note_draft", is_label: false, is_override: false,
      reviewer: reviewer.trim(), verdict, rationale: rationale.trim(), timestamp: new Date().toISOString(),
      case_id: c.case_id, target_ref: c.target_ref, semantic_identity: c.semantic_identity,
      nearest_gold_edge_ids: c.nearest_gold_edge_ids, source_graph_row_digest: c.source_graph_row_digest,
      gold_row_digests: c.gold_row_digests, packet_sha256: payload.packet_sha256,
      build_manifest_sha256: payload.build_manifest_sha256, A_auto: 0, production_acceptance: 0};
  }
  function validatePayload(payload, requested, manifest) {
    if (payload.case.case_id !== requested || payload.build_manifest_sha256 !== manifest) throw new Error("Изменился пакет или выбран другой case. Перезагрузите workbench.");
    if (payload.packet.A_auto !== 0 || payload.case.A_auto !== 0) throw new Error("A_auto guard нарушен");
    return payload;
  }
  const api = {LatestRequest, filterCases, makeDraft, validatePayload};
  root.ReviewCore = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof globalThis === "undefined" ? this : globalThis);
