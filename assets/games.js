/* ============================================================
   games.js — interactive games for /data/.

   - State Higher-or-Lower + Statue Test
   - "What Did We Build?" (Diversion Game)

   Each IIFE no-ops if its root container isn't in the DOM, so the
   pamphlet (/) can load this script harmlessly even though it has
   neither game.
   ============================================================ */

// ─── INTERACTIVE GAME — Higher-or-Lower + Statue Test ─────────────
(function initGame() {
  const app = document.getElementById("game-app");
  if (!app) return;
  const show = makeScreenSwitcher(app);

  // State pairs for Higher-or-Lower: pre-shuffle 5 contrasting pairs.
  const stateNames = Object.keys(STATE_DATA).filter((n) => STATE_POP_MN[n]);
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function makePairs(n) {
    const pairs = [];
    const seen = new Set();
    let safety = 0;
    while (pairs.length < n && safety++ < 200) {
      const [a, b] = shuffle(stateNames).slice(0, 2);
      if (a === b) continue;
      const key = [a, b].sort().join("|");
      if (seen.has(key)) continue;
      // skip pairs where both spends are essentially identical
      const va = STATE_DATA[a][6] || 0, vb = STATE_DATA[b][6] || 0;
      if (Math.abs(va - vb) < 0.05) continue;
      seen.add(key);
      pairs.push([a, b]);
    }
    return pairs;
  }

  let pairs = [], roundIdx = 0, streak = 0, userHomeState = null;

  // Populate the home-state picker on the intro screen.
  const homeSel = document.getElementById("game-home");
  if (homeSel) {
    Object.keys(STATE_DATA).sort().forEach((name) => {
      if (!STATE_POP_MN[name]) return; // only states with pop data
      const opt = document.createElement("option");
      opt.value = name; opt.textContent = name;
      homeSel.appendChild(opt);
    });
    homeSel.addEventListener("change", () => {
      const startBtn = document.getElementById("game-start");
      if (startBtn) startBtn.disabled = !homeSel.value;
    });
  }

  function startGame() {
    if (homeSel && homeSel.value) userHomeState = homeSel.value;
    pairs = makePairs(5);
    roundIdx = 0; streak = 0;
    show("round");
    renderRound();
  }

  function renderRound() {
    const [a, b] = pairs[roundIdx];
    document.getElementById("game-round").textContent = roundIdx + 1;
    document.getElementById("game-streak").textContent = streak;
    const aEl = document.getElementById("game-a");
    const bEl = document.getElementById("game-b");
    aEl.dataset.state = a;
    bEl.dataset.state = b;
    aEl.className = "game-card"; // resets correct/wrong/disabled/your-pick
    bEl.className = "game-card";
    document.getElementById("game-feedback").hidden = true;
    document.getElementById("game-feedback").innerHTML = "";
    aEl.innerHTML = `<div class="game-card-name">${a}</div><div class="game-card-cta">PICK THIS</div>`;
    bEl.innerHTML = `<div class="game-card-name">${b}</div><div class="game-card-cta">PICK THIS</div>`;
  }

  function pickCard(picked, other) {
    const va = STATE_DATA[picked][6] || 0;
    const vb = STATE_DATA[other][6] || 0;
    const correct = va > vb;
    if (correct) streak++;
    document.getElementById("game-streak").textContent = streak;

    const aEl = document.getElementById("game-a");
    const bEl = document.getElementById("game-b");
    [aEl, bEl].forEach((el) => el.classList.add("disabled"));
    const pickedEl = aEl.dataset.state === picked ? aEl : bEl;
    const otherEl  = aEl.dataset.state === picked ? bEl : aEl;
    pickedEl.classList.add(correct ? "correct" : "wrong");
    otherEl.classList.add(correct ? "wrong" : "correct");
    pickedEl.classList.add("your-pick"); // mark the user's choice regardless of right/wrong
    pickedEl.querySelector(".game-card-cta").outerHTML =
      `<div class="game-card-reveal">₹${fmtMoney(va)} / yr</div>`;
    otherEl.querySelector(".game-card-cta").outerHTML =
      `<div class="game-card-reveal">₹${fmtMoney(vb)} / yr</div>`;

    const fb = document.getElementById("game-feedback");
    fb.hidden = false;
    fb.classList.toggle("hit", correct);
    if (correct) {
      const ratio = vb > 0 ? Math.round(va / vb) : Infinity;
      fb.innerHTML = `<strong>Right.</strong> <strong>${picked}</strong> spends ₹${fmtMoney(va)} per person per year. <strong>${other}</strong> spends ₹${fmtMoney(vb)}. ${ratio >= 2 ? `That's <strong>${ratio === Infinity ? "∞" : ratio + "×"}</strong> more.` : ""}`;
    } else {
      fb.innerHTML = `<strong>Wrong.</strong> <strong>${other}</strong> actually spends more — ₹${fmtMoney(vb)} per person per year, vs ₹${fmtMoney(va)} for ${picked}.`;
    }

    setTimeout(() => {
      roundIdx++;
      if (roundIdx >= pairs.length) {
        startStatue();
      } else {
        renderRound();
      }
    }, 2200);
  }

  document.getElementById("game-a").addEventListener("click", (e) => {
    if (e.currentTarget.classList.contains("disabled")) return;
    pickCard(e.currentTarget.dataset.state, document.getElementById("game-b").dataset.state);
  });
  document.getElementById("game-b").addEventListener("click", (e) => {
    if (e.currentTarget.classList.contains("disabled")) return;
    pickCard(e.currentTarget.dataset.state, document.getElementById("game-a").dataset.state);
  });

  // STATUE TEST
  function startStatue() {
    show("statue");
    // Anchor the statue test to the user's HOME state (chosen on intro).
    // Falls back to the lowest-spending state in any played pair if no home set.
    const state = userHomeState || (pairs.length ? pairs[pairs.length - 1].slice().sort((x, y) => (STATE_DATA[x][6] || 0) - (STATE_DATA[y][6] || 0))[0] : Object.keys(STATE_DATA)[0]);
    const perCap = STATE_DATA[state][6] || 0;
    const popCr = (STATE_POP_MN[state] || 0) / 10; // millions → crore
    const annualBudget = perCap * popCr; // ₹ crore / year (pop in crore × ₹/person)
    const yearsForOneStatue = annualBudget > 0 ? Math.round(STATUE_OF_UNITY_CR / annualBudget) : Infinity;

    document.getElementById("statue-q").innerHTML =
      `<strong>${state}</strong> spends roughly <strong>₹${fmtMoney(annualBudget)} crore</strong> a year on every public library combined.<br>How many years would <strong>${state}</strong> need to equal <strong>one ₹${fmtIN(STATUE_OF_UNITY_CR)} crore Statue of Unity?</strong>`;

    document.getElementById("statue-reveal").hidden = true;
    document.getElementById("statue-reveal").innerHTML = "";

    const submit = document.getElementById("statue-submit");
    const guess = document.getElementById("statue-guess");
    guess.value = 100;
    setTimeout(() => guess.focus(), 50);

    function reveal() {
      const userGuess = Math.max(0, parseInt(guess.value, 10) || 0);
      let verdict;
      if (yearsForOneStatue === Infinity) {
        verdict = `<strong>${state}</strong> spends so little on libraries that the answer is, literally, <strong>forever</strong>.`;
      } else {
        const off = userGuess > 0 ? Math.abs(userGuess - yearsForOneStatue) / yearsForOneStatue : 1;
        if (off < 0.10) verdict = `<strong>Eerily close.</strong> You guessed within 10% of the truth.`;
        else if (off < 0.30) verdict = `<strong>In the ballpark.</strong> You guessed within 30% of the real number.`;
        else if (userGuess < yearsForOneStatue) {
          const mult = Math.round(yearsForOneStatue / Math.max(userGuess, 1));
          verdict = `<strong>You under-guessed by ${mult}×.</strong> The real answer is <strong>${fmtIN(yearsForOneStatue)} years</strong>. ${state}'s library budget is much smaller than you think.`;
        } else {
          const mult = Math.round(userGuess / Math.max(yearsForOneStatue, 1));
          verdict = `<strong>You over-guessed by ${mult}×.</strong> The real answer is <strong>${fmtIN(yearsForOneStatue)} years</strong>. Somehow worse than your worst case.`;
        }
      }

      document.getElementById("statue-reveal").innerHTML =
        `<div class="statue-reveal-num">${yearsForOneStatue === Infinity ? "∞" : fmtIN(yearsForOneStatue)}<span class="unit">years</span></div>
         <div class="statue-reveal-text">${verdict} ${state} would need <strong>${yearsForOneStatue === Infinity ? "an eternity" : fmtIN(yearsForOneStatue) + " years"}</strong> of its annual library budget to equal a single Statue of Unity. The Centre and Gujarat funded one in five.</div>
         <div class="statue-reveal-actions">
           <button class="game-btn" id="statue-next">SEE FINAL SCORE →</button>
         </div>`;
      document.getElementById("statue-reveal").hidden = false;
      document.getElementById("statue-next").addEventListener("click", showEnd);
    }

    submit.onclick = reveal;
    guess.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); reveal(); } };
  }

  function showEnd() {
    show("end");
    const final = document.getElementById("game-final");
    let line;
    if (streak === 5) line = `You got <span class="num">5/5</span>. You already know the scandal. Now do something with it.`;
    else if (streak >= 3) line = `You got <span class="num">${streak}/5</span>. Better than most. The library you'd visit doesn't exist yet.`;
    else if (streak >= 1) line = `You got <span class="num">${streak}/5</span>. The data is barely a guess for anyone. That is itself the point.`;
    else line = `You got <span class="num">0/5</span>. Don't blame yourself. Public-library spending in India is so low that the rankings are noise. Read the page. Write to your CM.`;
    final.innerHTML = line;
  }

  document.getElementById("game-start").addEventListener("click", startGame);
  // Replay: re-use the same home state, skip the intro, go straight into round 1.
  document.getElementById("game-replay").addEventListener("click", () => {
    if (!userHomeState && homeSel && homeSel.value) userHomeState = homeSel.value;
    pairs = makePairs(5);
    roundIdx = 0; streak = 0;
    show("round");
    renderRound();
  });
})();

