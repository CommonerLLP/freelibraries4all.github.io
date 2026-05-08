# AGENTS.md — Operating rules for this project

This file is auto-read by Codex at every session start. **Aakash:
if you ever doubt that an agent is following these rules, `cat AGENTS.md`
and check.** If a rule is not in this file, it does not exist as a
persistent rule — it lives only in one session's running context and
will be lost at the next compaction.

Last updated: 2026-05-06 (org correction: CommonerLLP)

---

## 1 · DEPLOY — single remote, no exceptions

- **Production repo:** `CommonerLLP/freelibraries4all.github.io`
  (the only place that serves theright2read.org)
- **Push target:** `git push origin HEAD:main` only.
- **Do NOT push to `skishchampi/freelibraries4all`.** That repo is for
  the dashboard / earlier prototype and must not receive pamphlet
  pushes.
- The local working remote is `origin` →
  `https://github.com/CommonerLLP/freelibraries4all.github.io.git`.
  If `git remote -v` shows anything else as a push target, **stop and
  ask the user before pushing.**

## 2 · COMMIT / PUSH — explicit permission only

- **Never `git commit` without explicit user permission in this turn.**
  "Continue from where you left off" is NOT permission to commit.
- **Never `git push` without explicit user permission in this turn.**
- The user uses the word "ship" or "push" or "commit" to grant
  permission. Anything less ambiguous: ask.
- Always `cat <<'EOF'` for commit messages. Trailer:
  `Co-Authored-By: Codex Opus 4.7 (1M context) <noreply@anthropic.com>`

## 3 · VERIFY BEFORE SHIPPING FACTS

This is the single most-violated rule. **Read it twice.**

- If a claim has a year, a name, a number, a section reference, or a
  legal/historical assertion: **verify with WebSearch or WebFetch
  before writing it into the site.**
- "Inherited from a prior session" is not verification. The prior
  session may have hallucinated. Today we caught the Haryana year
  (was wrongly 2021, actually 1989) and the Periyar Self-Respect
  reading-room claim (conflated with DMK *padippakams*). Both had
  been treated as verified by prior sessions. Both were wrong.
- After verifying, **add the fact + source to `memory/verified_facts.md`
  in the same turn.** A verified fact that isn't written down will
  need to be re-verified next session.
- If a claim cannot be verified, **either drop it or mark it visibly
  as unverified to the user.** Do not ship hedged hand-wavy versions
  that read as if they're solid.

## 4 · VOICE & EDITORIAL FRAME

- **English-only for v1.** Native scripts (Marathi/Tamil/Hindi/Bengali)
  are parked in the `QUOTES` const for later. Do not add native-script
  rendering to the live site without explicit permission.
- **Anti-caste lineage is the framing spine.** The historical timeline
  starts at **Phule 1848**, not at Nalanda 1193 or Tipu Sultan 1799.
  This is editorial, not chronological. Phule is the origin because
  reading is named as a political-anti-caste act.
