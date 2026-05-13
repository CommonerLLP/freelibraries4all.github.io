/* ============================================================
   main.js — render orchestration for both / and /data/.

   Each block is guarded by a presence check on its root element,
   so this single file runs cleanly on both pages — only the
   sections that exist will render.

   Loaded after data.js, helpers.js, games.js.
   ============================================================ */

// Substitute {{TOKEN}} placeholders in any node tagged `data-substitute`.
document.addEventListener("DOMContentLoaded", () => substituteConstants());

// ─── RENDER STATIC SECTIONS ───────────────────────────────────────
// Each section's render call is guarded — runs only on the page that
// has the corresponding root element.
$$("#standards").innerHTML = STANDARDS.map((s) => `
  <div class="standard">
    <div class="num">${s.n}</div>
    <div>
      <div class="short">${esc(s.short)}.</div>
      <div class="long">${esc(s.long)}</div>
    </div>
  </div>`).join("");

// Render guarded — section is currently parked (commented out in HTML).
const excludedEl = $("#excluded-grid");
if (excludedEl) excludedEl.innerHTML = EXCLUDED.map((e, i) => `
  <div class="excluded-card${i === 0 ? " first" : ""}">
    <div class="tag">Excluded — ${String(i+1).padStart(2, "0")}</div>
    <div class="name">${esc(e.label)}.</div>
    ${e.stats ? `<div class="stats">${esc(e.stats)}</div>` : ""}
  </div>`).join("");

// ─── INTERACTIVE TIMELINE ────────────────────────────────────────
// Horizontal scrubber + detail panel. Each event in HISTORY is a dot
// on a 1193 → 2026 line; clicking/keyboard-navigating/auto-playing
// updates the detail panel below. Era bands underneath the scrubber
// give a coarse colored sense of "where we are in 833 years."
(function renderInteractiveTimeline() {
  const root = $("#timeline");
  if (!root || typeof HISTORY === "undefined" || !HISTORY.length) return;

  // Parse the first 4-digit year out of each event's `year` string
  // ("1193" → 1193, "1947–49" → 1947). Used for scrubber positioning.
  const yearOf = (str) => parseInt(String(str).match(/\d{4}/)?.[0] || "0", 10);
  const events = HISTORY.map((e) => ({ ...e, _y: yearOf(e.year) }));
  const minY = Math.min(...events.map((e) => e._y));
  const maxY = Math.max(...events.map((e) => e._y));
  const span = Math.max(1, maxY - minY);

  // Era bands — anti-caste lineage framing. Timeline begins at Phule
  // (1848) so the first band names the lineage itself, not the
  // colonial state.
  //   reform:       1848–1946 (Phule, Periyar, Ranganathan, Travancore)
  //   republic:     1947–1990 (the Republic's broken promise — TN Act,
  //                 KSSP, DMK, Chattopadhyay, Haryana 1989)
  //   retreat:      1991–present (after liberalisation: NKC, NEP digital)
  const eras = [
    { key: "ref",  label: "Anti-caste reform",            start: minY, end: 1946 },
    { key: "ind",  label: "The Republic's broken promise", start: 1947, end: 1990 },
    { key: "rec",  label: "After liberalisation: the retreat", start: 1991, end: maxY },
  ];
  const eraOf = (y) => eras.find((e) => y >= e.start && y <= e.end)?.label || "";
  const pos = (y) => ((y - minY) / span) * 100;

  // Render shell
  root.classList.add("timeline-interactive");
  root.innerHTML = `
    <div class="tl-eras" aria-hidden="true">
      ${eras.map((e) => `
        <div class="tl-era tl-era-${e.key}"
             style="left:${pos(e.start)}%; right:${100 - pos(e.end)}%"></div>`).join("")}
    </div>
    <div class="tl-scrubber" role="group" aria-label="Timeline navigation">
      <div class="tl-line" aria-hidden="true"></div>
      ${events.map((e, i) => `
        <button type="button" class="tl-dot" data-idx="${i}"
                style="left:${pos(e._y)}%"
                aria-label="${esc(e.year)} — ${esc(e.title)}">
          <span class="tl-dot-year">${esc(e.year)}</span>
        </button>`).join("")}
    </div>
    <div class="tl-detail" aria-live="polite">
      <div class="tl-meta">
        <span class="tl-year"></span>
        <span class="tl-era-tag"></span>
      </div>
      <h3 class="tl-title"></h3>
      <p class="tl-body"></p>
    </div>
    <div class="tl-controls">
      <button type="button" class="tl-prev" aria-label="Previous event">← Prev</button>
      <span class="tl-progress" aria-live="polite"><span class="tl-cur">1</span> / ${events.length}</span>
      <button type="button" class="tl-play" aria-label="Auto-play timeline">▶ Play</button>
      <button type="button" class="tl-next" aria-label="Next event">Next →</button>
    </div>
  `;

  const detail = {
    year:  root.querySelector(".tl-year"),
    eraEl: root.querySelector(".tl-era-tag"),
    title: root.querySelector(".tl-title"),
    body:  root.querySelector(".tl-body"),
    cur:   root.querySelector(".tl-cur"),
  };
  const dots   = Array.from(root.querySelectorAll(".tl-dot"));
  const prevBtn = root.querySelector(".tl-prev");
  const nextBtn = root.querySelector(".tl-next");
  const playBtn = root.querySelector(".tl-play");

  let idx = 0;
  let playing = false;
  let timer = null;

  function show(i) {
    idx = (i + events.length) % events.length;
    const e = events[idx];
    detail.year.textContent  = e.year;
    detail.eraEl.textContent = eraOf(e._y);
    detail.title.textContent = e.title + ".";
    detail.body.textContent  = e.body;
    detail.cur.textContent   = String(idx + 1);
    dots.forEach((d, j) => {
      d.classList.toggle("active", j === idx);
      if (j === idx) d.setAttribute("aria-current", "true");
      else d.removeAttribute("aria-current");
    });
  }

  function setPlaying(on) {
    playing = on;
    playBtn.textContent = on ? "❚❚ Pause" : "▶ Play";
    playBtn.setAttribute("aria-pressed", on ? "true" : "false");
    if (timer) { clearInterval(timer); timer = null; }
    if (on) {
      timer = setInterval(() => {
        if (idx >= events.length - 1) { setPlaying(false); return; }
        show(idx + 1);
      }, 4500);
    }
  }

  // Click any dot → jump
  dots.forEach((d) => d.addEventListener("click", () => {
    setPlaying(false);
    show(parseInt(d.dataset.idx, 10));
  }));

  // Prev/Next + autoplay toggle
  prevBtn.addEventListener("click", () => { setPlaying(false); show(idx - 1); });
  nextBtn.addEventListener("click", () => { setPlaying(false); show(idx + 1); });
  playBtn.addEventListener("click", () => setPlaying(!playing));

  // Keyboard arrows (when timeline is focused via tab)
  root.addEventListener("keydown", (ev) => {
    if (ev.key === "ArrowLeft")  { ev.preventDefault(); setPlaying(false); show(idx - 1); }
    if (ev.key === "ArrowRight") { ev.preventDefault(); setPlaying(false); show(idx + 1); }
    if (ev.key === " ")           { ev.preventDefault(); setPlaying(!playing); }
  });

  // Touch swipe on the detail panel (mobile)
  const panel = root.querySelector(".tl-detail");
  let touchX = 0;
  panel.addEventListener("touchstart", (ev) => { touchX = ev.touches[0].clientX; }, { passive: true });
  panel.addEventListener("touchend",   (ev) => {
    const dx = ev.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) < 40) return;
    setPlaying(false);
    show(idx + (dx < 0 ? 1 : -1));
  });

  show(0);
})();