// ─── DIVERSION GAME — "What did we build?" runner ───────────────

(function initDiversionGame() {
  const app = document.getElementById("dgame-app");
  if (!app) return;
  const show = makeScreenSwitcher(app);

  let idx = 0, score = 0;

  function start() { idx = 0; score = 0; show("round"); renderRound(); }

  function renderRound() {
    const r = DIVERSION_ROUNDS[idx];
    document.getElementById("dgame-round").textContent = idx + 1;
    document.getElementById("dgame-score").textContent = score;
    document.getElementById("dgame-prompt").innerHTML = r.prompt;
    const optsEl = document.getElementById("dgame-options");
    // Shuffle option order so the "correct" item isn't always at the same position
    const shuffled = r.options.slice().sort(() => Math.random() - 0.5);
    optsEl.innerHTML = shuffled.map((o, i) => `
      <button class="dgame-option" data-correct="${o.correct ? "1" : "0"}" data-i="${i}" type="button">
        <span class="dgame-marker" aria-hidden="true"></span>
        <span class="dgame-text">${o.text}<span class="dgame-cost">${esc(o.cost)}</span></span>
      </button>`).join("");
    document.getElementById("dgame-feedback").hidden = true;
    document.getElementById("dgame-feedback").innerHTML = "";

    optsEl.querySelectorAll(".dgame-option").forEach((btn) => {
      btn.addEventListener("click", () => onPick(btn));
    });
  }

  function onPick(btn) {
    const r = DIVERSION_ROUNDS[idx];
    const correct = btn.dataset.correct === "1";
    if (correct) score++;
    document.getElementById("dgame-score").textContent = score;

    const optsEl = document.getElementById("dgame-options");
    optsEl.querySelectorAll(".dgame-option").forEach((b) => {
      b.classList.add("disabled");
      if (b.dataset.correct === "1") b.classList.add("correct");
      else b.classList.add("wrong");
    });
    btn.classList.add("your-pick");

    const fb = document.getElementById("dgame-feedback");
    fb.hidden = false;
    fb.innerHTML = `
      <div>${r.feedback}</div>
      <span class="alt">${r.diversion}</span>
      <div class="next-btn"><button class="game-btn" id="dgame-next" type="button">${idx + 1 < DIVERSION_ROUNDS.length ? "NEXT ROUND →" : "SEE THE PATTERN →"}</button></div>
    `;
    document.getElementById("dgame-next").addEventListener("click", () => {
      idx++;
      if (idx >= DIVERSION_ROUNDS.length) showEnd();
      else renderRound();
    });
  }

  function showEnd() {
    show("end");
    const final = document.getElementById("dgame-final");
    let line;
    if (score === 6) line = `You got <span class="num">6/6</span>. You already see the pattern. India funds vanity.`;
    else if (score >= 4) line = `You got <span class="num">${score}/6</span>. You caught on by round four. So has every Indian voter who has been paying attention.`;
    else if (score >= 2) line = `You got <span class="num">${score}/6</span>. You assumed your government would fund the useful thing. India isn't there yet.`;
    else line = `You got <span class="num">${score}/6</span>. The State's pattern surprised you because nobody told you. That is itself the diversion.`;
    final.innerHTML = line;
  }

  document.getElementById("dgame-start").addEventListener("click", start);
  document.getElementById("dgame-replay").addEventListener("click", start);
})();
