/* ============================================================
   helpers.js — small utilities shared by both pages.
   Loaded after data.js, before games.js + main.js.
   ============================================================ */

// Convenience query selector. Returns null if the element doesn't exist —
// callers must guard.
const $ = (s) => document.querySelector(s);

// "Safe" selector: returns a no-op stand-in when the element is missing,
// so `$$("#x").innerHTML = ...` doesn't throw on pages that don't have
// that element. Use sparingly — explicit guards are still clearer.
const $$ = (s) => document.querySelector(s) || { innerHTML: "", set innerHTML(_) {} };

// Indian-locale number formatting (lakhs/crores grouping).
const fmtIN = (n) => n.toLocaleString("en-IN");
const fmtMoney = (n) => n.toLocaleString("en-IN", { maximumFractionDigits: 2 });

// HTML-escape a string for safe innerHTML insertion.
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[c]));

// Replace {{CONSTANT_NAME}} placeholders in HTML with values from window.CONSTANTS.
// Used to keep canonical numbers (statue cost, per-capita, etc.) in one place.
// Call once on DOMContentLoaded; opt-in by adding `data-substitute` to a node.
function substituteConstants(root = document) {
  if (!window.CONSTANTS) return;
  root.querySelectorAll("[data-substitute]").forEach((el) => {
    el.innerHTML = el.innerHTML.replace(/\{\{([A-Z_][A-Z0-9_]*)\}\}/g, (_, key) => {
      const v = window.CONSTANTS[key];
      return v == null ? "{{" + key + "}}" : v;
    });
    el.removeAttribute("data-substitute");
  });
}