// English-only render — native scripts (Marathi/Tamil/Hindi/Bengali) parked in
// QUOTES const for the future bilingual version. For this release we surface
// only the English gloss + roman-script attribution. Speaker's name in their
// own script is preserved in QUOTES; this renderer just doesn't print it yet.
$$("#quote-grid").innerHTML = QUOTES.map((q) => {
  const text = q.en || q.text;
  const attr = q.attrEn || q.attr;
  return `
    <blockquote class="quote" lang="en">
      <div class="text">"${esc(text)}"</div>
      <div class="attr" lang="en">— ${esc(attr)}</div>
    </blockquote>`;
}).join("");

$$("#actions-grid").innerHTML = ACTIONS.map((a) => `
  <div class="action">
    <div class="action-head"><div class="action-num">${a.n}</div><div class="action-verb">${esc(a.verb)}</div></div>
    <div class="action-title">${esc(a.title)}</div>
    <p class="action-text">${esc(a.body)}</p>
  </div>`).join("");

// Parliament library corpus. Generated by
// scripts/build_parliament_libraries.py into assets/parliament_libraries.js,
// joining the upstream sansad-semantic-crawler manifest with the v1.0.0
// discourse-analysis outputs.
(function renderParliamentLibraries() {
  const data = window.PARLIAMENT_LIBRARY_DATA || {};
  if (!$("#parl-headline-stat")) return;

  const ds = data.discourseSummary || {};
  const ministries = data.ministryDiscourse || [];
  const excerpts = data.discourseExcerpts || [];
  const rrrlf = data.rrrlfDeflections || [];

  // ── Headline stat ─────────────────────────────────────────────────
  const headlineEl = $("#parl-headline-stat");
  if (headlineEl && ds.responsesClassified) {
    const pct = ds.evasionRateClassified != null
      ? Math.round(ds.evasionRateClassified * 100) + "%"
      : "—";
    headlineEl.innerHTML = `
      <div class="parl-headline-num">${esc(pct)}</div>
      <div class="parl-headline-body">
        <div class="parl-headline-lede"><strong>${esc(ds.evasiveCount)} of ${esc(ds.responsesClassified)}</strong> classified responses to library questions in Parliament were evasive.</div>
      </div>`;
  }

  // ── RRRLF "State subject" cascade ─────────────────────────────────
  const cascadeEl = $("#parl-rrrlf-cascade");
  if (cascadeEl) {
    cascadeEl.innerHTML = rrrlf.length
      ? rrrlf.map((r) => {
          const asker = (r.askers || []).filter(Boolean).slice(0, 2).join(", ");
          return `
            <article class="parl-cascade-card">
              <div class="parl-cascade-date">${esc(r.date || "undated")}</div>
              <div class="parl-cascade-body">
                <div class="parl-cascade-quote">&ldquo;${esc(r.matchedPattern)}&rdquo;</div>
                <div class="parl-cascade-meta">
                  ${r.uri ? `<a href="${esc(r.uri)}" target="_blank" rel="noopener">` : ""}${esc(r.house)} ${esc(r.qtype)} Q${esc(r.qno)} — ${esc(r.title)}${r.uri ? `</a>` : ""}
                </div>
                <div class="parl-cascade-min">${esc(r.ministry)} · response to ${esc(asker || "MP")}</div>
              </div>
            </article>`;
        }).join("")
      : `<div class="parl-empty">No RRRLF-tagged FEDERAL_DEFLECTION responses in the current corpus.</div>`;
  }

  // ── Per-ministry evasion bars ────────────────────────────────────
  const minRowsEl = $("#parl-ministry-rows");
  if (minRowsEl) {
    const shown = ministries.filter((m) => (m.recordsClassified || 0) > 0);
    minRowsEl.innerHTML = shown.length
      ? shown.map((m) => {
          const rate = m.evasionRateClassified != null
            ? Math.round(m.evasionRateClassified * 100)
            : 0;
          const ratePct = `${rate}%`;
          return `
            <div class="parl-ministry-row">
              <div class="parl-ministry-name">${esc(m.ministry)}</div>
              <div class="parl-ministry-bar-wrap">
                <div class="parl-ministry-bar" style="width:${rate}%"></div>
                <div class="parl-ministry-rate">${ratePct}</div>
              </div>
              <div class="parl-ministry-n">N = ${esc(m.recordsClassified)} classified <span class="t-cream-soft">of ${esc(m.recordsTotal)} total</span></div>
            </div>`;
        }).join("")
      : "";
  }

  // ── Verbatim evasion cards (one per label) ───────────────────────
  const gridEl = $("#parl-evasion-grid");
  if (gridEl) {
    const seen = new Set();
    const oneEach = [];
    for (const e of excerpts) {
      if (seen.has(e.label)) continue;
      seen.add(e.label);
      oneEach.push(e);
    }
    gridEl.innerHTML = oneEach.map((e) => {
      const pattern = (e.matchedPattern || "").trim() || e.excerpt;
      const citation = `${esc(e.ministry)} · ${esc(e.date)} · ${esc(e.house)} ${esc(e.qtype)} Q${esc(e.qno)} — ${esc(e.title)}`;
      const cite = e.uri
        ? `<a href="${esc(e.uri)}" target="_blank" rel="noopener">${citation}</a>`
        : citation;
      return `
        <article class="parl-evasion-row">
          <div class="parl-evasion-tag">${esc(e.label.replace(/_/g, " "))}</div>
          <div class="parl-evasion-body">
            <div class="parl-evasion-pattern">&ldquo;${esc(pattern)}&rdquo;</div>
            <div class="parl-evasion-cite">${cite}</div>
            <details class="parl-evasion-more">
              <summary>Read the passage</summary>
              <blockquote>${esc(e.excerpt)}</blockquote>
              ${e.politicalFunction ? `<div class="parl-evasion-function">Classifier note: ${esc(e.politicalFunction)}</div>` : ""}
            </details>
          </div>
        </article>`;
    }).join("");
  }

  // ── Collapsible: corpus stats + top tags (kept for completeness) ─
  const stats = data.summaryStats || [];
  const tags = data.topTags || [];
  const grid = $("#parl-grid");
  if (grid) {
    grid.innerHTML = stats.map((p) => `
      <div class="parl-stat">
        <div class="label">${esc(p.label)}</div>
        <div class="value">${esc(p.value)}</div>
        <div class="sub">${esc(p.sub)}</div>
      </div>`).join("");
  }
  const tagEl = $("#parl-tags");
  if (tagEl) {
    tagEl.innerHTML = tags.length
      ? tags.map((t) => `<span class="parl-chip">${esc(t.label)} <strong>${esc(t.count)}</strong></span>`).join("")
      : `<span class="parl-chip">No topic tags yet</span>`;
  }

  // ── Method note ──────────────────────────────────────────────────
  const sourceEl = $("#parl-source-note");
  if (sourceEl) {
    const generated = data.generatedAt ? `Generated ${data.generatedAt}. ` : "";
    sourceEl.innerHTML = `${esc(generated)}Corpus: ${esc(ds.questionsTotal || 0)} library questions, ${esc(ds.responsesExtracted || 0)} parseable responses, ${esc(ds.responsesClassified || 0)} classified by sansad-semantic-crawler regex_v2 + LLM ensemble. Sources: Lok Sabha <a href="https://elibrary.sansad.in/" target="_blank" rel="noopener">elibrary.sansad.in</a>; Rajya Sabha <a href="https://rsdoc.nic.in/" target="_blank" rel="noopener">rsdoc.nic.in</a>. Classifier: <a href="https://github.com/CommonerLLP/sansad-semantic-crawler" target="_blank" rel="noopener">CommonerLLP/sansad-semantic-crawler</a> v1.0.0.`;
  }
})();


