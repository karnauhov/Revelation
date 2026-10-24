"use strict";
const test = require("node:test"), assert = require("node:assert/strict");
const {LatestRequest, filterCases, makeDraft, validatePayload} = require("../core.js");
test("rapid switching: latest response wins", async () => {
  const guard = new LatestRequest(), applied = [];
  const old = guard.begin(), current = guard.begin();
  await Promise.resolve().then(() => { if (guard.current(current)) applied.push("current"); });
  await Promise.resolve().then(() => { if (guard.current(old)) applied.push("old"); });
  assert.deepEqual(applied, ["current"]);
});
test("independent class taxonomy and text filters", () => {
  const cases = [{case_id:"1",target_ref:"Gen.1.1",target_label:"Бог",final_class:"B_review",structural:["extra_participant"],conflict_count:2}, {case_id:"2",target_ref:"Gen.1.2",target_label:"земля",final_class:"C_unresolved",structural:["incomplete_group"],conflict_count:0}];
  assert.deepEqual(filterCases(cases,"бог","B_review","conflict").map(c=>c.case_id), ["1"]);
  assert.deepEqual(filterCases(cases,"","","incomplete_group").map(c=>c.case_id), ["2"]);
  assert.equal(filterCases(cases,"Gen.1.2","B_review","").length,0);
});
test("export is a bound draft preserving full many-to-many identity, never label", () => {
  const payload = {packet_sha256:"packet",build_manifest_sha256:"build",case:{A_auto:0,case_id:"case",target_ref:"Gen.1.1",semantic_identity:["Gen.1.1","many_to_many",["a","b"],["x","y"],null],nearest_gold_edge_ids:["g1","g2"],gold_row_digests:{g1:"d1",g2:"d2"},source_graph_row_digest:"graph"}};
  const note = makeDraft(payload,"reviewer","unresolved","Не хватает доказательства.");
  assert.deepEqual(note.semantic_identity,payload.case.semantic_identity);
  assert.equal(note.is_label,false);assert.equal(note.is_override,false);assert.equal(note.production_acceptance,0);
  assert.throws(()=>makeDraft(payload,"","unresolved","reason"));
  assert.throws(()=>makeDraft(payload,"reviewer","accept","reason"));
  assert.throws(()=>makeDraft({...payload,packet_sha256:null},"reviewer","unresolved","reason"));
});
test("case and build must match the displayed list snapshot", () => {
  const payload = {build_manifest_sha256:"b",case:{case_id:"c",A_auto:0},packet:{A_auto:0}};
  assert.equal(validatePayload(payload,"c","b"),payload);
  assert.throws(()=>validatePayload(payload,"other","b"));
  assert.throws(()=>validatePayload(payload,"c","new-build"));
});
