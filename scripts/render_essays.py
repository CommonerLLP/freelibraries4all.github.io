"""
Render essays from notes/blog-drafts/*.md → writing/<slug>/index.html.

Markdown is the canonical source. This script generates the HTML that
GitHub Pages serves, plus a regenerated writing/index.html listing.

Front-matter (YAML between --- delimiters) controls everything:

  ---
  title: "The Grammar of Refusal"
  slug: grammar-of-refusal
  date: 2026-05-07
  description: "..."
  dek: "..."   (one-line subhead under the title)
  ---

Usage:
  .venv/bin/python scripts/render_essays.py
or:
  make essays
"""
from __future__ import annotations

import re, sys
from pathlib import Path
from datetime import datetime

import markdown

REPO = Path(__file__).resolve().parents[1]
DRAFTS = REPO / "notes/blog-drafts"
WRITING = REPO / "writing"
ASSET_VER = "v=68"  # bump in lockstep with the site-wide ?v=N cache-bust ritual

INDEX_HEAD = """<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{description}" />
<link rel="icon" type="image/svg+xml" href="{asset_root}assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{asset_root}assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{asset_root}assets/favicon-16.png">
<link rel="shortcut icon" href="{asset_root}assets/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="{asset_root}assets/apple-touch-icon.png">
<meta name="theme-color" content="#dc2a14">
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="Right to Read — Free Libraries for All" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:locale" content="en_IN" />
{extra_meta}
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@600;700;900&family=Roboto+Slab:wght@400;500;700;900&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="{asset_root}assets/styles.css?{asset_ver}">
</head>
<body>
<a class="skip-link" href="#main-content">Skip to content</a>
<main class="pamphlet" id="main-content">

  <div class="strip">
    <span lang="en">Free Libraries For All</span>
    <span class="accent">A People's Pamphlet</span>
  </div>
"""

ESSAY_NAV = """
  <div class="data-backbar">
    <a href="/writing/" class="data-back-link">← All writing</a>
    <a href="/data/#parliament" class="data-back-link" style="margin-left: 16px;">The data →</a>
  </div>
"""

LISTING_NAV = """
  <div class="data-backbar">
    <a href="/" class="data-back-link">← Back to the pamphlet</a>
    <a href="/data/" class="data-back-link" style="margin-left: 16px;">The data →</a>
  </div>
"""

FOOT = """
</main>
</body>
</html>
"""


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_markdown). Front matter is the YAML
    block between two `---` lines at the very start of the file."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    yaml_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    fm: dict = {}
    for line in yaml_block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # strip surrounding quotes
        if val.startswith(('"', "'")) and val.endswith(('"', "'")):
            val = val[1:-1]
        # strip [tag, ...] lists — we don't render them, just pass through
        if val.startswith("[") and val.endswith("]"):
            val = [x.strip() for x in val[1:-1].split(",") if x.strip()]
        fm[key] = val
    return fm, body