// ─── WORLD COMPARISON ─────────────────────────────────────────────
(function renderWorld() {
  const max = Math.max(...WORLD.map((w) => w.value));
  $$("#world-rows").innerHTML = WORLD.map((w) => {
    const pct = Math.max(0.3, (w.value / max) * 100);
    return `
      <div class="world-row${w.india ? " india" : ""}">
        <div class="world-name">${esc(w.name)}</div>
        <div class="world-bar-wrap"><div class="world-bar" style="width:${pct.toFixed(2)}%"></div></div>
        <div class="world-amount">₹${fmtIN(Math.round(w.value))}</div>
      </div>`;
  }).join("");
})();


// ─── STATE SCANDAL PICKER (pamphlet only) ─────────────────────────
// Replaces the old 31-row state-list + filters. Same data, but
// now revealed one-state-at-a-time so the user gets a punchline.
const NATIONAL_AVG = 15.30; // ₹/person/year — per-capita library spend (state avg)
const BOOK_PRICE   = 250;   // ₹ — typical Indian-published paperback
function rankStates() {
  return Object.keys(STATE_DATA)
    .map((name) => ({ name, val: STATE_DATA[name][6] || 0 }))
    .sort((a, b) => b.val - a.val); // highest first
}
function scandalFor(name) {
  const ranked = rankStates();
  const idx = ranked.findIndex((r) => r.name === name);
  const rank = idx + 1;
  const total = ranked.length;
  const spend = STATE_DATA[name]?.[6] || 0;

  const leg = LEGISLATION[name] || {};
  const actLine = leg.has_act
    ? (leg.free ? `${leg.year} Library Act — defines libraries as <strong>free</strong>` : `${leg.year} Library Act — but it permits user fees`)
    : `<strong style="color:var(--red)">No Library Act on the books</strong>`;

  const ruralCov = RURAL_COVERAGE[name];
  const ruralLine = ruralCov !== undefined ? `<strong>${ruralCov}%</strong> of Gram Panchayats have a functional library (PAI 2.0)` : `Rural coverage data unavailable for this jurisdiction`;

  const releasedL = RRRLF_RELEASED[name] || 0;
  const rrrlLine = releasedL > 0 ? `₹${fmtIN(releasedL)}L received from the Centre's library foundation` : `<strong style="color:var(--red)">₹0 received from the Centre's library foundation</strong>`;

  // vs national avg
  let vsLine;
  if (spend > NATIONAL_AVG) {
    const pct = Math.round((spend / NATIONAL_AVG - 1) * 100);
    vsLine = `<strong style="color:var(--red)">${pct}% above</strong> the national average (₹${fmtMoney(NATIONAL_AVG)})`;
  } else {
    const pct = Math.round((1 - spend / NATIONAL_AVG) * 100);
    const diff = (NATIONAL_AVG - spend).toFixed(2);
    vsLine = `<strong style="color:var(--red)">${pct}% below</strong> the national average (−₹${diff})`;
  }

  // Rank line
  let rankLine;
  if (rank <= 5) rankLine = `<strong>${rank} / ${total}</strong> — <strong style="color:var(--red)">top five</strong>`;
  else if (rank > total - 5) rankLine = `<strong>${rank} / ${total}</strong> — <strong style="color:var(--red)">bottom five</strong>`;
  else rankLine = `<strong>${rank} / ${total}</strong> — middle of the pack`;

  // Punchline
  let punchline;
  if (spend <= 0) {
    punchline = `Your state's per-capita library spend rounds to <strong>zero</strong>. There is, in effect, no public library budget. The bookstore is closer than the library.`;
  } else {
    const yearsForBook = Math.round(BOOK_PRICE / spend);
    const peopleForBook = Math.round(BOOK_PRICE / spend);
    if (yearsForBook >= 100) {
      punchline = `Your state spends about <strong>₹${fmtMoney(spend)}</strong> per person per year on libraries. At that rate it would take a resident <strong>${fmtIN(yearsForBook)} years</strong> of their state's library budget to buy <strong>one ₹${BOOK_PRICE} book</strong>.`;
    } else if (yearsForBook >= 10) {
      punchline = `Your state spends about <strong>₹${fmtMoney(spend)}</strong> per person per year. That is <strong>${yearsForBook} years</strong> of one resident's library share for <strong>one ₹${BOOK_PRICE} book</strong>.`;
    } else if (yearsForBook >= 2) {
      punchline = `Your state spends about <strong>₹${fmtMoney(spend)}</strong> per person per year — <strong>${yearsForBook} years</strong> per resident to buy <strong>one ₹${BOOK_PRICE} book</strong>. Even the best Indian state cannot stock a single shelf.`;
    } else {
      punchline = `Your state spends about <strong>₹${fmtMoney(spend)}</strong> per person per year — about <strong>one ₹${BOOK_PRICE} book per resident every ${yearsForBook} year${yearsForBook === 1 ? "" : "s"}</strong>. Even this — the best in the country — falls far short of any global standard.`;
    }
  }

  return {
    name, spend, rank, total,
    rows: [
      { dim: "Per-capita spending",      detail: `₹${fmtMoney(spend)} per person per year (2020-21).`,  value: `₹${fmtMoney(spend)}` },
      { dim: "Rural Coverage (GP)",      detail: ruralLine, value: ruralCov !== undefined ? `${ruralCov}%` : "—" },
      { dim: "vs national average",       detail: vsLine,  value: spend >= NATIONAL_AVG ? "↑" : "↓" },
      { dim: "Library Act",                detail: actLine, value: leg.has_act ? (leg.free ? "Free" : "Fees") : "None" },
      { dim: "RRRLF 2021-24",              detail: rrrlLine, value: releasedL > 0 ? `₹${fmtIN(releasedL)}L` : "₹0" },
      { dim: "Rank (out of 31)",           detail: rankLine, value: `${rank}/${total}` }
    ],

    punchline
  };
}

