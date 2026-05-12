# The Right to Read

This repository powers the The Right to Read GitHub Pages site:

```text
https://theright2read.github.io
```

It is a static public data dashboard tracking public library funding in India.
The site compares Indian state-level per-capita library spending, Raja
Rammohun Roy Library Foundation (RRRLF) grants, public library legislation,
National Mission on Libraries (NML) participation, and international spending
benchmarks.

If you are another developer, this README is meant to be a quick scan: fork the
repo, run the dashboard locally, and reproduce the deployed
`theright2read.github.io` site from static files.

There is no build step, backend, database, or package manager. The live site is
served directly from the static files in this repo.

## Ethics and Principles

The Right to Read is grounded in the principles of social justice and 
democratic access to knowledge. The project treats access to books, 
public libraries, and knowledge infrastructure as essential components 
of material equality and civil participation.

The dashboard is built with the understanding that public libraries are 
critical for those who have been historically excluded from institutional 
literacy and cultural power. This includes Dalit, Bahujan, Adivasi, 
minority, and working-class communities, among others.

Contributors are expected to maintain these commitments:

- Treat library access as a fundamental public good.
- Prioritize technical accuracy in documenting exclusion across caste, 
  class, region, and language.
- Maintain analytical rigor: follow the evidence where it reveals 
  systemic neglect.
- Build tools and data that empower researchers and communities to 
  hold public institutions accountable.

## Refreshing The Parliamentary Library Corpus

`assets/parliament_libraries.js` is generated, not hand-edited. As of
2026-05-06 the crawler that produces it is the standalone public-good
package
[`sansad-semantic-crawler`](https://github.com/CommonerLLP/sansad-semantic-crawler)
(PolyForm Noncommercial 1.0.0), pinned at `v1.0.0` in
[`requirements.txt`](./requirements.txt). The host project supplies the
topic profile at [`topics/libraries.json`](./topics/libraries.json) (a
vendored copy of the package's `examples/topics/libraries.json`,
because `pip install` does not pull `examples/`).

```sh
make deps              # one-time: install pinned deps into .venv
make corpus-refresh    # crawl LS + RS, parse PDFs, regenerate the JS
```

After regeneration, **bump the `?v=N` cache-bust suffix** wherever the
JS or CSS is loaded. One-pass update across all HTML files:

```bash
find . -name "*.html" -not -path "./node_modules/*" \
  -exec sed -i '' 's/v=OLD/v=NEW/g' {} +
```

The legacy `scripts/sansad_library_crawl.py` + `sansad_library_parse.py`
that previously did this work were retired in the 2026-05-06 migration;
they were never tracked in git (dev-time tools that produced the
committed JS). If you find a stale local copy on disk, it is safe to
delete.

## Quick Start For Developers

1. Fork the repo on GitHub:

   ```text
   https://github.com/theright2read/theright2read.github.io
   ```

2. Clone your fork:

   ```sh
   git clone https://github.com/YOUR-USER/theright2read.github.io.git
   cd theright2read.github.io
   ```

3. Serve the site locally:

   ```sh
   python3 -m http.server 8000
   ```

4. Open:

   ```text
   http://localhost:8000
   ```

5. Edit `index.html`, refresh the browser, and verify the dashboard still works.

## Reproducing The GitHub Pages Site

This repo is structured for GitHub Pages. To reproduce the public site from a
fork:

1. Keep the production dashboard at the repository root as `index.html`.
2. Push your changes to the fork's `main` branch.
3. In GitHub, open the fork's repository settings.
4. Go to **Pages**.
5. Set the source to deploy from the `main` branch and the repository root.
6. Save and wait for GitHub Pages to publish.

For a personal or organization fork, GitHub will usually publish at:

```text
https://YOUR-USER.github.io/theright2read.github.io/
```

To publish at `https://YOUR-USER.github.io/`, rename the fork to
`YOUR-USER.github.io` before enabling Pages.

## What The Dashboard Covers

- India vs. world public library spending, with nominal USD and PPP-adjusted
  comparisons.
- State-by-state public library expenditure for 31 Indian states and union
  territories from 2014-15 through 2020-21.
- RRRLF annual grant trends from 2003 through 2023.
- State-wise RRRLF releases for 2021-22 through 2024-25, based on Parliament
  data.
- Public Library Act status by state and how legislation relates to spending.
- State report cards combining spending, legislation, RRRLF utilization, and NML
  participation.
- A state-specific "Write to Your MP" letter generator for library advocacy.
- **`/spend/`** — per-capita library expenditure analysis. Corrects
  Kulkarni-Balaji-Dhanamjaya (2025) with TG 2020 population projections,
  extrapolates state series to 2024-25, compares MHA Zonal Councils
  (1956) against Ministry of Culture Cultural Zones (1985), and reads
  the data against four generations of state Library Acts. Generated
  by `scripts/build_spend_page.py`.

## Data Sources

The dashboard cites and combines public sources, including:

- Ministry of Culture, Government of India: state-wise per-capita expenditure on
  public libraries, 2014-15 to 2020-21.
- Raja Rammohun Roy Library Foundation annual and state-wise grant data.
- Rajya Sabha Question 1316, answered July 31, 2025, for RRRLF state-wise data.
- Lok Sabha questions from the July-August 2025 session on NML status and
  library funding.
- Public library legislation surveys for Indian states and union territories.
- International benchmarks from sources such as IMLS, CIPFA, NAPLE,
  Libraries.fi, ALIA, and Statistics Canada / Alberta.

Source notes, caveats, and conversion notes are included in the dashboard
footer. Data corrections are welcome, especially when they include a primary
source link, table, annexure, or official PDF.

## Acknowledgements

Special thanks to the Open Budgets India project by CivicDataLab for opening up
Indian budget data. This project relies significantly on the broader
availability and usability of public budget data that work like Open Budgets
India has made possible.

## Repository Structure

```text
.
|-- index.html           # The pamphlet — the case
|-- data/index.html      # The data — RRRLF, State Report Card, etc.
|-- inequality/index.html# The history — interactive timeline
|-- spend/index.html     # Per-capita expenditure analysis (generated)
|-- assets/              # styles.css, data.js, helpers.js, games.js, main.js
|-- scripts/             # render_essays.py, sync_agents.py, build_spend_page.py
|-- design/index.html    # Earlier design/prototype version
|-- README.md
|-- CONTRIBUTING.md
`-- LICENSE
```

Most application logic, styles, and data live inside `index.html`,
`data/`, `inequality/`, and shared `assets/`. The page loads Chart.js
from a CDN.

`spend/index.html` is generated by `scripts/build_spend_page.py` and
carries a `DO-NOT-HAND-EDIT` header — regenerate with
`python3 scripts/build_spend_page.py`.

## Development Notes

- Keep the site usable as a static page.
- Prefer primary public sources for data changes.
- Add source notes when changing numbers, formulas, classifications, or claims.
- Check the dashboard on mobile and desktop widths after visual changes.
- Keep accessibility in mind: chart colors, table readability, and keyboard
  navigation matter for a public-interest site.

## License

This project is licensed under the [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)
license. Noncommercial use only. See `LICENSE` for the full license text.