def html_escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def render_essay(md_path: Path) -> dict:
    """Render one .md file to writing/<slug>/index.html. Return frontmatter
    dict (used for the listing page)."""
    raw = md_path.read_text(encoding="utf-8")
    fm, body_md = parse_front_matter(raw)
    slug = fm.get("slug") or md_path.stem.split("-", 3)[-1]  # YYYY-MM-DD-slug → slug
    title = fm.get("title", slug)
    date = fm.get("date", "")
    description = fm.get("description", "")
    dek = fm.get("dek") or ""
    word_count_label = fm.get("word_count") or ""

    # Drop the leading H1 from the markdown body — title is rendered separately
    body_md = re.sub(r"^\s*#\s+.*?\n", "", body_md, count=1)
    # Drop the immediate italic-line subtitle if it's the dek (we already have it)
    if dek:
        body_md = re.sub(r"^\s*\*[^*]+\*\s*\n", "", body_md, count=1)
    # Drop the leading horizontal-rule that often follows in our drafts
    body_md = re.sub(r"^\s*---\s*\n", "", body_md, count=1)

    body_html = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "attr_list", "smarty", "sane_lists"],
        output_format="html5",
    )

    # Map standard markdown output → our essay CSS classes.
    # Strategy: post-process the rendered HTML to re-tag elements that
    # need site-specific classes. This keeps the .md source clean.
    #
    # 1. Blockquote variants:
    #    - .essay-pull   if the blockquote content is a single <p> wholly
    #                    wrapped in <strong> (markdown for "> **text**")
    #    - .essay-quote  for everything else (verbatim long quotes)
    def _classify_blockquote(m: re.Match) -> str:
        inner = m.group(1).strip()
        # Single-paragraph blockquote that contains a <strong> = pull-quote
        # (the headline punchline). Multi-paragraph blockquote = verbatim
        # quote (typically a long quoted passage from a parliamentary record).
        n_paragraphs = len(re.findall(r"<p[> ]", inner))
        has_strong = "<strong>" in inner
        if n_paragraphs <= 1 and has_strong:
            return f'<blockquote class="essay-pull">{inner}</blockquote>'
        return f'<blockquote class="essay-quote">{inner}</blockquote>'
    body_html = re.sub(r"<blockquote>(.*?)</blockquote>", _classify_blockquote, body_html, flags=re.DOTALL)

    # 2. <h2> → add essay-section class
    body_html = re.sub(r"<h2(?![^>]*class)", '<h2 class="essay-section"', body_html)

    # 3. <table> → add essay-table class
    body_html = body_html.replace("<table>", '<table class="essay-table">')

    # 4. Table rows whose final cell starts with "+" or "−" get is-up / is-down.
    #    Lets markdown tables carry the visual emphasis without raw HTML.
    def _classify_row(m: re.Match) -> str:
        row = m.group(0)
        # Extract last <td>
        last_td_match = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
        if not last_td_match:
            return row
        last = re.sub(r"<[^>]+>", "", last_td_match[-1]).strip()
        if last.startswith("+"):
            return row.replace("<tr>", '<tr class="is-up">', 1)
        if last.startswith("−") or last.startswith("-"):
            return row.replace("<tr>", '<tr class="is-down">', 1)
        return row
    body_html = re.sub(r"<tr>.*?</tr>", _classify_row, body_html, flags=re.DOTALL)

    # 5. <ul> not nested → essay-list-bullets
    body_html = re.sub(r"<ul>(?!\s*<li><ul>)", '<ul class="essay-list-bullets">', body_html)

    # 6. <hr /> → essay-hr
    body_html = body_html.replace("<hr />", '<hr class="essay-hr">').replace("<hr>", '<hr class="essay-hr">')

    # 7. References paragraph: any <p> whose text starts with "References" → .essay-refs
    body_html = re.sub(r"<p>(<strong>References</strong>)", r'<p class="essay-refs">\1', body_html)

    # 8. Foot italic line right after the final <hr /> → .essay-foot
    body_html = re.sub(
        r'(<hr class="essay-hr">\s*)<p><em>',
        r'\1<p class="essay-foot"><em>',
        body_html,
    )

    # Estimate word count if not provided
    if not word_count_label:
        words = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", body_html)))
        rounded = round(words / 500) * 500
        word_count_label = f"~{rounded:,} words"

    # Compose the page
    section = fm.get("section", "Parliament")
    meta_line = f"{date} · {section} · {word_count_label}"
    head = INDEX_HEAD.format(
        title=html_escape(title) + " — Right to Read",
        description=html_escape(description),
        canonical=f"https://theright2read.org/writing/{slug}/",
        og_type="article",
        extra_meta=f'<meta property="article:published_time" content="{html_escape(date)}" />',
        asset_root="../../",
        asset_ver=ASSET_VER,
    )
    article = f"""
  <article class="section cream essay" id="essay-{slug}">
    <div class="essay-meta">{html_escape(meta_line)}</div>
    <h1 class="essay-h">{html_escape(title)}</h1>
    {f'<p class="essay-dek">{html_escape(dek)}</p>' if dek else ''}
    <div class="essay-body">
{body_html}
    </div>
  </article>
"""
    page = head + ESSAY_NAV + article + FOOT

    out_dir = WRITING / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    return {
        "slug": slug,
        "title": title,
        "date": date,
        "description": description,
        "dek": dek,
        "section": section,
        "word_count": word_count_label,
    }


def render_listing(posts: list[dict]) -> None:
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    cards = []
    for p in posts:
        cards.append(f"""
        <article class="essay-card">
          <div class="essay-card-meta">{html_escape(p['date'])} · {html_escape(p['section'])} · {html_escape(p['word_count'])}</div>
          <h3 class="essay-card-title"><a href="/writing/{html_escape(p['slug'])}/">{html_escape(p['title'])}</a></h3>
          <p class="essay-card-dek">{html_escape(p.get('dek') or p.get('description', ''))}</p>
          <a href="/writing/{html_escape(p['slug'])}/" class="essay-card-readmore">Read the essay →</a>
        </article>""")
    head = INDEX_HEAD.format(
        title="Writing — Right to Read",
        description="Long-form essays from the Free Libraries for All project.",
        canonical="https://theright2read.org/writing/",
        og_type="website",
        extra_meta="",
        asset_root="../",
        asset_ver=ASSET_VER,
    )
    body = f"""
{LISTING_NAV}
  <section class="section cream" id="writing-hero">
    <div class="def-stack">
      <div class="eyebrow">Writing</div>
      <h2>LONGER-FORM, <span class="red">SOURCED.</span></h2>
      <p class="lede">Essays from the Free Libraries for All project. Each one anchored in the underlying data on the <a href="/data/" style="text-decoration-color: var(--red);">data page</a> and in the historical record on the <a href="/inequality/" style="text-decoration-color: var(--red);">inequality page</a>.</p>
    </div>
  </section>
  <section class="section ink" id="writing-list">
    <div class="grain soft"></div>
    <div class="stack">
      <div class="essay-list">{''.join(cards)}
      </div>
    </div>
  </section>
"""
    (WRITING / "index.html").write_text(head + body + FOOT, encoding="utf-8")


def main() -> int:
    if not DRAFTS.exists():
        print(f"no drafts dir at {DRAFTS}", file=sys.stderr)
        return 1
    drafts = sorted(DRAFTS.glob("[0-9][0-9][0-9][0-9]-*.md"))
    if not drafts:
        print("no draft files matching YYYY-... pattern", file=sys.stderr)
        return 1
    posts = []
    for md in drafts:
        print(f"rendering {md.name}")
        meta = render_essay(md)
        posts.append(meta)
        print(f"  → writing/{meta['slug']}/index.html")
    render_listing(posts)
    print(f"\nrendered {len(posts)} essay(s); refreshed writing/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