// Render the scandal panel for a given state. Used by:
// (a) the standalone scandal-picker (homepage version, now retired)
// (b) the data-page state-picker which drives BOTH grade + scandal panels.
function renderScandalPanel(name) {
  const result = document.getElementById("scandal-result");
  if (!result) return;
  if (!name) { result.hidden = true; return; }
  const s = scandalFor(name);
  document.getElementById("scandal-state").textContent = s.name;
  document.getElementById("scandal-stat").textContent = `₹${fmtMoney(s.spend)}`;
  document.getElementById("scandal-rows").innerHTML = s.rows.map((r) => `
    <div class="scandal-row">
      <div>
        <div class="scandal-dim">${esc(r.dim)}</div>
        <div class="scandal-detail">${r.detail}</div>
      </div>
      <div class="scandal-value">${r.value}</div>
    </div>`).join("");
  document.getElementById("scandal-punchline").innerHTML =
    `<span class="label">THE SCANDAL</span>${s.punchline}`;
  result.hidden = false;
}

(function initScandalPicker() {
  // Standalone scandal picker (homepage) — kept for backward compatibility
  // if reintroduced; safely no-ops when the dropdown isn't present.
  const select = document.getElementById("scandal-picker");
  if (!select) return;
  Object.keys(STATE_DATA).sort().forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name; opt.textContent = name;
    select.appendChild(opt);
  });
  select.addEventListener("change", (e) => renderScandalPanel(e.target.value));
})();


