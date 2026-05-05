# Contributing

Thank you for your interest in contributing to Free Libraries for All. This
project is a static public data dashboard about public library funding in India.

We welcome contributions from developers, researchers, data analysts,
public-finance readers, journalists, and library advocates. The project is
especially interested in contributors who can expand the site's state and
regional analysis by working with public finance records and official documents.

## Project Direction

The current dashboard provides national and state-level views of public library
spending, legislation, RRRLF grants, NML participation, and international
benchmarks.

The next phase is to add more detailed analysis of specific states, union
territories, and regions. This includes understanding how state governments
budget for public libraries, how funds move through departments and schemes,
what audit reports show, and how public library spending appears in public
accounts.

## Priority Contribution Areas

### State And Regional Research

Contributors can help by selecting one state, union territory, or region and
building a documented analysis of its public library finances.

Relevant work includes:

- Reading historical state budget documents.
- Reviewing demand-for-grants documents and department-level expenditure books.
- Studying state finance accounts, appropriation accounts, and public accounts
  data.
- Reviewing CAG audit reports and other audit documents.
- Finding library-related line items that may sit under education, culture,
  language, archives, rural development, local bodies, or other departments.
- Comparing budget estimates, revised estimates, actual expenditure, and
  utilization.
- Tracking state library directorates, library cess systems, grants-in-aid, and
  support to district, taluk, panchayat, municipal, and community libraries.
- Connecting state-level spending patterns to library legislation, RRRLF grants,
  National Mission on Libraries participation, and parliamentary answers.

### Data And Methodology

Data contributions should make the public library finance picture more
accurate, reproducible, and auditable. Useful contributions include:

- Correcting existing figures with primary sources.
- Adding source notes for budget heads, schemes, departments, and classification
  changes.
- Tracing library spending across multiple financial years.
- Comparing budget estimates, revised estimates, and actual expenditure.
- Documenting calculations, unit conversions, and assumptions.
- Structuring data so future state-level research is easier to review.

### Frontend And Site Improvements

Developer contributions are also welcome. Useful improvements include:

- Improving chart readability and table usability.
- Adding state profiles or region-specific views.
- Improving mobile layout, accessibility, keyboard behavior, and performance.
- Fixing interactions in tabs, filters, chart clicks, sharing, copying, and CSV
  downloads.
- Refactoring carefully where it makes the static site easier to maintain.

## Source Standards

Data changes need a source trail. When changing numbers, classifications, or
claims, please include:

- The exact source name.
- A link to the official page, PDF, answer, annexure, report, or dataset when
  available.
- The publication, budget, audit, or answer date.
- The financial year covered.
- The table, page, question number, demand number, major head, sub-major head,
  minor head, scheme name, annexure, or row used.
- Any transformation applied, such as per-capita calculation, inflation
  adjustment, currency conversion, PPP adjustment, or unit conversion from
  rupees to lakhs/crores.

Prefer primary public sources, including:

- State budget documents.
- State demand-for-grants books.
- Finance accounts and appropriation accounts.
- CAG reports and state audit reports.
- Public accounts and treasury data where available.
- Ministry of Culture, RRRLF, NML, Lok Sabha, and Rajya Sabha documents.
- State library department reports, rules, notifications, and annual reports.

News articles and secondary summaries can help explain context, but they should
not be the only basis for numeric changes when a primary source exists.

## Development Workflow

1. Fork the repository.
2. Create a focused branch for your change.
3. Make the smallest coherent change that addresses the issue or research
   question.
4. Document sources and assumptions in the relevant file, pull request, or
   methodology note.
5. Test the static site locally before opening a pull request.

## Code Style

- Keep the site static unless there is a strong reason to add tooling.
- Match the existing plain HTML, CSS, and JavaScript style.
- Use clear names for chart data, state data, and helper functions.
- Keep data transformations easy to audit.
- Avoid unrelated refactors in data correction pull requests.
- Do not commit local operating-system files such as `.DS_Store`.

## Local Checks

Before submitting a change:

1. Open `index.html` in a browser, or serve the repo with:

   ```sh
   python3 -m http.server 8000
   ```

2. Check the main tabs:

   - India vs World
   - State Tracker
   - RRRLF Grants
   - Legislation Gap
   - State Report Card
   - Parliament 2025
   - Write to Your MP

3. Try the interactive controls you touched, such as toggles, filters, sorting,
   chart clicks, copy buttons, share buttons, and CSV download.

4. Check at least one narrow mobile viewport and one desktop viewport.

## Pull Request Checklist

- The change is focused and described clearly.
- The state, region, scheme, or data question being addressed is named.
- Data changes cite primary sources.
- Source notes or methodology text were updated when needed.
- Calculations and unit conversions are explained.
- The dashboard still works as a static site.
- No generated local files, caches, or operating-system metadata are included.

## Tone And Content

The site should remain evidence-led and source-driven. Strong claims are
acceptable when they are supported by public records. Avoid unsupported
conclusions, partisan framing, or claims that cannot be traced back to a public
source.
