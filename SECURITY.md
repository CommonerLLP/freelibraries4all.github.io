# Security Policy

## Supported Versions

Right to Read is a static public-interest pamphlet served from GitHub
Pages. There are no versioned releases — the live site is whatever is
on the `main` branch.

| Branch | Supported          |
| ------ | ------------------ |
| `main` | :white_check_mark: |
| other  | :x:                |

## Reporting a Vulnerability

This project is grounded in public-interest research. If you discover a
vulnerability, please report it through one of the following channels:

1. **Non-sensitive issues** — open a GitHub Issue:
   <https://github.com/CommonerLLP/theright2read/issues>. Use this for
   things like broken links, content errors, or minor accessibility
   regressions.

2. **Sensitive disclosure** — privately email the maintainer at the
   address listed on the maintainer's GitHub profile, or use GitHub's
   private vulnerability reporting feature. Use this for anything that
   could enable abuse of readers (XSS, CDN-integrity issues, etc.) or
   expose private data.

We will acknowledge the report within a reasonable time and credit
contributors who agree to be named.

## Scope

The site is fully static — no backend, no scrapers, no user data, no
authentication. The relevant security surfaces are narrow:

- **Cross-site scripting (XSS).** Any rendered user-derived string
  (search params, anchor fragments, etc.). The site uses `textContent`
  for user-derived strings; `innerHTML` only for fixed templates.
- **Third-party content integrity.** The site loads fonts from
  `fonts.googleapis.com` and Chart.js from `cdn.jsdelivr.net`. Reports
  about a compromised or hijacked dependency are in scope.
- **Data accuracy.** The site cites primary sources for every numerical
  claim (see `memory/verified_facts.md` locally, the in-page Data
  Sources sections, and `/spend/` Methods). Reports about misattributed
  or fabricated claims are treated as security-relevant — a public-
  interest pamphlet's value is its sourcing.
- **Licensing.** Code is under PolyForm Noncommercial 1.0.0; data is
  under CC BY-NC-SA 4.0. Reports about license-violating reuse can be
  routed through the same channels.

## Out of scope

- The third-party services we link to (`fln.org.in`, `nhm.gov.in`,
  `polyformproject.org`, etc.) are not our infrastructure.
- The local-only build script `scripts/build_spend_page.py` does not
  ship to the live site; reports about its behaviour on a maintainer's
  laptop are not security issues.