// ─── RRRLF ANNUAL CHART ───────────────────────────────────────────
// India population (millions, mid-year), 2003–2023, World Bank.
const INDIA_POP_MN = {
  2003: 1094, 2004: 1110, 2005: 1127, 2006: 1143, 2007: 1160, 2008: 1176,
  2009: 1192, 2010: 1207, 2011: 1221, 2012: 1235, 2013: 1250, 2014: 1265,
  2015: 1280, 2016: 1296, 2017: 1311, 2018: 1327, 2019: 1342, 2020: 1355,
  2021: 1367, 2022: 1378, 2023: 1404
};

(function renderRrrlf() {
  const rrrlfEl = $("#rrrlf-chart");
  if (!rrrlfEl) return;

  // Compute per-capita ₹/year for each year that has RRRLF data.
  // RRRLF disbursement is in lakhs (₹L). 1 L = 100,000 ₹.
  const points = [];
  for (let y = 2003; y <= 2023; y++) {
    const v = RRRLF_DATA[y];
    const pop = INDIA_POP_MN[y];
    if (!v || !pop) continue;
    const perCapita = (v * 100000) / (pop * 1_000_000); // ₹/person/year
    points.push({ y, perCapita, raw: v });
  }

  const W = 1000, H = 360;
  const padL = 64, padR = 32, padT = 28, padB = 56;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;

  const xMin = 2003, xMax = 2023;
  const yMax = Math.max(...points.map((p) => p.perCapita)) * 1.1;
  const x = (yr) => padL + ((yr - xMin) / (xMax - xMin)) * innerW;
  const y = (val) => padT + (1 - (val / yMax)) * innerH;

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.y).toFixed(2)} ${y(p.perCapita).toFixed(2)}`).join(" ");

  // 5-year rolling avg trend line
  const avg = [];
  for (let i = 0; i < points.length; i++) {
    const window = points.slice(Math.max(0, i - 2), Math.min(points.length, i + 3));
    const m = window.reduce((s, p) => s + p.perCapita, 0) / window.length;
    avg.push({ y: points[i].y, perCapita: m });
  }
  const avgPath = avg.map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.y).toFixed(2)} ${y(p.perCapita).toFixed(2)}`).join(" ");

  // X-axis tick years (every 4 years + endpoints)
  const xTicks = [2003, 2007, 2011, 2015, 2019, 2023];
  // Y-axis tick values
  const yTicks = [0, 0.05, 0.10, 0.15, 0.20, 0.25].filter((v) => v <= yMax);

  // Find peak + most-recent for callouts
  const peak = points.reduce((a, b) => (b.perCapita > a.perCapita ? b : a));
  const last = points[points.length - 1];

  rrrlfEl.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" class="rrrlf-svg" xmlns="http://www.w3.org/2000/svg" role="img"
         aria-label="Per-capita RRRLF disbursement ₹/year, 2003–2023. Line trends downward despite spikes.">
      <!-- y-axis grid + labels -->
      ${yTicks.map((v) => `
        <line x1="${padL}" y1="${y(v)}" x2="${W - padR}" y2="${y(v)}" stroke="var(--cream-deep)" stroke-opacity="0.18" stroke-width="1"/>
        <text x="${padL - 12}" y="${y(v) + 5}" fill="var(--cream-deep)" font-family="var(--f-mono)" font-size="13" font-weight="700" letter-spacing="1.2" text-anchor="end">₹${v.toFixed(2)}</text>
      `).join("")}

      <!-- x-axis ticks -->
      ${xTicks.map((yr) => `
        <text x="${x(yr)}" y="${H - padB + 26}" fill="var(--cream-deep)" font-family="var(--f-mono)" font-size="13" font-weight="700" letter-spacing="1.2" text-anchor="middle">${yr}</text>
      `).join("")}

      <!-- 5-year rolling-avg trend line (red, dashed) -->
      <path d="${avgPath}" fill="none" stroke="var(--red)" stroke-width="3" stroke-dasharray="6 4" stroke-opacity="0.7"/>

      <!-- raw line (cream) -->
      <path d="${path}" fill="none" stroke="var(--cream)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>

      <!-- data points -->
      ${points.map((p) => `
        <circle cx="${x(p.y)}" cy="${y(p.perCapita)}" r="${p === peak || p === last ? 7 : 4}"
                fill="${p === peak || p === last ? "var(--red)" : "var(--cream)"}"
                stroke="var(--ink)" stroke-width="2"/>
      `).join("")}

      <!-- peak callout -->
      <text x="${x(peak.y)}" y="${y(peak.perCapita) - 16}" fill="var(--red)"
            font-family="var(--f-display)" font-size="18" font-weight="900" letter-spacing="-0.3" text-anchor="middle">
        Peak ${peak.y} · ₹${peak.perCapita.toFixed(2)}
      </text>

      <!-- 2023 callout -->
      <text x="${x(last.y) - 6}" y="${y(last.perCapita) + 22}" fill="var(--red)"
            font-family="var(--f-display)" font-size="18" font-weight="900" letter-spacing="-0.3" text-anchor="end">
        ${last.y} · ₹${last.perCapita.toFixed(2)}
      </text>
    </svg>
    <div class="rrrlf-legend">
      <span class="legend-item"><span class="dot solid"></span> Per capita, ₹/year (nominal)</span>
      <span class="legend-item"><span class="dot dash"></span> 5-year rolling average</span>
    </div>
  `;
})();


// ─── REPORT CARD (interactive picker — /data/) ────────────────────
function gradeState(name) {
  const spend = STATE_DATA[name]?.[6] || 0;
  // Per-capita spending — most-recent year (~2020-21). 50 pts max.
  let spendScore;
  let spendBand;
  if      (spend >= 100) { spendScore = 50; spendBand = "best in country"; }
  else if (spend >= 50)  { spendScore = 40; spendBand = "well above average"; }
  else if (spend >= 20)  { spendScore = 30; spendBand = "above average"; }
  else if (spend >= 15)  { spendScore = 22; spendBand = "near national average"; }
  else if (spend >= 10)  { spendScore = 16; spendBand = "below national average"; }
  else if (spend >= 5)   { spendScore = 10; spendBand = "low"; }
  else if (spend >= 1)   { spendScore = 5;  spendBand = "very low"; }
  else                   { spendScore = 0;  spendBand = "essentially nothing"; }

  const leg = LEGISLATION[name] || {};
  const actScore = leg.has_act ? 20 : 0;
  const freeBonus = leg.free ? 5 : 0;
  let actDetail;
  if (leg.has_act && leg.free) actDetail = `${leg.year} Library Act — defines libraries as <strong>free</strong>.`;
  else if (leg.has_act)         actDetail = `${leg.year} Library Act — but it permits user fees.`;
  else                          actDetail = `No Library Act on the books.`;

  const releasedL = RRRLF_RELEASED[name] || 0;
  let rrrlScore, rrrlDetail;
  if      (releasedL >= 100) { rrrlScore = 20; rrrlDetail = `₹${fmtIN(releasedL)}L received from RRRLF (2021-24) — strong utilisation.`; }
  else if (releasedL >= 50)  { rrrlScore = 15; rrrlDetail = `₹${fmtIN(releasedL)}L received — moderate utilisation.`; }
  else if (releasedL >= 10)  { rrrlScore = 10; rrrlDetail = `₹${fmtIN(releasedL)}L received — low utilisation.`; }
  else if (releasedL > 0)    { rrrlScore = 5;  rrrlDetail = `₹${fmtIN(releasedL)}L received — token amount.`; }
  else                       { rrrlScore = 0;  rrrlDetail = `₹0 received from RRRLF in 2021-24.`; }

  const inNML = NML_STATES.has(name);
  const nmlScore = inNML ? 10 : 0;
  const nmlDetail = inNML
    ? "Participates in the National Mission on Libraries (one of 27)."
    : "Not part of the National Mission on Libraries.";

  const total = spendScore + actScore + freeBonus + rrrlScore + nmlScore;
  const grade = total >= 85 ? "A" : total >= 70 ? "B" : total >= 55 ? "C" : total >= 40 ? "D" : "F";

  return {
    name, total, grade,
    rows: [
      { dim: "Per-capita spending",   detail: `₹${fmtMoney(spend)}/person/year — ${spendBand}.`, score: spendScore, max: 50 },
      { dim: "Library Act",            detail: actDetail + (freeBonus ? ` <strong style="color:var(--red);">+5 free bonus</strong>` : ""), score: actScore + freeBonus, max: 20 },
      { dim: "RRRLF utilisation",      detail: rrrlDetail, score: rrrlScore, max: 20 },
      { dim: "NML participation",      detail: nmlDetail, score: nmlScore, max: 10 }
    ]
  };
}

const GRADE_MEANING = {
  A: "Top of the class — but the class itself is failing. Even the best states fall well short of the IFLA per-capita norm.",
  B: "Above average for India, but India's average is among the lowest in the world. Real public-library access is still limited.",
  C: "Mediocre. The state is doing the bare minimum — or has the structure but not the funding.",
  D: "Failing. The state has either no Library Act or no real spending. Both, often.",
  F: "The state has effectively no public library system. Citizens here have neither the law, the funds, nor the institutional commitment."
};

(function initReportPicker() {
  const select = document.getElementById("state-picker");
  const result = document.getElementById("report-result");
  if (!select || !result) return;

  const states = Object.keys(STATE_DATA).sort();
  states.forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name; opt.textContent = name;
    select.appendChild(opt);
  });

  function showResult(name) {
    if (!name) { result.hidden = true; return; }
    const g = gradeState(name);
    document.getElementById("result-state").textContent = g.name;
    const gradeEl = document.getElementById("result-grade");
    gradeEl.textContent = g.grade;
    gradeEl.classList.toggle("fail", g.grade === "D" || g.grade === "F");
    document.getElementById("result-rows").innerHTML = g.rows.map((r) => `
      <div class="result-row">
        <div>
          <div class="result-dim">${esc(r.dim)}</div>
          <div class="result-detail">${r.detail}</div>
        </div>
        <div class="result-score">${r.score}</div>
        <div class="result-out-of">/ ${r.max}</div>
      </div>`).join("");
    document.getElementById("result-total").innerHTML =
      `<span>Total</span><span><span class="num">${g.total}</span> / 100 &nbsp;→&nbsp; Grade <span class="num">${g.grade}</span></span>`;
    document.getElementById("result-meaning").innerHTML =
      `<strong>What this means:</strong> ${GRADE_MEANING[g.grade]}`;
    result.hidden = false;
  }

  select.addEventListener("change", (e) => {
    const name = e.target.value;
    showResult(name);
    // Also render the scandal panel below if it's present on this page.
    renderScandalPanel(name);
  });
})();


// ─── TAX ALLOCATION CALCULATOR ────────────────────────────────────
// Income → estimated income tax → Centre's allocation of that tax
// across libraries (RRRLF), advertising, and PM foreign trips.
//
// Tax brackets: New Tax Regime, FY 2024-25 (no rebate, simplified for advocacy).
// Centre line items use FY24-25 actuals where available; libraries uses recent
// RRRLF average. Total Union Budget = FY 2024-25 BE.
const NEW_TAX_BRACKETS = [
  [300000,  700000,  0.05],
  [700000,  1000000, 0.10],
  [1000000, 1200000, 0.15],
  [1200000, 1500000, 0.20],
  [1500000, Infinity, 0.30]
];
// Income tax under New Tax Regime FY 2024-25, with ₹75,000 standard deduction
// for salaried individuals and 4% Health & Education cess on tax payable.
// Section 87A rebate (zero tax up to ₹7L taxable) applied for salaried filers.
const STANDARD_DEDUCTION = 75000;
const REBATE_TAXABLE_CAP = 700000; // 87A rebate makes tax zero up to ₹7L taxable
const CESS_RATE = 0.04;
function estimatedIncomeTax(salary) {
  const taxable = Math.max(0, salary - STANDARD_DEDUCTION);
  if (taxable <= REBATE_TAXABLE_CAP) return 0;
  let tax = 0;
  for (const [lo, hi, rate] of NEW_TAX_BRACKETS) {
    if (taxable <= lo) break;
    tax += (Math.min(taxable, hi) - lo) * rate;
  }
  return tax * (1 + CESS_RATE);
}
const CENTRE_BUDGET    = 4800000; // ₹ crore — Union Budget 2024-25 BE
const CENTRE_LIBRARIES = 195;     // ₹ crore — Centre's full library spend (CAG 2205-105 avg 2014-21)
const CENTRE_ADS       = 644;     // ₹ crore — Govt advertising FY 2024-25 actual
const CORP_TAX_CUT     = 145000;  // ₹ crore — revenue forgone from 2019 corporate tax cut, FY 2019-20

const incomeInput = $("#income-input"), incomeRange = $("#income-range");
const tTax = $("#t-tax"), tLib = $("#t-lib"), tAds = $("#t-ads"), tCorp = $("#t-corp");
const tAdsMult = $("#t-ads-mult"), tCorpMult = $("#t-corp-mult");
const TAX_CALC_PRESENT = !!incomeInput;

function shareFromTax(tax, lineItemCrore) {
  return tax * (lineItemCrore / CENTRE_BUDGET);
}
function recomputeTax(value, source) {
  const salary = Math.max(0, Math.round(+value || 0));
  if (source !== "input") incomeInput.value = salary;
  if (source !== "range") incomeRange.value = Math.min(Math.max(salary, +incomeRange.min), +incomeRange.max);
  const tax  = Math.round(estimatedIncomeTax(salary));
  const lib  = shareFromTax(tax, CENTRE_LIBRARIES);
  const ads  = shareFromTax(tax, CENTRE_ADS);
  const corp = shareFromTax(tax, CORP_TAX_CUT);
  tTax.textContent  = fmtIN(tax);
  tLib.textContent  = lib.toFixed(2);
  tAds.textContent  = ads.toFixed(2);
  tCorp.textContent = fmtIN(Math.round(corp));
  // Multipliers (relative to libraries, the anchor)
  const adsX  = lib > 0 ? Math.round(ads  / lib) : 0;
  const corpX = lib > 0 ? Math.round(corp / lib) : 0;
  tAdsMult.textContent  = adsX  > 0 ? `${adsX}×`  : "—";
  tCorpMult.textContent = corpX > 0 ? `${fmtIN(corpX)}×` : "—";
}
if (TAX_CALC_PRESENT) {
  incomeInput.addEventListener("input", (e) => recomputeTax(e.target.value, "input"));
  incomeRange.addEventListener("input", (e) => recomputeTax(e.target.value, "range"));
  recomputeTax(incomeInput.value, null);
}


// ─── MP LETTER (state-aware) ──────────────────────────────────────
const stateSel = $("#mp-state");
const MP_LETTER_PRESENT = !!stateSel;
if (MP_LETTER_PRESENT) Object.keys(STATE_DATA).sort().forEach((name) => {
  const opt = document.createElement("option");
  opt.value = name; opt.textContent = name;
  stateSel.appendChild(opt);
});
const nameInput = $("#mp-name");
const constInput = $("#mp-constituency");
const letterPre = $("#letter-pre");
const mailtoLink = $("#cta-mailto");
const copyBtn = $("#cta-copy");
function buildLetter() {
  const name = nameInput.value || "[Your name]";
  const state = stateSel.value;
  const constituency = constInput.value || "[Your constituency]";
  const stateContact = state ? JURISDICTION_CONTACTS[state] : null;
  const centreContact = JURISDICTION_CONTACTS._centre;
  const cmTitle = stateContact ? stateContact.title : "Hon'ble Chief Minister, Government of [Your State]";
  const stateLabel = state || "[your state]";

  let stateLine = "";
  if (state) {
    const spend = STATE_DATA[state]?.[6];
    const leg = LEGISLATION[state] || {};
    const ratio = spend ? (15.30 / spend).toFixed(1) : null;
    if (spend !== undefined && spend !== null) {
      if (spend < 1)         stateLine = `${state} spends just ₹${fmtMoney(spend)} per person per year on public libraries — among the lowest in India, ${ratio}× below the state-level national average of ₹15.30.`;
      else if (spend < 15.3) stateLine = `${state} spends ₹${fmtMoney(spend)} per person per year on public libraries — below the state-level national average of ₹15.30.`;
      else                   stateLine = `${state} spends ₹${fmtMoney(spend)} per person per year on public libraries — above the national average, but still a fraction of what comparable democracies spend.`;
    }
    if (leg.free) {
      stateLine += ` ${state}'s Public Library Act (${leg.year}) is one of the only state laws in India that defines public libraries as free of fees — a national model. The challenge now is funding and implementation.`;
    } else if (leg.has_act) {
      stateLine += ` ${state} has had a Public Library Act since ${leg.year}, but like 14 of India's 15 state library acts, it permits subscription fees, contradicting Ranganathan's First Law of Library Science. Only Haryana's 2021 Act defines libraries as free of fees.`;
    } else {
      stateLine += ` ${state} does not yet have a Public Library Act — leaving libraries without statutory funding mandate or any guaranteed right of access.`;
    }
  }

  return `To: ${cmTitle}
cc: ${centreContact.title}

Subject: Public Library Funding in ${stateLabel} — A Constitutional Failure

I write to both of you because public libraries in India are a failure of the State and of the Centre.

Libraries are listed in List II of the Seventh Schedule of the Constitution — a State subject. The responsibility to legislate, fund, and operate them is constitutionally the State's. The Centre has used "state subject" as cover to abdicate, but India is a centralized polity in practice, and the Prime Minister's office sets the political agenda. Both of you chose this.

THE FACTS

State governments together spend ₹15.30 per person per year on public libraries — less than a packet of biscuits. The Centre's RRRLF works out to ₹0.07 per person per year. The United States spends ₹2,900 per person. Australia ₹2,400. Of 36 states and union territories, only 19 have library legislation. Only one — Haryana — defines a public library as actually free of fees.
${stateLine ? "\n" + stateLine + "\n" : ""}
This is not a budget problem. It is a political choice. It locks Dalit, Bahujan, Adivasi, working-class, women, disabled and minority readers out of the institutions our Constitution promises them under Articles 14, 21 and 21A.

TO THE HON'BLE CHIEF MINISTER

  1. Enact (or strengthen) ${stateLabel}'s Public Library Act to define public libraries as free of fees, on the Haryana model.
  2. Allocate per-capita library funding tied to minimum standards. Audit it.
  3. Engage local self-government (Panchayats, Municipalities) in library governance and outreach to Dalit, Bahujan, Adivasi communities.

TO THE HON'BLE PRIME MINISTER

  1. Stop using "state subject" as cover for inaction.
  2. Adopt the People's National Library Policy 2024 (PNLP24) drafted by the Free Libraries Network — endorsed by IFLA, Internet Freedom Foundation, HarperCollins India, the Dalit Bahujan Resource Centre, and the National Campaign on Dalit Human Rights.
  3. Mandate a national survey of every public library in India — even the Raja Rammohun Roy Library Foundation cannot say how many exist.

The library is not a favour. It is a right.

Yours,
${name}
${constituency}, ${stateLabel}`;
}