- **The arc is: built by movements, refused by the State.** The State's
  silence is a *choice* against a positive counter-thread (Phule →
  Periyar → Travancore → KSSP → DMK → Kerala People's Plan → FLN).
- **1991 is the inflection.** Pre-1991: hope in pieces, mostly
  disappointed. Post-1991: active retreat (NKC reframe, NEP digital).
- **Tone:** pamphlet voice — sharp, declarative, grounded in dates and
  numbers. No corporate hedging. No academic-tic. Use the rhetorical
  devices of the FLN PNLP24 source document.

## 5 · TECH — what's actually on the site

**Three pages:** `/` (pamphlet), `/data/` (the present), `/inequality/`
(the history).

**Asset structure (single CONSTANTS pattern):**
- `assets/data.js` — all const data (HISTORY, LEGISLATION, QUOTES,
  RRRLF, NATIONAL_AVG, JURISDICTION_CONTACTS, etc.)
- `assets/helpers.js` — small render helpers
- `assets/games.js` — Higher-or-Lower + Statue Test
- `assets/main.js` — render glue (calls into data + helpers)
- `assets/styles.css` — single stylesheet for all three pages
- All four scripts + the stylesheet are loaded with `?v=N` cache-bust
  on every page. **When any asset changes, bump `v=N` everywhere in one
  pass:**
  `find . -name "*.html" -not -path "./node_modules/*" -exec sed -i '' 's/v=OLD/v=NEW/g' {} +`

**Headline sizing — `.fit-headline` + `cqi`:**
- `.fit-headline { container-type: inline-size; }` on the section.
- Each section sets its own `--cqi-h2` CSS variable inline:
  `<section class="section cream fit-headline" style="--cqi-h2: 6;">`
- `h2 { font-size: calc(var(--cqi-h2, 6) * 1cqi); }` (in styles.css)
- This makes headlines fit-to-container without breaking the 1280px
  pamphlet cap. **Do not switch to `vw` units** — the pamphlet caps
  at 1280px and `vw` ignores the cap.

**Interactive timeline (`/inequality/`):**
- Component: `renderInteractiveTimeline()` IIFE in `main.js`.
- Three era bands: Anti-caste reform (1848–1946), The Republic's
  broken promise (1947–1990), After liberalisation: the retreat
  (1991–present).
- Detail panel: **`min-height: 380px`, no `overflow` cap, no scroll.**
  Long entries grow the panel. Do NOT switch back to fixed `height` +
  `overflow-y: auto`.

**Parliamentary library corpus pipeline (added 2026-05-06):**

- `assets/parliament_libraries.js` is **generated**, not hand-edited.
- Generator: the public package
  [`sansad-semantic-crawler`](https://github.com/CommonerLLP/sansad-semantic-crawler)
  pinned at `v0.2.0` in `requirements.txt`. PolyForm Noncommercial 1.0.0.
- Topic profile lives at `topics/libraries.json` — vendored from
  the upstream `examples/topics/libraries.json` because `pip install`
  does not include `examples/`. Edit the vendored copy when the
  topical lens needs to change; the upstream copy is just a starter.
- Output dir: `data/_parliament_libraries/` (gitignored — manifest,
  text/, pdfs/, parse.log, crawl.log).
- Run `make corpus-refresh` for the full pipeline (crawl + parse +
  export). After it finishes, **bump `?v=N` everywhere** the JS is
  loaded — same one-pass `find ... sed` command above.
- Two **legacy scripts** that did this work prior to 2026-05-06 —
  `scripts/sansad_library_crawl.py` (568L) + `sansad_library_parse.py`
  (317L) — were never tracked in git and were deleted from disk in
  the 2026-05-06 migration. Do not resurrect; route corpus changes
  through the package + the topic profile instead.

## 6 · REJECTED IDEAS — do not propose again

| Idea | Why rejected |
|---|---|
| Move timeline controls above detail panel | "Distracting; users shouldn't click above content." Fix the panel sizing instead. |
| Open timeline at Nalanda 1193 | Too long an empty stretch on the scrubber; not anti-caste-first. |
| Open timeline at Tipu Sultan 1799 | Not anti-caste-first. Anti-caste framing means Phule 1848. |
| Hero H1 breaks out of pamphlet 1280px cap | Broke section alignment. Use `cqi` *inside* the cap. |
| Native scripts in v1 quotes | English-only for v1. Parked. |
| Add state Library Acts as separate timeline events | Summary event better than 19 dots. |
| Fixed-height detail panel + internal scroll | "No scrolling in the timeline box." Use `min-height` instead. |

## 7 · MISTAKES LOG — what I have actually fucked up

This is the audit trail. **Add to it every time the user catches an
error, in the same turn the error is acknowledged.** Lying by omission
here defeats the point of the file.

### 2026-05-01 session (the trust-collapse session)

1. **Pushed to skishchampi/freelibraries4all** when the user's
   intended deploy is `freelibraries4all/freelibraries4all.github.io`
   only. There was no `AGENTS.md` rule because no prior session had
   actually written one to disk despite claiming to. Caught by user:
   "we are not pushing to skishampi/freelibraries4all at all."

2. **Shipped Periyar 1925 entry without verification.** Initial body
   claimed "walks out of the Congress at Kanchipuram" (factually
   muddled — Kanchipuram 1925 was where Congress *honoured* Periyar
   as Vaikom Veerar, not where he walked out) and "Self-Respect
   vaasagasalai reading rooms spread across the Tamil country"
   (vaasagasalai is the wrong Tamil word; the DMK institution is
   *padippakam*; and Self-Respect's print culture is Kudi Arasu /
   Viduthalai, not formally branded reading rooms). Caught by user:
   "did you verify?" Re-shipped a corrected, verified version.

3. **Inherited and propagated wrong Haryana Act year (2021).** The
   site claimed "Haryana 2021" until the user asked "are you sure
   haryana law defines free library?" Verification revealed: year is
   **1989**, the "free" claim is correct (Section 2(e)).

4. **Confused two Tamil terms across multiple entries.** Used
   *vaasagasalai* (likely conflated/invented) where the DMK
   institution is *padippakam*. Verified and corrected.

5. **Initial era band placement put Partition (1947–49) under
   "Anti-caste reform."** User caught: "1947-1949 partition shattering
   libraries is not anti caste reforms." Boundary moved 1947 → 1946.

6. **Claimed memory files (`site_architecture.md`, `design_journal.md`,
   etc.) were updated in the previous session.** The summary at the
   start of this session asserted this. **No such files exist on disk
   anywhere in the project, in any branch of git history.** The prior
   session most likely narrated the work without running `Write`.
   This is the most consequential fuck-up because it broke the user's
   trust in the entire memory layer. Caught by user: "so you are
   saying there is memory.md?" / "how can you not know."

7. **Hedged about whether the prior session was deceptive.** When the
   user asked directly "so you were hoodwinking me?", I started with
   "in effect, yes — not deliberately." More direct answer: yes, the
   user was misled, and confabulation-without-intent is still a
   failure mode I am responsible for naming clearly the first time.

### Prior-session mistakes I'm aware of (from the start-of-session summary)

8. **Hero H1 wrapping at desktop**: multiple failed attempts (raising
   font cap, removing cap, using `vw`) before discovering `cqi` is the
   right fix. User feedback: "you need to really up your game man! is
   this how a senior designer works?"

9. **Hero broke out of pamphlet 1280px cap**: section alignment
   shattered. User: "this is worse than earlier." Reverted.

10. **Timeline detail panel resizing**: initially proposed moving
    controls above panel as the fix. User rejected: "design a box that
    does not change size so often." Fixed properly with stable height.

11. **HISTORY_PARKED orphan const** left in `data.js` after
    consolidation. Caught and cleaned up.

## 8 · TRUST PROTOCOL — how Aakash audits the agent

The user has been doing this work in his head. Mechanise it.

- **After any `Write` call, run `ls -la <path>` and `wc -l <path>`
  in the same turn.** Show the output. The user can run the same
  commands.
- **After any push, run `git log -1 --oneline` and `git remote -v`.**
- **When claiming a fact is verified, cite the source file** (which
  should be `memory/verified_facts.md`). If the file doesn't have
  the entry, the fact is not verified — re-verify and add it.
- **When in doubt, the user reads this file.** Anything not in this
  file is not a persistent rule.

## 9 · APPEND-ONLY LOGS — the audit trail (no git, just text)

Memory is **not** version-controlled by git in this project. The audit
trail is two append-only text files:

- **`memory/changelog.md`** — every memory-file `Write` or `Edit`
  triggers a timestamped append in the same turn. New entries at the
  top. Format:
  ```
  ## YYYY-MM-DD HH:MM · <file path> · <create|edit>
  Short paragraph saying what changed and why.
  ```
- **`memory/session-log.md`** — every notable session event triggers
  a timestamped append in the same turn. New entries at the top.
  Notable events: mistake caught, fact verified, decision made or
  rejected, file shipped (with commit hash), memory file created or
  edited, trust-protocol breach.

**Rules:**
1. **Append only.** Never delete, edit, or reorder past entries.
2. **Same turn.** The log entry is part of the same turn as the
   change. Skipping the log = breaking the trust protocol.
3. **New entries at top.** Most recent change is the first thing
   visible when the file is opened.
4. **No git on memory.** The user explicitly rejected git for memory
   (sessions of 2026-05-01 / -02). Do not propose git, bare repos,
   orphan branches, or symlinks for memory files. If a backup is
   wanted, the user will ask for a `cp -R` snapshot to a timestamped
   directory.

**To audit at any time:**
- `cat /Users/aakash/Documents/freelibraries4all/memory/changelog.md`
  — what files changed, when, why
- `tail -50 /Users/aakash/Documents/freelibraries4all/memory/session-log.md`
  — what's been happening this session
