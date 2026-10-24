"use strict";
const $ = id => document.getElementById(id);
const state = {cases: [], filtered: [], visible: 100, selected: null, payload: null, manifest: null, drafts: new Map()};
const guard = new ReviewCore.LatestRequest();
let abort;
const terms = {incomplete_group: "Неполная группа", extra_participant: "Лишние endpoints", wrong_endpoints: "Неверные endpoints", relation_null_semantics: "Relation / NULL", repetition: "Повторение · hint", morphology_unresolved: "Morphology · unresolved", polysemy: "Polysemy · hint", textual_conflict: "Textual conflict · hint"};
function el(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }
function detail(title, node, open = false) { const d = el("details"); d.open = open; d.append(el("summary", title), node); return d; }
function json(value) { return el("pre", JSON.stringify(value, null, 2)); }
function badge(text, alert = false) { return el("span", text, "badge" + (alert ? " alert" : "")); }
function token(id, side, ctx, highlight = "") {
  const n = ctx[side].get(id); if (!n) throw new Error("Нет endpoint: " + id);
  const box = el("span", undefined, "token " + highlight);
  const surface = el("span", side === "original" ? (n.surface_raw || n.surface || n.surface_normalized || id) : n.surface, "surface"); surface.dir = "auto";
  box.append(surface);
  if (side === "original") {
    box.append(el("small", (n.strong_classic || []).join(" · ") || "Strong в source не указан"));
    box.append(el("small", n.morphology_raw || n.morphology || "Morphology не указана"));
  } else box.append(el("small", `scalar ${n.start_scalar}–${n.end_scalar} · byte ${n.start_byte}–${n.end_byte}`));
  box.append(el("small", id));
  if (ctx.deferred[side].has(id)) box.append(badge("Registered deferral · не переоткрывается", true));
  return box;
}
function tokens(ids, side, ctx, highlight = "") {
  const box = el("div", undefined, "tokens");
  if (!ids.length) box.append(el("span", "∅", "muted"));
  else ids.forEach(id => box.append(token(id, side, ctx, highlight)));
  return box;
}
function sourceEvidence(edge, ctx) {
  const body = el("div");
  if (edge.provenance) {
    body.append(el("p", "Производные одного источника сохраняют общую dependency group. Число rows не является числом независимых подтверждений.", "muted"));
    for (const [i, group] of (edge.dependence_groups || []).entries()) body.append(detail(`Dependency group ${i + 1}: ${group.labels.join(" · ")}`, json(group)));
    for (const p of edge.provenance) {
      const block = el("div", undefined, "panel");
      block.append(el("h4", p.generator_id), el("p", `${p.input_channel} · ${p.candidate_id}`, "edgeid"));
      block.append(el("p", (p.evidence || []).map(e => e.kind || "evidence").join(" · "), "muted"));
      block.append(detail("Полное evidence и provenance", json(p)));
      body.append(block);
    }
  } else {
    body.append(el("p", "Историческая finalized gold-группа. Это существующая development-разметка.", "muted"));
    body.append(json(edge));
  }
  const originals = edge.original_token_ids.map(id => ctx.original.get(id));
  body.append(detail("Original source: locator, lemma, morphology, commit и SHA", json(originals)));
  const targets = edge.target_token_ids.map(id => ctx.target.get(id));
  body.append(detail("OH1988 endpoints: точные spans и digests", json(targets)));
  return detail("Source evidence и stable IDs", body);
}
function edgeCard(edge, ctx, title, cls = "", delta = null) {
  const box = el("section", undefined, "panel " + cls);
  box.append(el("h3", title), el("p", edge.edge_id, "edgeid"), badge(edge.relation));
  if (edge.null_reason) box.append(badge("NULL: " + edge.null_reason, true));
  box.append(el("h4", "Original · полная группа"), tokens(edge.original_token_ids, "original", ctx));
  box.append(el("h4", "OH1988 · полная группа"), tokens(edge.target_token_ids, "target", ctx));
  if (delta) {
    for (const [key, label, style] of [["missing_original", "Пропущенные original endpoints", "missing"], ["missing_target", "Пропущенные OH1988 endpoints", "missing"], ["extra_original", "Лишние original endpoints в prediction", "extra"], ["extra_target", "Лишние OH1988 endpoints в prediction", "extra"]]) {
      const row = el("div", undefined, "delta-row");
      row.append(el("div", label, "delta-label " + style + "-title"), tokens(delta[key], key.endsWith("original") ? "original" : "target", ctx, style)); box.append(row);
    }
    if (delta.relation_differs || delta.null_reason_differs) box.append(el("p", "Различаются relation / null semantics.", "notice"));
  }
  box.append(sourceEvidence(edge, ctx));
  return box;
}
function renderCase(payload) {
  const c = payload.case, p = payload.packet;
  if (p.A_auto !== 0 || c.A_auto !== 0) throw new Error("A_auto guard нарушен");
  const ctx = {original: new Map(p.original_nodes.map(n => [n.token_id, n])), target: new Map(p.target_nodes.map(n => [n.token_id, n])), deferred: {original: new Set(p.deferred_original_ids), target: new Set(p.deferred_target_ids)}};
  const edges = new Map(p.candidate_edges.map(e => [e.edge_id, e])), gold = new Map(p.historical_gold_edges.map(e => [e.edge_id, e]));
  const fragment = document.createDocumentFragment();
  fragment.append(el("div", "Development inspection. Ранее reviewed gold показан для поиска ошибок; этот экран не является blind audit или новой сертификацией.", "notice"));
  fragment.append(el("h2", c.target_ref), badge(c.final_class));
  [...c.structural, ...c.evidence_hints_not_causal_labels].forEach(t => fragment.append(badge(terms[t] || t, c.structural.includes(t))));
  const verse = el("section", undefined, "verse");
  verse.append(el("div", "OH1988 · точный source text", "eyebrow"), el("p", p.oh1988_source.plain_text_nfc, "verse-text"));
  verse.append(detail("Source mapping / печатные страницы / SHA", json(p.oh1988_source)));
  fragment.append(verse);
  const cols = el("div", undefined, "cols");
  const left = el("div"), right = el("section", undefined, "panel expected");
  left.append(edgeCard(edges.get(c.prediction_edge_id), ctx, "Frozen top-1 prediction", "predicted"));
  right.append(el("h3", `Ближайшие gold-группы · ${c.gold_comparisons.length}`), el("p", "Каждая группа сравнивается отдельно. Ties и shared declarations сохраняются целиком.", "muted"));
  c.gold_comparisons.forEach((d, i) => right.append(edgeCard(gold.get(d.expected_edge_id), ctx, `Gold-группа ${i + 1}`, "gold-comparison", d)));
  cols.append(left, right); fragment.append(cols);
  const conflicts = el("div");
  if (!c.conflicting_candidate_edge_ids.length) conflicts.append(el("p", "Конфликтующих eligible candidates нет; отсутствие не означает NULL.", "muted"));
  c.conflicting_candidate_edge_ids.forEach((id, i) => {
    const edge = edges.get(id), ranks = p.nbest.filter(d => d.edge_ids.includes(id)).map(d => d.rank);
    const wrap = el("div"); wrap.append(el("p", ranks.length ? "Есть в decomposition ranks: " + ranks.join(", ") : "В сохранённые n-best не входит", "muted"));
    wrap.append(edgeCard(edge, ctx, "Полный конфликтующий hyperedge"));
    conflicts.append(detail(`${i + 1}. ${edge.relation} · ${edge.original_token_ids.length} original → ${edge.target_token_ids.length} OH1988`, wrap));
  });
  fragment.append(detail(`Конфликтующие hyperedges · ${c.conflicting_candidate_edge_ids.length}`, conflicts, true));
  if (c.compatible_shared_candidate_edge_ids.length) {
    const shared = el("div"); c.compatible_shared_candidate_edge_ids.forEach(id => shared.append(edgeCard(edges.get(id), ctx, "Совместимый shared candidate")));
    fragment.append(detail(`Совместимые shared declarations · ${c.compatible_shared_candidate_edge_ids.length}`, shared));
  }
  const nbest = el("div");
  p.nbest.forEach(d => {
    const group = el("div");
    d.edge_ids.forEach(id => group.append(edgeCard(edges.get(id), ctx, "Constituent hyperedge")));
    nbest.append(detail(`Decomposition ${d.rank} · ${d.edge_ids.length} полных hyperedges`, group));
  });
  fragment.append(detail("Полные сохранённые decompositions", nbest));
  fragment.append(detail("Все historical gold-группы этого стиха", (() => { const n = el("div"); p.historical_gold_edges.forEach(e => n.append(edgeCard(e, ctx, "Historical gold"))); return n; })()));
  const note = el("section", undefined, "panel"); note.append(el("h3", "Заметка reviewer"), el("p", "Черновики сохраняются при переключении случаев в этой вкладке. Скачайте нужные заметки до её закрытия. Экспорт не меняет gold и не принимает Strong links.", "muted"));
  const grid = el("div", undefined, "note-grid");
  const nameLabel = el("label", "Reviewer"), name = el("input"); name.id = "reviewer"; name.autocomplete = "off"; nameLabel.append(name);
  const verdictLabel = el("label", "Тип заметки"), verdict = el("select"); verdict.id = "verdict";
  [["needs_review", "Нужна проверка"], ["incomplete_group", "Неполная группа"], ["extra_participant", "Лишний endpoint"], ["conflicting_groups", "Конфликт групп"], ["unresolved", "Неразрешённый случай"]].forEach(([v, t]) => { const option = el("option", t); option.value = v; verdict.append(option); }); verdictLabel.append(verdict); grid.append(nameLabel, verdictLabel);
  const rationaleLabel = el("label", "Обоснование и source evidence"), rationale = el("textarea"); rationale.id = "rationale"; rationaleLabel.append(rationale);
  const saved = state.drafts.get(c.case_id);
  if (saved && saved.packet === payload.packet_sha256) { name.value = saved.reviewer; verdict.value = saved.verdict; rationale.value = saved.rationale; }
  const saveInputs = () => state.drafts.set(c.case_id, {packet: payload.packet_sha256, reviewer: name.value, verdict: verdict.value, rationale: rationale.value});
  [name, verdict, rationale].forEach(input => input.addEventListener("input", saveInputs));
  const download = el("button", "Скачать черновик review", "primary"), message = el("p", "", "muted"); message.setAttribute("role", "status");
  download.addEventListener("click", () => {
    try {
      const draft = ReviewCore.makeDraft(payload, name.value, verdict.value, rationale.value);
      const url = URL.createObjectURL(new Blob([JSON.stringify(draft, null, 2) + "\n"], {type: "application/json"}));
      const a = el("a"); a.href = url; a.download = `review78-${c.target_ref}-${c.case_id.slice(-10)}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      message.textContent = "Черновик скачан. Решение не применено.";
    } catch (e) { message.textContent = e.message; }
  });
  note.append(grid, rationaleLabel, download, message); fragment.append(note);
  fragment.append(detail("Input bindings и case identity", json({case_id: c.case_id, semantic_identity: c.semantic_identity, graph_row_sha256: c.source_graph_row_digest, gold_row_digests: c.gold_row_digests, packet_sha256: payload.packet_sha256, build_manifest_sha256: payload.build_manifest_sha256})));
  $("main").replaceChildren(fragment);
}
async function selectCase(id) {
  const revision = guard.begin(); if (abort) abort.abort(); abort = new AbortController();
  state.selected = id; renderList(); $("main").replaceChildren(el("p", "Загрузка полного случая…", "empty"));
  try {
    const response = await fetch("/api/case?id=" + encodeURIComponent(id), {signal: abort.signal});
    if (!response.ok) throw new Error("Case недоступен или source digest изменился. Пересборка не выполняется автоматически.");
    const payload = await response.json();
    if (!guard.current(revision)) return;
    ReviewCore.validatePayload(payload, id, state.manifest);
    state.payload = payload; renderCase(payload);
    history.replaceState(null, "", "#" + encodeURIComponent(id));
  } catch (e) { if (e.name !== "AbortError" && guard.current(revision)) $("main").replaceChildren(el("p", e.message, "error")); }
}
function renderList() {
  const list = $("cases"); list.replaceChildren();
  state.filtered.slice(0, state.visible).forEach(c => {
    const button = el("button", undefined, "case" + (c.case_id === state.selected ? " active" : "")); button.type = "button";
    button.append(el("strong", c.target_ref), el("div", c.target_label, "label"), el("small", `${c.final_class} · ${c.structural.map(t => terms[t] || t).join(" / ")}`));
    button.addEventListener("click", () => selectCase(c.case_id)); list.append(button);
  });
  $("count").textContent = `${state.filtered.length} из ${state.cases.length} случаев · показано ${Math.min(state.visible, state.filtered.length)}`;
  $("more").hidden = state.visible >= state.filtered.length;
}
function filter() { state.filtered = ReviewCore.filterCases(state.cases, $("search").value, $("class").value, $("category").value); state.visible = 100; renderList(); }
$("search").addEventListener("input", filter); $("class").addEventListener("change", filter); $("category").addEventListener("change", filter);
$("more").addEventListener("click", () => { state.visible += 100; renderList(); });
(async () => {
  try {
    const response = await fetch("/api/index"); if (!response.ok) throw new Error("Index недоступен");
    const index = await response.json(); if (index.A_auto !== 0) throw new Error("A_auto guard нарушен");
    state.cases = index.cases; state.manifest = index.build_manifest_sha256; filter();
    const requested = decodeURIComponent(location.hash.slice(1));
    const first = state.cases.find(c => c.case_id === requested) || state.filtered[0];
    if (first) { if (requested) { $("class").value = ""; filter(); } await selectCase(first.case_id); }
  } catch (e) { $("main").replaceChildren(el("p", e.message, "error")); $("count").textContent = "Загрузка не завершена"; }
})();