function syncLetter() {
  const letter = buildLetter();
  letterPre.textContent = letter;
  const state = stateSel.value;
  const cmEmail = state ? (JURISDICTION_CONTACTS[state]?.email || "") : "";
  // PMO has no public direct email; cc field is intentionally blank.
  // The howto strip directs users to the official PM contact form & CPGRAMS portal.
  const subject = state
    ? `Public Library Funding in ${state} — A Constitutional Failure`
    : "Public Library Funding in India — A Constitutional Failure";
  mailtoLink.href = "mailto:" + encodeURIComponent(cmEmail) +
    "?subject=" + encodeURIComponent(subject) +
    "&body=" + encodeURIComponent(letter);
}
if (MP_LETTER_PRESENT) {
  nameInput.addEventListener("input", syncLetter);
  stateSel.addEventListener("change", syncLetter);
  constInput.addEventListener("input", syncLetter);
  syncLetter();
}

if (MP_LETTER_PRESENT) copyBtn.addEventListener("click", () => {
  const letter = buildLetter();
  const done = () => {
    const orig = copyBtn.textContent;
    copyBtn.textContent = "Copied ✓";
    setTimeout(() => { copyBtn.textContent = orig; }, 2000);
  };
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(letter).then(done).catch(() => {
      const r = document.createRange();
      r.selectNode(letterPre);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(r);
      done();
    });
  } else {
    const r = document.createRange();
    r.selectNode(letterPre);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(r);
    done();
  }
});

// ─── ACTBAR ARMING ──────────────────────────────────────────────
// Quiet "Read on →" by default; flips to loud red "ACT! Write to your
// CM and the PM" once the reader engages with the tax calculator OR
// scrolls past the calc section. State persists for the session via
// localStorage so the bar stays armed on subsequent loads.
(function armActbar() {
  if (!document.querySelector(".actbar")) return;

  const STORAGE_KEY = "r2r-actbar-armed";
  let armed = false;

  const arm = () => {
    if (armed) return;
    armed = true;
    document.body.classList.add("actbar-armed");
    try { localStorage.setItem(STORAGE_KEY, "1"); } catch (_) {}
  };

  // Restore armed state across visits
  try {
    if (localStorage.getItem(STORAGE_KEY) === "1") {
      arm();
      return;
    }
  } catch (_) {}

  // Trigger 1: any interaction with the salary slider/input
  ["income-range", "income-input"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", arm, { once: true });
  });

  // Trigger 2: scrolled past the calculator (calc bottom above viewport top)
  const calc = document.querySelector(".calc");
  if (calc && "IntersectionObserver" in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.boundingClientRect.bottom < 0) {
          arm();
          obs.disconnect();
        }
      });
    }, { threshold: 0 });
    obs.observe(calc);
  }
})();
