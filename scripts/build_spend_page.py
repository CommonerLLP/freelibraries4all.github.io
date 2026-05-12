#!/usr/bin/env python3
"""Build /spend/index.html — per-capita library expenditure report.

A self-contained static page for theright2read.org, building on
Kulkarni, Balaji & Dhanamjaya (2025) with two corrections and one
extension:

- Corrects the denominator from Census 2011 fixed to TG 2020 annual
  projections (MoHFW, July 2020, Table 11) — read directly from the
  primary PDF, no interpolation.
- Adjusts for inflation via the MoSPI implicit GDP deflator (NAS,
  base 2011-12) so we can report a real per-capita series alongside
  Balaji's nominal. GDP deflator is the standard in real
  government-spending analysis (IMF GFSM 2014, OECD, World Bank PER,
  RBI State Finances) — replaces an earlier CPI-IW (Labour Bureau)
  implementation.
- Extends state series through 2024-25 using either (a) state demand-
  for-grants documents where available (Assam, Goa, Rajasthan,
  Odisha) or (b) CAGR (2016-17 → 2020-21) extrapolation. CAG actuals
  for 2021-22 onwards are not yet published; this output is a
  forecast that must be reconciled when CAG releases land.

Methodology in full at:
  - In-page Methods section of /spend/
  - memory/verified_facts.md → "₹4.66 hero figure — methodology"

Voice: pamphlet register (cream/ink/red palette, Bebas Neue display +
Inter Tight body + JetBrains Mono eyebrows + Roboto Slab pull-quotes).
Inlined CSS + SVG; small in-page tooltip JS. Generated HTML carries
a DO-NOT-HAND-EDIT header.

Regenerate:
  python3 scripts/build_spend_page.py
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "spend", "index.html"))

# ── Data ──────────────────────────────────────────────────────────────────────

years_balaji  = ["2014-15","2015-16","2016-17","2017-18","2018-19","2019-20","2020-21"]
years_ext     = ["2021-22","2022-23","2023-24","2024-25"]
years_all     = years_balaji + years_ext

# Chart 1: National per capita — three scenarios, 2014-15 → 2024-25
# A: Nominal total / Census 2011 India population (fixed) — Balaji's method
# B: Nominal total / TG 2020 projected India population (annual July 1)
# C: Real (NAS GDP deflator, 2011-12 base) total / TG 2020 projected population
# Years 2021-25 are CAGR extrapolation (see Methods section in HTML).
nat_A = [5.16, 6.62, 8.62, 9.96, 11.64, 7.79, 8.39,  8.49, 8.66, 9.13, 9.51]
nat_B = [4.93, 6.25, 8.05, 9.19, 10.63, 7.04, 7.50,  7.51, 7.60, 7.94, 8.20]
# Real per-Indian per-year, base 2011-12 ₹, deflated by MoSPI NAS implicit
# GDP deflator (the standard for real government-spending analysis per
# IMF GFSM 2014, OECD, World Bank PER methodology, RBI State Finances).
# Year-by-year factors below; full provenance in /spend/ Methods.
nat_C = [4.16, 5.16, 6.44, 7.07,  7.87, 5.09, 5.17,  4.78, 4.57, 4.65, 4.66]
LAST_ACTUAL_IDX = 6  # 2020-21 — last CAG actual

# MoSPI NAS implicit GDP deflator factors (constant / current), base 2011-12.
# Latest revision per year: Third Revised 2014-15..2020-21, Second Revised
# 2021-22, Final 2022-23, First Revised 2023-24, Provisional 2024-25.
# Source: mospi.gov.in/national-accounts-statistics (queried 2026-05-12).
DEFLATOR_FACTOR = [0.8444, 0.8256, 0.7997, 0.7691, 0.7404,
                   0.7230, 0.6898, 0.6366, 0.6011, 0.5860, 0.5684]
# 2018-19 single-year factor — used for state and zone cross-sections
# (K-B-D's published base year).
DEFLATOR_2018_19 = 0.7404


def deflate_series(nominal_series):
    """Year-by-year deflation of an 11-element FY series (2014-15..2024-25)."""
    return [None if v is None else round(v * DEFLATOR_FACTOR[i], 2)
            for i, v in enumerate(nominal_series)]


def deflate_cross_2018(v):
    """Deflate a 2018-19 nominal per-capita figure to 2011-12 real ₹."""
    return round(v * DEFLATOR_2018_19, 2)

# Chart 2: State per capita 2018-19, nominal/TG (ranked low→high)
state_labels = ['Jharkhand','Bihar','Uttar Pradesh','Punjab','Madhya Pradesh',
                'Odisha','Chhattisgarh','Haryana','Rajasthan','Uttarakhand',
                'Nagaland','Delhi','Assam','Gujarat','Manipur','Tripura',
                'Meghalaya','Himachal Pradesh','Maharashtra','Jammu & Kashmir',
                'Telangana','Tamil Nadu','Mizoram','Sikkim','West Bengal',
                'Kerala','Andhra Pradesh','Karnataka','Arunachal Pradesh',
                'Puducherry','Goa']
# Nominal source values (K-B-D 2025, base 2018-19) kept here for audit.
# The arrays used everywhere downstream are the deflated real-terms versions.
state_vals_nominal = [0.14,0.36,0.94,0.98,1.09,1.22,1.26,1.48,1.49,1.79,3.33,4.31,
                      4.71,5.02,6.88,10.61,11.11,11.66,12.43,13.16,13.97,16.23,16.80,
                      19.68,19.69,24.67,24.74,35.23,48.02,50.61,118.76]
state_vals = [deflate_cross_2018(v) for v in state_vals_nominal]

# Chart 3: Regional averages 2018-19
region_labels = ['Central','North','East','North-East','South','West','Puducherry (UT)']
region_vals_nominal = [1.18, 4.48, 5.35, 15.14, 22.97, 45.40, 50.61]
region_vals = [deflate_cross_2018(v) for v in region_vals_nominal]

# Chart 4: Extended 4-state series — nominal (K-B-D + OBI extrapolation),
# then year-by-year deflation to 2011-12 real ₹.
ext_assam_nominal     = [3.99,3.42,3.72,5.20,4.71,4.70,4.92, 4.87,4.42,7.84,6.97]
ext_goa_nominal       = [66.52,90.59,96.69,113.23,118.76,130.42,132.00, None,163.38,245.19,284.17]
ext_rajasthan_nominal = [1.27,1.22,1.25,1.29,1.49,1.43,1.40, None,None,1.80,2.04]
ext_odisha_nominal    = [0.91,0.97,0.99,1.11,1.22,1.20,1.13, None,1.16,1.30,1.14]
ext_assam     = deflate_series(ext_assam_nominal)
ext_goa       = deflate_series(ext_goa_nominal)
ext_rajasthan = deflate_series(ext_rajasthan_nominal)
ext_odisha    = deflate_series(ext_odisha_nominal)

india_avg_2018 = deflate_cross_2018(10.63)   # = 7.87

# ── SVG visualisations for Section 2 ──────────────────────────────────────────

# State populations in millions (~2020 mid-year, from theright2read assets/data.js)
STATE_POP_MN = {
    "Andhra Pradesh": 53, "Arunachal Pradesh": 1.5, "Assam": 35, "Bihar": 124,
    "Chhattisgarh": 30, "Delhi": 19, "Goa": 1.7, "Gujarat": 67, "Haryana": 28,
    "Himachal Pradesh": 7.4, "Jammu & Kashmir": 14, "Jharkhand": 38,
    "Karnataka": 67, "Kerala": 36, "Madhya Pradesh": 85, "Maharashtra": 124,
    "Manipur": 3.2, "Meghalaya": 3.4, "Mizoram": 1.2, "Nagaland": 2.2,
    "Odisha": 46, "Puducherry": 1.5, "Punjab": 30, "Rajasthan": 80,
    "Sikkim": 0.7, "Tamil Nadu": 79, "Telangana": 38, "Tripura": 4.0,
    "Uttar Pradesh": 235, "Uttarakhand": 11, "West Bengal": 100,
}


def strip_plot_svg():
    """Bubble plot: 31 states+UTs on a log x-axis. Bubble area ∝ population.
    Colour = traffic-light gradient on per-capita library spend."""
    W, H = 1200, 460
    PAD_L, PAD_R = 90, 90
    Y_AXIS = 270
    LO, HI = 0.1, 200.0
    log_lo, log_hi = math.log10(LO), math.log10(HI)

    def x_of(v):
        return PAD_L + (math.log10(v) - log_lo) / (log_hi - log_lo) * (W - PAD_L - PAD_R)

    # bubble radius from sqrt(pop) — area ∝ population
    pops = [STATE_POP_MN.get(s, 5) for s in state_labels]
    max_pop = max(pops)
    min_r, max_r = 6, 42
    def r_of(pop):
        return min_r + (math.sqrt(pop) / math.sqrt(max_pop)) * (max_r - min_r)

    # traffic-light colour by value
    def col_of(v):
        if v < 2:   return "#c53030"   # deep red
        if v < 5:   return "#ed8936"   # orange
        if v < 15:  return "#ecc94b"   # yellow
        if v < 40:  return "#68d391"   # light green
        return "#2f855a"               # deep green

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Bubble chart: 31 Indian states by per-capita library expenditure 2018-19; bubble size proportional to population; colour green-to-red shows spend tier">']

    # title
    parts.append(f'<text x="0" y="22" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" letter-spacing="2" fill="#f1e8d3" opacity="0.75">31 STATES + UTs · BUBBLE = POPULATION · REAL ₹/PERSON · 2018-19 · 2011-12 ₹</text>')

    # baseline axis
    parts.append(f'<line x1="{PAD_L}" y1="{Y_AXIS}" x2="{W-PAD_R}" y2="{Y_AXIS}" stroke="#f1e8d3" stroke-width="2"/>')

    # tick marks
    for tick_v, label in [(0.1,"₹0.10"),(1,"₹1"),(10,"₹10"),(100,"₹100")]:
        tx = x_of(tick_v)
        parts.append(f'<line x1="{tx:.1f}" y1="{Y_AXIS-8}" x2="{tx:.1f}" y2="{Y_AXIS+8}" stroke="#f1e8d3" stroke-width="2"/>')
        parts.append(f'<text x="{tx:.1f}" y="{Y_AXIS+30}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="14" font-weight="700" fill="#f1e8d3">{label}</text>')

    # India avg dashed marker
    tx = x_of(india_avg_2018)
    parts.append(f'<line x1="{tx:.1f}" y1="40" x2="{tx:.1f}" y2="{Y_AXIS-50}" stroke="#dc2a14" stroke-dasharray="5 4" stroke-width="2"/>')
    parts.append(f'<text x="{tx:.1f}" y="36" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" letter-spacing="1" fill="#dc2a14">INDIA AVG ₹{india_avg_2018} · 2018-19 REAL</text>')

    # bubbles — draw in pop ascending order so big ones are on top of small ones at the same x
    indexed = sorted(range(len(state_labels)), key=lambda i: pops[i])
    for i in indexed:
        st, v = state_labels[i], state_vals[i]
        pop = pops[i]
        cx = x_of(v); r = r_of(pop); col = col_of(v)
        share = pop / sum(STATE_POP_MN.values()) * 100
        tt = f"{st}|₹{v:.2f} per capita|{pop:.1f}M people ({share:.1f}% of India)"
        parts.append(
            f'<circle class="bubble" cx="{cx:.1f}" cy="{Y_AXIS}" r="{r:.1f}" '
            f'fill="{col}" fill-opacity="0.78" stroke="#0e0e0e" stroke-width="1.5" '
            f'data-tip="{tt}"><title>{tt.replace("|", " · ")}</title></circle>'
        )

    # callouts for selected states (the politically important ones)
    callouts = [
        # (state, real-2018-19 value, x_offset_for_label, y_offset_for_label, anchor)
        ("UP",          0.70, 0,   -110, "middle"),
        ("Bihar",       0.27, 0,   -70,  "middle"),
        ("Jharkhand",   0.10, 0,   -30,  "middle"),
        ("MP",          0.81, 0,   80,   "middle"),
        ("Maharashtra", 9.20, 0,   70,   "middle"),
        ("Karnataka",  26.08, 0,   -50,  "middle"),
        ("Goa",        87.94, 0,   -30,  "middle"),
    ]
    for name, v, dx, dy, anchor in callouts:
        cx = x_of(v); pop = STATE_POP_MN.get(name if name not in ("UP","MP") else {"UP":"Uttar Pradesh","MP":"Madhya Pradesh"}[name], 5)
        r = r_of(pop)
        ty = Y_AXIS + dy
        # connecting line from bubble edge to label
        if dy < 0:
            line_y1 = Y_AXIS - r
            line_y2 = ty + 14
        else:
            line_y1 = Y_AXIS + r
            line_y2 = ty - 18
        parts.append(f'<line x1="{cx:.1f}" y1="{line_y1:.1f}" x2="{cx+dx:.1f}" y2="{line_y2:.1f}" stroke="#f1e8d3" stroke-width="1" stroke-dasharray="2 2" opacity="0.5"/>')
        parts.append(f'<text x="{cx+dx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-family="Bebas Neue" font-size="26" fill="#f1e8d3" letter-spacing="0.5">{name.upper()}</text>')
        parts.append(f'<text x="{cx+dx:.1f}" y="{ty+18:.1f}" text-anchor="{anchor}" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" fill="{col_of(v)}">₹{v:.2f} · {pop:.0f}M</text>')

    # Single unified legend strip.
    # Plain-English explainer in one line, then a row of colour swatches.
    # Size encoding is intentionally NOT given a separate legend — the chart
    # itself is the demonstration (UP's red bubble dominates everything else).
    legend_y = H - 50
    parts.append(
        f'<text x="{PAD_L}" y="{legend_y - 18}" '
        f'font-family="JetBrains Mono, monospace" font-size="12" '
        f'font-weight="700" letter-spacing="1.5" fill="#f1e8d3" opacity="0.85">'
        f'EACH ● = ONE STATE  ·  SIZE ∝ POPULATION  ·  COLOUR = ₹/PERSON TIER  ·  HOVER FOR DETAIL'
        f'</text>'
    )
    swatches = [
        ("#c53030", "₹0-2"),
        ("#ed8936", "₹2-5"),
        ("#ecc94b", "₹5-15"),
        ("#68d391", "₹15-40"),
        ("#2f855a", "₹40+"),
    ]
    sw_w = 80; sw_gap = 6
    total_w = len(swatches) * sw_w + (len(swatches) - 1) * sw_gap
    start_x = PAD_L
    for i, (col, lbl) in enumerate(swatches):
        sx = start_x + i * (sw_w + sw_gap)
        parts.append(f'<rect x="{sx}" y="{legend_y - 4}" width="{sw_w}" height="20" fill="{col}" stroke="#0e0e0e" stroke-width="1"/>')
        parts.append(f'<text x="{sx + sw_w/2:.0f}" y="{legend_y + 10}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" fill="#0e0e0e">{lbl}</text>')

    parts.append('</svg>')
    return "\n".join(parts)


def cess_sparklines_svg():
    """Five small sparklines, one per cess state, showing the volatility (or lack
    of it) over 2014-15 → 2020-21. Normalised per-row so each row's shape is
    independently readable."""
    cess_series = [
        ("Tamil Nadu",   1948, [7886, 8199, 9755,10750,12249,13604,13094]),
        ("Andhra Pradesh",1960,[4144, 4241, 7460,10126,12874,12989,10486]),
        ("Karnataka",    1965, [10107,9779,11161,11950,23055,12039, 7321]),
        ("West Bengal",  1979, [ 483,  491,17518,17743,19005,  421,14855]),
        ("Kerala",       1989, [1683, 5417, 4849, 8379, 8637, 3397, 2591]),
    ]
    ROWS = len(cess_series)
    ROW_H = 64
    W = 560
    H = ROW_H * ROWS + 44
    LABEL_W = 180
    SPARK_W = W - LABEL_W - 110
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Year-on-year volatility of MH 2205-105 expenditure in the five Indian states with library cess legislation">']
    # header labels
    parts.append(f'<text x="0" y="22" font-family="JetBrains Mono, monospace" font-size="14" font-weight="700" letter-spacing="2" fill="#f1e8d3">STATE · ACT</text>')
    parts.append(f'<text x="{LABEL_W}" y="22" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" letter-spacing="1.5" fill="#f1e8d3">2014-15 → 2020-21</text>')
    parts.append(f'<text x="{W}" y="22" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" letter-spacing="1.5" fill="#f1e8d3">MAX ÷ MIN</text>')

    for i, (name, act_year, vals) in enumerate(cess_series):
        y_top = 40 + i * ROW_H
        y_mid = y_top + ROW_H / 2
        # label block
        parts.append(f'<text x="0" y="{y_mid - 4}" font-family="Bebas Neue" font-size="28" fill="#f1e8d3">{name.upper()}</text>')
        parts.append(f'<text x="0" y="{y_mid + 18}" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" fill="#f1e8d3" opacity="0.65">CESS · {act_year}</text>')
        # sparkline normalised in this row's vertical band
        lo, hi = min(vals), max(vals)
        rng = hi - lo if hi > lo else 1
        spark_top = y_top + 10
        spark_bot = y_top + ROW_H - 12
        pts = []
        for j, v in enumerate(vals):
            x = LABEL_W + (j / (len(vals)-1)) * SPARK_W
            y = spark_bot - ((v - lo) / rng) * (spark_bot - spark_top)
            pts.append(f"{x:.1f},{y:.1f}")
        path = " ".join(pts)
        ratio = hi / lo if lo > 0 else 0
        col = "#dc2a14" if ratio > 5 else "#f1e8d3"
        # baseline rule
        parts.append(f'<line x1="{LABEL_W}" y1="{spark_bot}" x2="{LABEL_W+SPARK_W}" y2="{spark_bot}" stroke="#f1e8d3" stroke-opacity="0.2" stroke-width="1"/>')
        # the line itself
        parts.append(f'<polyline class="sparkline" points="{path}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"><title>{name} · {act_year} · expenditure range ₹{lo:,} – ₹{hi:,} lakh · max/min = {ratio:.0f}×</title></polyline>')
        years = ["2014-15","2015-16","2016-17","2017-18","2018-19","2019-20","2020-21"]
        for j, pt in enumerate(pts):
            x, y = pt.split(",")
            parts.append(f'<circle class="sparkdot" cx="{x}" cy="{y}" r="3.5" fill="{col}"><title>{name} · {years[j]} · ₹{vals[j]:,} lakh</title></circle>')
        # ratio label on the right — bigger
        parts.append(f'<text x="{W}" y="{y_mid + 8}" text-anchor="end" font-family="Bebas Neue" font-size="36" fill="{col}">{ratio:.0f}×</text>')

    parts.append('</svg>')
    return "\n".join(parts)


def goa_stack_svg():
    """The Goa-exception argument in three rows: the outlier itself, the
    inflated unweighted-state average that the press cites, and the honest
    population-weighted figure. Bars are linear-scaled; ₹ values are
    right-aligned in a fixed column so they never overlap the sub-labels.

    Hindi-belt and Central averages live in Section 3 (region cards) — they
    don't belong in the Goa-exception panel because they aren't part of the
    same argument."""
    # Sub-text is provided as a 2-tuple now (line1, line2) so we control the
    # break point precisely — splitting at the natural · in the prose.
    rows = [
        ("GOA",                       87.94, ("1.6M people",                  "the outlier"),                        "#dc2a14"),
        ("AVERAGE OF STATE AVERAGES", 11.33, ("What the press cites",          "Goa weighs as much as UP"),          "#f1e8d3"),
        ("PER INDIAN",                 7.87, ("2018-19 real · what India spends", "weighted by population"),         "#f1e8d3"),
    ]
    W = 720
    ROW_H = 132
    H = ROW_H * len(rows) + 32
    LABEL_W = 340
    VAL_X = W - 12
    VAL_RESERVED = 120
    BAR_X = LABEL_W
    BAR_MAX_W = W - LABEL_W - VAL_RESERVED
    MAX_V = 130
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Goa per-capita library expenditure compared with two ways of averaging national figures">']
    for i, (label, v, sub_pair, col) in enumerate(rows):
        sub1, sub2 = sub_pair
        y_top = 16 + i * ROW_H
        y_mid = y_top + ROW_H / 2
        # Main display label
        parts.append(f'<text x="0" y="{y_mid - 26}" font-family="Bebas Neue" font-size="36" fill="#f1e8d3">{label}</text>')
        # Sub-text on TWO lines, each bigger than before
        parts.append(f'<text x="0" y="{y_mid + 6}"  font-family="JetBrains Mono, monospace" font-size="16" font-weight="500" fill="#f1e8d3" opacity="0.75" letter-spacing="0.5">{sub1}</text>')
        parts.append(f'<text x="0" y="{y_mid + 28}" font-family="JetBrains Mono, monospace" font-size="16" font-weight="500" fill="#f1e8d3" opacity="0.75" letter-spacing="0.5">{sub2}</text>')
        bar_len = (v / MAX_V) * BAR_MAX_W
        parts.append(f'<rect class="zonebar" x="{BAR_X}" y="{y_mid - 26}" width="{bar_len:.1f}" height="52" fill="{col}" rx="2"><title>{label} · ₹{v:.2f} per Indian · {sub1} · {sub2}</title></rect>')
        parts.append(f'<text x="{VAL_X}" y="{y_mid + 14}" text-anchor="end" font-family="Bebas Neue" font-size="50" fill="{col}">₹{v:.2f}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


# ── Zone classifications ──────────────────────────────────────────────────────
# MHA Zonal Councils (1956) — non-overlapping. Sikkim was transferred from the
# Eastern ZC to the NEC by the North Eastern Council (Amendment) Act, 2002.
MHA_ZONE = {
    "Haryana":"Northern","Himachal Pradesh":"Northern","Jammu & Kashmir":"Northern",
    "Punjab":"Northern","Rajasthan":"Northern","Delhi":"Northern","Chandigarh":"Northern",
    "Chhattisgarh":"Central","Uttarakhand":"Central","Uttar Pradesh":"Central","Madhya Pradesh":"Central",
    "Bihar":"Eastern","Jharkhand":"Eastern","Odisha":"Eastern","West Bengal":"Eastern",
    "Goa":"Western","Gujarat":"Western","Maharashtra":"Western",
    "Dadra and Nagar Haveli":"Western","Daman and Diu":"Western",
    "Andhra Pradesh":"Southern","Karnataka":"Southern","Kerala":"Southern","Tamil Nadu":"Southern",
    "Puducherry":"Southern","Telangana":"Southern","Lakshadweep":"Southern",
    "Arunachal Pradesh":"NEC","Assam":"NEC","Manipur":"NEC","Meghalaya":"NEC",
    "Mizoram":"NEC","Nagaland":"NEC","Tripura":"NEC","Sikkim":"NEC",
    "Andaman & Nicobar":"None",
}

# MoC Cultural Zones (1985) — OVERLAPPING. For each state, primary = first
# ZCC in Wikipedia listing order (N → NC → E → NE → S → SC → W). All zones
# listed in MOC_ALL for multi-zone states.
MOC_PRIMARY = {
    "Chandigarh":"N","Haryana":"N","Himachal Pradesh":"N","Jammu & Kashmir":"N",
    "Punjab":"N","Rajasthan":"N","Uttarakhand":"N",
    "Bihar":"NC","Delhi":"NC","Madhya Pradesh":"NC","Uttar Pradesh":"NC",
    "Andaman & Nicobar":"E","Assam":"E","Jharkhand":"E","Manipur":"E",
    "Odisha":"E","Sikkim":"E","Tripura":"E","West Bengal":"E",
    "Arunachal Pradesh":"NE","Meghalaya":"NE","Mizoram":"NE","Nagaland":"NE",
    "Andhra Pradesh":"S","Karnataka":"S","Kerala":"S","Lakshadweep":"S",
    "Puducherry":"S","Tamil Nadu":"S","Telangana":"S",
    "Chhattisgarh":"SC","Goa":"SC","Maharashtra":"SC",
    "Dadra and Nagar Haveli":"W","Daman and Diu":"W","Gujarat":"W",
}
MOC_ALL = {  # full zone memberships for hover-tooltip and overlap indication
    "Chandigarh":["N"],"Haryana":["N","NC"],"Himachal Pradesh":["N"],"Jammu & Kashmir":["N"],
    "Punjab":["N"],"Rajasthan":["N","NC","W"],"Uttarakhand":["N","NC"],
    "Bihar":["NC","E"],"Delhi":["NC"],"Madhya Pradesh":["NC","SC"],"Uttar Pradesh":["NC"],
    "Andaman & Nicobar":["E","S"],"Assam":["E","NE"],"Jharkhand":["E"],"Manipur":["E","NE"],
    "Odisha":["E"],"Sikkim":["E","NE"],"Tripura":["E","NE"],"West Bengal":["E"],
    "Arunachal Pradesh":["NE"],"Meghalaya":["NE"],"Mizoram":["NE"],"Nagaland":["NE"],
    "Andhra Pradesh":["S","SC"],"Karnataka":["S","SC"],"Kerala":["S"],"Lakshadweep":["S"],
    "Puducherry":["S"],"Tamil Nadu":["S"],"Telangana":["S","SC"],
    "Chhattisgarh":["SC"],"Goa":["SC","W"],"Maharashtra":["SC"],
    "Dadra and Nagar Haveli":["W"],"Daman and Diu":["W"],"Gujarat":["W"],
}

# Per-zone metadata: (display name, hex color, avg per-capita, population_M, share_of_india_pct).
# Pure traffic-light ramp: deep-red (lowest avg) → orange → yellow → light-green → green → forest.
# 6 stops for MHA; 7 stops for MoC. Both span the same red→green gradient.
# Zone avg per-capita: 2018-19 K-B-D nominal × 0.7404 (NAS GDP deflator).
MHA_ZONE_META = {
    "Central":   ("CENTRAL ZC",  "#c53030",  0.94, 361, 27),    # nom 1.27
    "Eastern":   ("EASTERN ZC",  "#e8633f",  3.96, 308, 23),    # nom 5.35
    "Northern":  ("NORTHERN ZC", "#ecc94b",  4.08, 180, 13),    # nom 5.51
    "NEC":       ("NE COUNCIL",  "#a3c265", 11.21,  50,  4),    # nom 15.14
    "Southern":  ("SOUTHERN ZC", "#68d391", 20.42, 274, 20),    # nom 27.58
    "Western":   ("WESTERN ZC",  "#2f855a", 33.61, 193, 14),    # nom 45.40
    "None":      ("UNGROUPED",   "#94908a", None,  None, None),
}
MOC_ZONE_META = {
    "NC": ("NORTH CENTRAL", "#c53030",  1.21, 584, 41),    # nom 1.64
    "N":  ("NORTH",         "#e8633f",  3.77, 174, 13),    # nom 5.09
    "E":  ("EAST",          "#ed8936",  5.86, 351, 26),    # nom 7.91
    "NE": ("NORTH EAST",    "#ecc94b", 11.21,  50,  4),    # nom 15.14
    "S":  ("SOUTH",         "#a3c265", 20.42, 275, 20),    # nom 27.58
    "SC": ("SOUTH CENTRAL", "#68d391", 21.95, 399, 29),    # nom 29.64
    "W":  ("WEST",          "#2f855a", 25.49, 273, 20),    # nom 34.43
}


def _invert_zone_map(zone_map):
    """state → zone  ⇒  zone → [states]"""
    out = {}
    for state, zk in zone_map.items():
        out.setdefault(zk, []).append(state)
    return out

def _invert_all_zones(all_zones):
    """state → [zones]  ⇒  zone → [states (all members, even multi-zone)]"""
    out = {}
    for state, zks in all_zones.items():
        for zk in zks:
            out.setdefault(zk, []).append(state)
    return out

MHA_ZONE_MEMBERS = _invert_zone_map(MHA_ZONE)
MOC_ZONE_MEMBERS = _invert_all_zones(MOC_ALL)


def zone_bubble_chart_svg(zone_map, all_zones_map, zone_meta, title, sub, show_overlap=False, zone_members=None):
    """Zone-level bubble chart. One bubble per zone (6 for MHA, 7 for MoC).

    X-position = zone's average per-capita library spend (log scale).
    Bubble area = zone's share of India's population (which sums to >100% for
    MoC because of overlapping memberships — noted in caption).
    Colour = traffic-light by per-capita (red → green) from zone_meta.

    zone_members: dict of zone_key → [list of member state names], used to
    populate the hover tooltip with the actual list of states in each zone.

    zone_map / all_zones_map are state-level inputs kept for API parity with
    the earlier state-level chart; unused here.
    """
    _ = zone_map, all_zones_map  # unused; preserved for backwards compatibility
    zone_members = zone_members or {}
    W, H = 960, 460
    PAD_L, PAD_R, PAD_T, PAD_B = 60, 60, 100, 70
    Y_AXIS = PAD_T + (H - PAD_T - PAD_B) / 2
    # Range tightened — zone averages cluster ₹1-50
    LO, HI = 0.7, 70.0
    log_lo, log_hi = math.log10(LO), math.log10(HI)
    def x_of(v):
        return PAD_L + (math.log10(v) - log_lo) / (log_hi - log_lo) * (W - PAD_L - PAD_R)

    # Bubble radius: AREA proportional to share-of-India.
    # CRITICAL: max_share is GLOBAL across MHA + MoC, not per-chart,
    # so the MoC North Central bubble (41%) reads as visibly bigger than
    # the MHA Central bubble (27%). Without this, both charts' largest
    # bubble drew at max_r — the cross-chart comparison was broken.
    # Truly area-proportional: r = k * sqrt(share). No min_r offset (that
    # would compress the dynamic range and make 41% look like 1.34× the
    # area of 27% when the true ratio is 1.52×).
    all_shares = (
        [v[4] for v in MHA_ZONE_META.values() if v[4] is not None] +
        [v[4] for v in MOC_ZONE_META.values() if v[4] is not None]
    )
    max_share = max(all_shares)
    R_AT_MAX = 80     # max bubble radius in viewBox units
    R_AT_MIN_FLOOR = 14  # readability floor for the smallest zone (NEC ~4%)
    def r_of(share_pct):
        r = math.sqrt(share_pct) / math.sqrt(max_share) * R_AT_MAX
        return max(r, R_AT_MIN_FLOOR)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{title}">']
    parts.append('<defs><pattern id="multizone-bbl" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="rgba(14,14,14,0.50)" stroke-width="1.6"/></pattern></defs>')

    # header
    parts.append(f'<text x="0" y="22" font-family="JetBrains Mono, monospace" font-size="14" font-weight="700" letter-spacing="2" fill="#f1e8d3" opacity="0.75">{sub}</text>')
    parts.append(f'<text x="0" y="58" font-family="Bebas Neue" font-size="34" fill="#f1e8d3" letter-spacing="0.5">{title}</text>')

    # axis baseline + ticks (only show ticks within the tightened range)
    parts.append(f'<line x1="{PAD_L}" y1="{Y_AXIS}" x2="{W-PAD_R}" y2="{Y_AXIS}" stroke="#f1e8d3" stroke-width="2"/>')
    for tick_v, label in [(1,"₹1"),(2,"₹2"),(5,"₹5"),(10,"₹10"),(20,"₹20"),(50,"₹50")]:
        tx = x_of(tick_v)
        parts.append(f'<line x1="{tx:.1f}" y1="{Y_AXIS-7}" x2="{tx:.1f}" y2="{Y_AXIS+7}" stroke="#f1e8d3" stroke-width="2"/>')
        parts.append(f'<text x="{tx:.1f}" y="{Y_AXIS+28}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="14" font-weight="700" fill="#f1e8d3">{label}</text>')

    # India avg marker (₹7.87)
    tx = x_of(india_avg_2018)
    parts.append(f'<line x1="{tx:.1f}" y1="{PAD_T - 8}" x2="{tx:.1f}" y2="{H - PAD_B + 12}" stroke="#f1e8d3" stroke-dasharray="4 4" stroke-width="1.2" opacity="0.45"/>')
    parts.append(f'<text x="{tx:.1f}" y="{PAD_T - 12}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" letter-spacing="1" fill="#f1e8d3" opacity="0.85">INDIA AVG ₹{india_avg_2018} · 2018-19 REAL</text>')

    # Zone bubbles — sorted by avg ascending so colour reads red→green left-to-right
    sorted_zones = sorted(
        [(k, v) for k, v in zone_meta.items() if v[2] is not None],
        key=lambda kv: kv[1][2]
    )
    # Alternate label position above/below the axis to avoid overlap
    for i, (zk, (name, color, avg, pop_m, share_pct)) in enumerate(sorted_zones):
        cx = x_of(avg)
        r = r_of(share_pct)
        label_above = (i % 2 == 0)
        # Native browser tooltip: name + ₹/person + population + member states
        members = zone_members.get(zk, [])
        n_members = len(members)
        states_str = ", ".join(members) if members else "—"
        tt_parts = [
            name,
            f"₹{avg:.2f} per Indian per year on libraries",
            f"{pop_m}M people · {share_pct}% of India",
            f"{n_members} state{'s' if n_members != 1 else ''}: {states_str}",
        ]
        if show_overlap:
            multi_count = sum(1 for s in members if len(MOC_ALL.get(s, [])) > 1)
            if multi_count:
                tt_parts.append(f"{multi_count} of these also belong to another MoC zone")
        tt = "|".join(tt_parts)
        parts.append(
            f'<circle class="bubble" cx="{cx:.1f}" cy="{Y_AXIS}" r="{r:.1f}" '
            f'fill="{color}" fill-opacity="0.85" stroke="#0e0e0e" stroke-width="1.5" '
            f'data-tip="{tt}"><title>{tt.replace("|", " · ")}</title></circle>'
        )
        if show_overlap:
            parts.append(f'<circle cx="{cx:.1f}" cy="{Y_AXIS}" r="{r:.1f}" fill="url(#multizone-bbl)" stroke="none" pointer-events="none"/>')
        # Label group: zone name + value, alternating above/below
        if label_above:
            ly_name = Y_AXIS - r - 24
            ly_val  = Y_AXIS - r - 6
        else:
            ly_name = Y_AXIS + r + 22
            ly_val  = Y_AXIS + r + 40
        parts.append(f'<text x="{cx:.1f}" y="{ly_name:.1f}" text-anchor="middle" font-family="Bebas Neue" font-size="22" fill="#f1e8d3" letter-spacing="0.5">{name}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{ly_val:.1f}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" font-weight="700" fill="{color}">₹{avg:.2f} · {share_pct}%</text>')

    # Note if overlapping classification
    if show_overlap:
        parts.append(f'<text x="0" y="{H - 14}" font-family="JetBrains Mono, monospace" font-size="11" font-weight="500" letter-spacing="0.5" fill="#f1e8d3" opacity="0.7">HATCHED FILL · OVERLAPPING ZONES · TOTAL POPULATION SHARE &gt; 100% (states counted in multiple zones)</text>')

    parts.append('</svg>')
    return "\n".join(parts)


def zone_bars_svg(title, sub, zones, max_v=50, on_ink=True):
    """Horizontal bar chart of zonal library averages.
    zones: list of (name, avg, meta_text, is_highlight).
    """
    fg = "#f1e8d3" if on_ink else "#0e0e0e"
    muted = "rgba(241,232,211,0.65)" if on_ink else "rgba(14,14,14,0.55)"
    rule = "rgba(241,232,211,0.18)" if on_ink else "rgba(14,14,14,0.18)"
    W = 760
    ROW_H = 56
    PAD_TOP = 60
    H = PAD_TOP + ROW_H * len(zones) + 24
    LABEL_W = 220
    BAR_X = LABEL_W + 10
    BAR_MAX_W = W - BAR_X - 110
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{title}">']
    # title block
    parts.append(f'<text x="0" y="16" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="{fg}" opacity="0.6">{sub}</text>')
    parts.append(f'<text x="0" y="42" font-family="Bebas Neue" font-size="28" fill="{fg}" letter-spacing="0.5">{title}</text>')
    for i, (name, avg, meta, hi) in enumerate(zones):
        y_top = PAD_TOP + i * ROW_H
        y_mid = y_top + ROW_H/2
        bar_color = "#dc2a14" if hi else (fg if avg >= 10 else "#8a3a2c")
        # label
        parts.append(f'<text x="0" y="{y_mid - 4}" font-family="Bebas Neue" font-size="20" fill="{fg}">{name}</text>')
        parts.append(f'<text x="0" y="{y_mid + 12}" font-family="JetBrains Mono, monospace" font-size="10" fill="{muted}" letter-spacing="1">{meta}</text>')
        # baseline rule
        parts.append(f'<line x1="{BAR_X}" y1="{y_mid+18}" x2="{BAR_X+BAR_MAX_W}" y2="{y_mid+18}" stroke="{rule}" stroke-width="1"/>')
        # bar
        bar_len = min(avg / max_v, 1.0) * BAR_MAX_W
        parts.append(f'<rect class="zonebar" x="{BAR_X}" y="{y_mid - 12}" width="{bar_len:.1f}" height="24" fill="{bar_color}" rx="1"><title>{name} · ₹{avg:.2f} per capita · {meta}</title></rect>')
        # value
        tx = BAR_X + bar_len + 8
        parts.append(f'<text x="{tx:.1f}" y="{y_mid + 6}" font-family="Bebas Neue" font-size="26" fill="{bar_color}">₹{avg:.2f}</text>')
        if hi:
            parts.append(f'<text x="{W}" y="{y_mid - 4}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="1.5" fill="#dc2a14">← LOWEST</text>')
    parts.append('</svg>')
    return "\n".join(parts)


# MHA vs MoC: drop North-East and South — those groupings are nearly identical
# across the two classifications (same 8 NE states; same 5 southern states + Puducherry).
# Show only where the two State maps diverge.
MHA_ZONES = [
    ("CENTRAL ZC",    1.27, "UP · MP · Chhattisgarh · Uttarakhand · ~361M (27%)",  True),
    ("EASTERN ZC",    5.35, "Bihar · Jharkhand · Odisha · WB · ~308M (23%)",        False),
    ("NORTHERN ZC",   5.51, "Punjab · Haryana · Rajasthan · Delhi · HP · J&K · ~180M (13%)", False),
    ("WESTERN ZC",   45.40, "Gujarat · Maharashtra · Goa · ~193M (14%)",            False),
]
MOC_ZONES = [
    ("NORTH CENTRAL", 1.64,  "Bihar · Delhi · Haryana · MP · Raj · UP · Uttarakhand · ~584M (41%)", True),
    ("NORTH",         5.09,  "Haryana · HP · J&K · Punjab · Raj · Uttarakhand + UTs · ~174M",      False),
    ("EAST",          7.91,  "9 incl. WB · Bihar · Jharkhand · Odisha · Assam · ~351M",            False),
    ("SOUTH CENTRAL",29.64,  "AP · Chhattisgarh · Goa · Karnataka · MP · Maha · Telangana · ~399M", False),
    ("WEST",         34.43,  "Goa · Gujarat · Maharashtra · Rajasthan + UTs · ~273M",              False),
]

MHA_BARS_SVG = zone_bars_svg(
    "MHA ZONAL COUNCILS",
    "MINISTRY OF HOME AFFAIRS · 1956 · ADMINISTRATIVE · NON-OVERLAPPING",
    MHA_ZONES, max_v=50, on_ink=True)

MOC_BARS_SVG = zone_bars_svg(
    "MoC CULTURAL ZONES",
    "MINISTRY OF CULTURE · 1985 · ZONAL CULTURAL CENTRES · OVERLAPPING",
    MOC_ZONES, max_v=50, on_ink=True)

# Zone-coloured bubble charts (the new dual-chart for Section 4).
# Same bubble positions and sizes in both; only the colour grouping changes.
MHA_ALL = {state: [zone] for state, zone in MHA_ZONE.items()}

MHA_BUBBLES_SVG = zone_bubble_chart_svg(
    MHA_ZONE, MHA_ALL, MHA_ZONE_META,
    "MHA ZONAL COUNCILS",
    "MINISTRY OF HOME AFFAIRS · 1956 · NON-OVERLAPPING",
    show_overlap=False,
    zone_members=MHA_ZONE_MEMBERS)

MOC_BUBBLES_SVG = zone_bubble_chart_svg(
    MOC_PRIMARY, MOC_ALL, MOC_ZONE_META,
    "MoC CULTURAL ZONES",
    "MINISTRY OF CULTURE · 1985 · OVERLAPPING",
    show_overlap=True,
    zone_members=MOC_ZONE_MEMBERS)


def overlap_matrix_svg():
    """Small matrix showing the states that sit in multiple MoC cultural zones."""
    zones = ["NORTH", "N. CENTRAL", "EAST", "N. EAST", "SOUTH", "S. CENTRAL", "WEST"]
    rows = [
        ("Rajasthan",        [1,1,0,0,0,0,1]),
        ("Haryana",          [1,1,0,0,0,0,0]),
        ("Assam",            [0,0,1,1,0,0,0]),
        ("Manipur",          [0,0,1,1,0,0,0]),
        ("Tripura",          [0,0,1,1,0,0,0]),
        ("Andhra Pradesh",   [0,0,0,0,1,1,0]),
        ("Karnataka",        [0,0,0,0,1,1,0]),
        ("Telangana",        [0,0,0,0,1,1,0]),
        ("Goa",              [0,0,0,0,0,1,1]),
    ]
    fg = "#f1e8d3"
    muted = "rgba(241,232,211,0.55)"
    rule = "rgba(241,232,211,0.18)"
    LABEL_W = 160
    CELL_W = 78
    W = LABEL_W + CELL_W * len(zones) + 20
    HDR_H = 56
    ROW_H = 30
    H = HDR_H + ROW_H * len(rows) + 36
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="States sitting in multiple Ministry of Culture cultural zones">']
    parts.append(f'<text x="0" y="20" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="{fg}" opacity="0.6">STATES IN MULTIPLE CULTURAL ZONES · ● = MEMBER</text>')
    # column headers
    for j, zname in enumerate(zones):
        cx = LABEL_W + j * CELL_W + CELL_W/2
        parts.append(f'<text x="{cx}" y="{HDR_H - 8}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" font-weight="700" letter-spacing="1" fill="{fg}">{zname}</text>')
    # column separators
    for j in range(len(zones) + 1):
        x = LABEL_W + j * CELL_W
        parts.append(f'<line x1="{x}" y1="{HDR_H}" x2="{x}" y2="{HDR_H + ROW_H*len(rows)}" stroke="{rule}" stroke-width="1"/>')
    # rows
    for i, (state, mem) in enumerate(rows):
        y_top = HDR_H + i * ROW_H
        y_mid = y_top + ROW_H/2
        n_zones = sum(mem)
        state_color = "#dc2a14" if n_zones >= 3 else fg
        parts.append(f'<text x="{LABEL_W - 10}" y="{y_mid + 4}" text-anchor="end" font-family="Bebas Neue" font-size="18" fill="{state_color}">{state.upper()}</text>')
        parts.append(f'<line x1="0" y1="{y_top}" x2="{W}" y2="{y_top}" stroke="{rule}" stroke-width="1"/>')
        for j, has in enumerate(mem):
            if has:
                cx = LABEL_W + j * CELL_W + CELL_W/2
                col = "#dc2a14" if n_zones >= 3 else fg
                parts.append(f'<circle class="memdot" cx="{cx}" cy="{y_mid}" r="6" fill="{col}"><title>{state} is a member of {zones[j]} Cultural Zone (total: {n_zones} zones)</title></circle>')
        # count badge on the right
        parts.append(f'<text x="{W - 4}" y="{y_mid + 5}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="11" font-weight="700" fill="{state_color}">×{n_zones}</text>')
    # bottom rule
    parts.append(f'<line x1="0" y1="{HDR_H + ROW_H*len(rows)}" x2="{W}" y2="{HDR_H + ROW_H*len(rows)}" stroke="{rule}" stroke-width="1"/>')
    parts.append('</svg>')
    return "\n".join(parts)


OVERLAP_SVG = overlap_matrix_svg()

STRIP_PLOT_SVG = strip_plot_svg()
CESS_SPARKS_SVG = cess_sparklines_svg()
GOA_STACK_SVG = goa_stack_svg()

# ── HTML ──────────────────────────────────────────────────────────────────────

html = f"""<!DOCTYPE html>
<!-- DO NOT HAND-EDIT · generated by scripts/build_spend_page.py · regenerate with: python scripts/build_spend_page.py -->

<html lang="en-IN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What India spends on libraries — Right to Read</title>
<meta name="description" content="Per capita state expenditure on public libraries in India, 2014-2025. Extending and correcting Kulkarni, Balaji &amp; Dhanamjaya (2025) with updated population projections and CAGR-extrapolated state series through 2024-25.">

<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../assets/favicon-16.png">
<link rel="shortcut icon" href="../assets/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="../assets/apple-touch-icon.png">
<meta name="theme-color" content="#dc2a14">

<!-- Canonical + Open Graph + Twitter card for link unfurls -->
<link rel="canonical" href="https://theright2read.org/spend/" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Right to Read — The Right to Read" />
<meta property="og:url" content="https://theright2read.org/spend/" />
<meta property="og:title" content="What India spends on libraries — Right to Read" />
<meta property="og:description" content="₹4.66 per Indian per year, real terms (2011-12 ₹). Per-capita state expenditure on public libraries 2014-2025 — extending and correcting Kulkarni-Balaji-Dhanamjaya (2025) with TG 2020 population projections and the MoSPI GDP deflator." />
<meta property="og:locale" content="en_IN" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="What India spends on libraries — Right to Read" />
<meta name="twitter:description" content="₹4.66 per Indian per year, real terms. Per-capita state expenditure on public libraries 2014-2025." />
<meta property="og:image" content="https://theright2read.org/assets/og-image.png?v=2" />
<meta property="og:image:secure_url" content="https://theright2read.org/assets/og-image.png?v=2" />
<meta property="og:image:type" content="image/png" />
<meta property="og:image:width" content="1600" />
<meta property="og:image:height" content="838" />
<meta property="og:image:alt" content="Right to Read — The Right to Read. India spends ₹4.66 per Indian per year on every public library combined." />
<meta name="twitter:image" content="https://theright2read.org/assets/og-image.png?v=2" />
<meta name="twitter:image:alt" content="Right to Read — The Right to Read. India spends ₹4.66 per Indian per year on every public library combined." />

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Roboto+Slab:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<style>
:root {{
  --cream: #f1e8d3;
  --cream-deep: #e3d7b8;
  --ink: #0e0e0e;
  --ink-soft: #2a2a2a;
  --red: #dc2a14;
  --red-deep: #a31e0e;
  --blue: #1936a8;
  --grid-ink: rgba(14,14,14,0.10);
  --grid-cream: rgba(241,232,211,0.12);

  --f-display: 'Bebas Neue', Impact, sans-serif;
  --f-body: 'Inter Tight', 'Helvetica Neue', sans-serif;
  --f-slab: 'Roboto Slab', Georgia, serif;
  --f-mono: 'JetBrains Mono', monospace;
  --ls-eyebrow: 3px;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #0e0e0e; }}
body {{
  font-family: var(--f-body);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}

/* ── Page frame (pamphlet cap) ── */
.pamphlet {{
  width: 100%; max-width: 960px; margin: 0 auto;
  background: var(--cream);
}}

/* ── Strip (top metadata) ── */
.strip {{
  background: var(--ink); color: var(--cream);
  padding: 10px clamp(20px, 4vw, 56px);
  display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;
  font-family: var(--f-mono); font-size: 11px; letter-spacing: var(--ls-eyebrow);
  text-transform: uppercase; border-bottom: 4px solid var(--red);
}}
.strip .accent {{ color: var(--red); }}

/* ── Back-bar ── */
.backbar {{
  background: var(--cream);
  border-bottom: 2px solid var(--ink);
  padding: 14px clamp(20px, 4vw, 56px);
}}
.backbar a {{
  font-family: var(--f-mono); font-size: 12px; letter-spacing: 2px;
  text-transform: uppercase; font-weight: 700;
  color: var(--ink); text-decoration: none;
  border-bottom: 2px solid var(--red); padding-bottom: 2px;
}}
.backbar a + a {{ margin-left: 18px; }}
.backbar a:hover {{ color: var(--red); }}

/* ── Section base ── */
.section {{
  position: relative;
  padding: clamp(48px, 6vw, 88px) clamp(20px, 4vw, 56px);
  border-bottom: 4px solid var(--ink);
  overflow: hidden;
}}
.section.cream {{ background: var(--cream); color: var(--ink); }}
.section.ink   {{ background: var(--ink);   color: var(--cream); }}
.section.ink   {{ border-bottom-color: var(--red); }}
.stack {{ position: relative; z-index: 1; }}

/* Grain overlay for ink sections */
.grain {{
  position: absolute; inset: 0; pointer-events: none;
  mix-blend-mode: multiply; opacity: 0.4;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.18 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>");
  background-size: 200px 200px;
}}

/* ── Typography ── */
.eyebrow {{
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: var(--ls-eyebrow); text-transform: uppercase;
  font-weight: 700; opacity: 0.85;
  margin-bottom: 18px;
}}
.section.ink .eyebrow {{ color: var(--red); opacity: 1; }}
.section.cream .eyebrow {{ color: var(--red); }}

h1, h2 {{
  font-family: var(--f-display);
  font-weight: 400; letter-spacing: 0.5px;
  line-height: 0.95; text-transform: uppercase;
}}
h1 {{ font-size: clamp(48px, 9cqi, 110px); margin-bottom: 24px; }}
h2 {{ font-size: clamp(40px, 6.5cqi, 84px); margin-bottom: 28px; }}
.red {{ color: var(--red); }}

p.lede {{
  font-family: var(--f-slab);
  font-size: clamp(18px, 1.7vw, 21px); line-height: 1.55;
  max-width: 76ch; margin-bottom: 28px; font-weight: 400;
}}
p.body {{
  font-family: var(--f-body);
  font-size: 17px; line-height: 1.7;
  margin-bottom: 18px;
  /* No max-width: body prose flows to the section's natural content width.
     The section's clamp() padding caps how wide it can get. */
}}

/* Standalone question callout (used outside region-card / gen-card contexts) */
.question-block {{
  font-family: var(--f-slab);
  font-size: clamp(18px, 1.8vw, 22px); line-height: 1.5;
  max-width: 80ch;
  margin: 32px 0 8px;
  padding: 22px 26px;
  border-left: 8px solid var(--red);
  background: rgba(241, 232, 211, 0.06);
}}
.section.cream .question-block {{ background: var(--cream-deep); }}
.question-block::before {{
  content: "Question · ";
  display: block; margin-bottom: 10px;
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red);
}}
.section.ink p.lede, .section.ink p.body {{ color: var(--cream); }}
strong {{ font-weight: 700; }}
.section.ink strong {{ color: #ffd5cd; }}

.hero-inner {{ container-type: inline-size; }}

/* ── Stat boxes (three-up trend story) ── */
.stat-grid {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: clamp(12px, 1.5vw, 20px);
  margin: clamp(28px, 4vw, 44px) 0;
}}
.stat {{
  background: var(--cream-deep);
  border: 2px solid var(--ink); border-top: 8px solid var(--ink);
  padding: clamp(20px, 2.4vw, 30px);
  display: flex; flex-direction: column;
}}
.section.ink .stat {{
  background: var(--ink-soft); border-color: var(--cream);
  border-top-color: var(--cream); color: var(--cream);
}}
.stat.peak  {{ border-top-color: var(--red); }}
.stat.now   {{ border-top-color: var(--red); background: #fff; }}
.section.ink .stat.now {{ background: #1a1a1a; }}

.stat .yr {{
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: 2px; text-transform: uppercase;
  margin-bottom: 18px; opacity: 0.7;
}}
/* Real is PRIMARY: huge, red, top of card */
.stat .real-lbl {{
  font-family: var(--f-mono); font-size: 10px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); margin-bottom: 4px;
}}
.stat .real {{
  font-family: var(--f-display);
  font-size: clamp(72px, 8.5cqi, 110px);
  line-height: 0.9; color: var(--red);
  letter-spacing: 0.5px; margin-bottom: 6px;
}}
.stat .real-unit {{
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 1.5px; text-transform: uppercase;
  opacity: 0.65; margin-bottom: 22px;
}}
/* Nominal is SECONDARY: small, muted, below the rule */
.stat .nom-row {{
  border-top: 2px dashed var(--ink);
  padding-top: 14px;
  display: flex; align-items: baseline; gap: 10px;
}}
.section.ink .stat .nom-row {{ border-top-color: var(--cream); }}
.stat .nom {{
  font-family: var(--f-display); font-size: clamp(24px, 2.8cqi, 34px);
  line-height: 1; letter-spacing: 0.5px;
  opacity: 0.85;
}}
.stat .nom-lbl {{
  font-family: var(--f-mono); font-size: 10px;
  letter-spacing: 1.5px; text-transform: uppercase;
  opacity: 0.55;
}}
.stat .caption {{
  font-family: var(--f-body); font-size: 13px; line-height: 1.5;
  margin-top: auto; padding-top: 16px;
  font-style: italic; opacity: 0.85;
}}

/* ── Hero killer stat (one big number) ── */
.killer {{
  margin: clamp(32px, 5vw, 56px) 0 0;
  border-top: 4px solid var(--ink); border-bottom: 4px solid var(--ink);
  padding: clamp(24px, 4vw, 40px) 0;
  display: grid; grid-template-columns: 1fr 2fr;
  gap: clamp(20px, 3vw, 40px); align-items: center;
}}
.killer .label {{
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: 2px; text-transform: uppercase;
  margin-bottom: 6px;
}}
.killer .figure {{
  font-family: var(--f-display);
  font-size: clamp(96px, 18cqi, 220px); line-height: 0.85;
  color: var(--red);
}}
.killer .sub {{
  font-family: var(--f-slab); font-size: clamp(16px, 1.6vw, 20px);
  line-height: 1.5; max-width: 50ch;
}}
@media (max-width: 700px) {{
  .killer {{ grid-template-columns: 1fr; }}
}}

/* ── Chart wrappers ── */
.chart-wrap {{
  background: #fff;
  border: 2px solid var(--ink);
  padding: clamp(16px, 2vw, 24px);
  margin: clamp(20px, 3vw, 32px) 0 12px;
}}
.section.ink .chart-wrap {{
  background: #1a1a1a; border-color: var(--cream);
}}
.chart-canvas {{ position: relative; }}
.chart-caption {{
  font-family: var(--f-mono); font-size: 11px;
  line-height: 1.6; letter-spacing: 0.5px;
  opacity: 0.75; max-width: 80ch;
}}

/* ── Legend pills ── */
.legend {{
  display: flex; flex-wrap: wrap; gap: 10px;
  margin: 12px 0 0;
}}
.pill {{
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 1px; text-transform: uppercase;
  padding: 6px 12px;
  border: 2px solid var(--ink);
  background: var(--cream);
}}
.section.ink .pill {{ background: var(--ink-soft); border-color: var(--cream); color: var(--cream); }}
.pill .swatch {{ width: 14px; height: 4px; }}
.pill.dashed {{ border-style: dashed; }}

/* ── Callout box ── */
.callout {{
  margin: 28px 0;
  border-left: 8px solid var(--red);
  background: var(--cream-deep);
  padding: 22px 26px;
}}
.section.ink .callout {{ background: var(--ink-soft); color: var(--cream); }}
.callout p {{ font-family: var(--f-slab); font-size: 17px; line-height: 1.55; max-width: 70ch; }}

/* ── SVG interactivity ── */
svg .bubble {{
  transition: stroke-width 0.15s, fill-opacity 0.15s, filter 0.15s;
  cursor: pointer;
}}
svg .bubble:hover {{
  stroke-width: 4;
  stroke: var(--cream);
  fill-opacity: 1;
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.45));
}}
svg .zonebar {{ transition: fill-opacity 0.12s; cursor: pointer; }}
svg .zonebar:hover {{ fill-opacity: 0.75; }}
svg .sparkline {{ cursor: pointer; }}
svg .sparkdot {{ transition: r 0.12s; cursor: pointer; }}
svg .sparkdot:hover {{ r: 6; }}
svg .memdot {{ transition: r 0.12s; cursor: pointer; }}
svg .memdot:hover {{ r: 9; }}

/* ── Work-in-progress notice in footer ── */
.wip-notice {{
  font-family: var(--f-mono);
  font-size: 11px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--red);
  padding: 8px 12px;
  border: 1px dashed var(--red);
  display: inline-block;
  margin-bottom: 14px;
  white-space: nowrap;
}}
@media (max-width: 720px) {{
  .wip-notice {{ white-space: normal; max-width: 100%; }}
}}

/* ── GitHub repo link · matches the academiaindia/whoseuniversity.org
   footer pattern: inherits text colour, no decoration. Inline-flex
   with octicon at 1em (scales with surrounding text). */
.github-link {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  vertical-align: -0.12em;
  color: inherit;
  text-decoration: none;
}}
.github-link:hover {{ text-decoration: underline; }}
.github-link .github-icon {{
  width: 1em;
  height: 1em;
  flex: 0 0 auto;
  fill: currentColor;
}}

/* ── "Builds on" credit strip — tight, between hero and Section 1.
   Visible attribution without monumental scale. */
.builds-on {{
  background: var(--cream-deep);
  border-left: 6px solid var(--red);
  padding: 16px clamp(16px, 2.5vw, 24px);
  margin: 0;
}}
.builds-on .bo-eyebrow {{
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 1.8px; text-transform: uppercase;
  font-weight: 700; color: var(--red); margin-bottom: 10px;
}}
.builds-on .bo-row {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px 28px;
}}
.builds-on .bo-item .bo-who {{
  font-family: var(--f-slab); font-size: 14px; font-weight: 700;
  line-height: 1.3; margin-bottom: 2px;
}}
.builds-on .bo-item .bo-what {{
  font-family: var(--f-body); font-size: 13px; line-height: 1.5;
  color: var(--ink-soft);
}}
.builds-on .bo-item .bo-what a {{ color: var(--red); }}
@media (max-width: 720px) {{
  .builds-on .bo-row {{ grid-template-columns: 1fr; gap: 12px; }}
}}

/* ── Tooltip on hover for SVG bubbles & bars ── */
.tip {{
  position: fixed;
  display: none;
  pointer-events: none;
  z-index: 9999;
  background: var(--ink);
  color: var(--cream);
  border: 2px solid var(--red);
  padding: 10px 14px;
  font-family: var(--f-mono);
  font-size: 13px;
  line-height: 1.55;
  max-width: 360px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}}
.tip b {{
  font-family: var(--f-display);
  font-size: 20px;
  font-weight: 400;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 4px;
}}
.tip span {{ display: block; opacity: 0.92; }}

/* ── Focus indicators (a11y) ── */
a:focus-visible,
button:focus-visible {{
  outline: 3px solid var(--red);
  outline-offset: 3px;
}}
svg .bubble:focus-visible,
svg .zonebar:focus-visible,
svg .sparkdot:focus-visible,
svg .memdot:focus-visible {{
  outline: 3px solid var(--red);
  outline-offset: 2px;
  fill-opacity: 1;
}}

/* ── Skip link (a11y; matches the main pamphlet's pattern) ── */
.skip-link {{
  position: absolute; top: -100px; left: 8px; z-index: 2000;
  background: var(--ink); color: var(--cream);
  padding: 10px 18px;
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: 2px; text-transform: uppercase;
  text-decoration: none;
  border: 2px solid var(--red);
}}
.skip-link:focus {{ top: 8px; outline: 2px solid var(--red); outline-offset: 2px; }}

/* ── Dual-chart layout (Section 4: MHA vs MoC) — always stacked,
   so each chart gets the full container width for the log axis. */
.dual-charts {{
  display: flex; flex-direction: column;
  gap: clamp(20px, 3vw, 32px);
  margin: clamp(24px, 4vw, 36px) 0;
}}
.dual-chart {{
  border: 2px solid var(--cream);
  padding: clamp(16px, 2vw, 24px);
  background: var(--ink-soft);
}}
.dual-chart svg {{ width: 100%; height: auto; display: block; }}

.overlap-wrap {{
  border: 2px solid var(--cream);
  padding: clamp(16px, 2vw, 24px);
  background: var(--ink-soft);
  margin: clamp(20px, 3vw, 32px) 0;
}}
.overlap-wrap svg {{ width: 100%; height: auto; display: block; }}

/* ── Spread visuals (Section 2) ── */
.spread-strip {{
  background: var(--cream);
  border: 2px solid var(--cream); padding: clamp(16px, 2vw, 28px);
  margin: clamp(28px, 4vw, 40px) 0 8px;
}}
.spread-strip svg {{ width: 100%; height: auto; display: block; }}

.spread-panels {{
  display: grid; grid-template-columns: 1fr;
  gap: clamp(20px, 3vw, 36px);
  margin: clamp(28px, 4vw, 40px) 0;
}}
@media (min-width: 760px) {{
  .spread-panels {{ grid-template-columns: 1.15fr 1fr; }}
}}
.spread-panel {{
  border: 2px solid var(--cream);
  padding: clamp(20px, 2.5vw, 32px);
  display: flex; flex-direction: column;
}}
.spread-panel .p-label {{
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 2px; text-transform: uppercase;
  color: var(--red); font-weight: 700; margin-bottom: 6px;
}}
.spread-panel .p-title {{
  font-family: var(--f-display); font-size: clamp(32px, 3.8cqi, 44px);
  letter-spacing: 0.5px; line-height: 1; margin-bottom: 14px;
}}
.spread-panel .p-viz {{ margin: 8px 0 18px; }}
.spread-panel .p-viz svg {{ width: 100%; height: auto; display: block; }}
.spread-panel .p-text {{
  font-family: var(--f-body); font-size: 14px; line-height: 1.6;
  margin-bottom: 14px;
}}
.spread-panel .p-q {{
  font-family: var(--f-slab); font-size: 15px; line-height: 1.55;
  margin-top: auto; padding-top: 12px;
  border-top: 1px dashed currentColor;
}}
.spread-panel .p-q::before {{
  content: "Question · ";
  font-family: var(--f-mono); font-size: 10px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); display: block;
  margin-bottom: 6px;
}}

/* ── Region cards (Section 3) ── */
.region-grid {{
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: clamp(20px, 2.5vw, 32px);
  margin: clamp(28px, 4vw, 44px) 0;
}}
@media (max-width: 760px) {{ .region-grid {{ grid-template-columns: 1fr; }} }}
.region-card {{
  background: var(--cream-deep);
  border: 2px solid var(--ink);
  padding: clamp(22px, 2.6vw, 32px);
  display: flex; flex-direction: column;
}}
.section.ink .region-card {{ background: var(--ink-soft); border-color: var(--cream); color: var(--cream); }}
.region-card .reg-head {{
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 14px; margin-bottom: 4px;
  border-bottom: 2px solid var(--ink); padding-bottom: 14px;
}}
.section.ink .region-card .reg-head {{ border-bottom-color: var(--cream); }}
.region-card .reg-name {{
  font-family: var(--f-display); font-size: clamp(34px, 4cqi, 46px);
  letter-spacing: 0.5px; line-height: 1;
}}
.region-card .reg-meta {{
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 1.5px; text-transform: uppercase;
  text-align: right; opacity: 0.7; line-height: 1.5;
}}
.region-card .reg-avg {{
  font-family: var(--f-display); color: var(--red);
  font-size: clamp(24px, 2.5cqi, 32px); display: block;
}}
.region-card .reg-states {{
  list-style: none; margin: 18px 0 22px; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
}}
.region-card .reg-states li {{
  display: grid; grid-template-columns: 1fr auto;
  align-items: baseline; gap: 10px;
  font-family: var(--f-mono); font-size: 13px;
  padding: 5px 0; border-bottom: 1px dotted rgba(14,14,14,0.20);
}}
.section.ink .region-card .reg-states li {{ border-bottom-color: rgba(241,232,211,0.25); }}
.region-card .reg-states .st {{ font-weight: 500; }}
.region-card .reg-states .v  {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
.region-card .reg-states .v.low  {{ color: var(--red); }}
.region-card .reg-states .v.cess {{ font-style: italic; opacity: 0.75; }}
.region-card .reg-states .v.cess::after {{
  content: " · cess"; font-size: 10px; letter-spacing: 1px;
  text-transform: uppercase; opacity: 0.7;
}}
.region-card .question {{
  font-family: var(--f-slab); font-size: 16px; line-height: 1.55;
  margin-top: auto; padding-top: 4px;
}}
.region-card .question::before {{
  content: "Question · ";
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); display: block;
  margin-bottom: 8px;
}}

/* ── Law generation cards (Section 5) ── */
.gen-stack {{
  display: flex; flex-direction: column;
  gap: clamp(20px, 2.5vw, 28px);
  margin: clamp(28px, 4vw, 44px) 0;
}}
.gen-card {{
  border: 2px solid var(--ink);
  background: var(--cream);
  padding: clamp(22px, 2.6vw, 36px);
  position: relative;
}}
.section.ink .gen-card {{
  background: var(--ink-soft); border-color: var(--cream); color: var(--cream);
}}
.gen-card.gen-1 {{ border-left: 12px solid var(--red); }}
.gen-card.gen-2 {{ border-left: 12px solid #8a3a2c; }}
.gen-card.gen-3 {{ border-left: 12px solid #c8a37c; }}
.gen-card.gen-absent {{ border-left: 12px solid var(--ink); background: var(--ink); color: var(--cream); }}
.section.cream .gen-card.gen-absent {{ background: var(--ink); }}

.gen-head {{
  display: grid; grid-template-columns: 1fr auto;
  gap: 18px; align-items: baseline;
  padding-bottom: 14px; margin-bottom: 18px;
  border-bottom: 2px solid currentColor;
}}
.gen-head .label {{
  font-family: var(--f-mono); font-size: 12px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); margin-bottom: 4px;
}}
.gen-card.gen-absent .gen-head .label {{ color: #ffd5cd; }}
.gen-head .h3 {{
  font-family: var(--f-display); font-size: clamp(30px, 3.6cqi, 44px);
  letter-spacing: 0.5px; line-height: 1;
}}
.gen-head .meta {{
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 1.5px; text-transform: uppercase;
  text-align: right; opacity: 0.7; line-height: 1.5;
}}
.gen-head .meta .avg {{
  font-family: var(--f-display); font-size: clamp(24px, 2.4cqi, 32px);
  color: var(--red); display: block; line-height: 1; margin-bottom: 2px;
}}
.gen-card.gen-absent .gen-head .meta .avg {{ color: #ffd5cd; }}

.gen-states {{
  font-family: var(--f-mono); font-size: 12px; line-height: 1.9;
  margin-bottom: 18px;
}}
.gen-states .st-pill {{
  display: inline-block; padding: 3px 9px;
  border: 1px solid currentColor; margin-right: 6px; margin-bottom: 6px;
  white-space: nowrap;
}}
.gen-states .st-pill .yr {{ opacity: 0.6; margin-left: 4px; }}
.gen-states .st-pill .v  {{ margin-left: 8px; font-weight: 700; opacity: 0.85; }}
.gen-states .st-pill.low {{ background: var(--red); color: var(--cream); border-color: var(--red); }}

.gen-text {{
  font-family: var(--f-body); font-size: 15px; line-height: 1.65;
  max-width: 75ch;
}}
.gen-text + .gen-text {{ margin-top: 12px; }}
.gen-text strong {{ font-weight: 700; }}
.gen-question {{
  font-family: var(--f-slab); font-size: 16px; line-height: 1.55;
  margin-top: 16px; padding-top: 14px;
  border-top: 1px dashed currentColor; max-width: 75ch;
}}
.gen-question::before {{
  content: "Question · ";
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); display: block;
  margin-bottom: 8px;
}}
.gen-card.gen-absent .gen-question::before {{ color: #ffd5cd; }}

/* ── State trajectory cards (Section 4) ── */
.traj-grid {{
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: clamp(20px, 2.5vw, 32px);
  margin: clamp(28px, 4vw, 44px) 0;
}}
@media (max-width: 760px) {{ .traj-grid {{ grid-template-columns: 1fr; }} }}
.traj-card {{
  background: var(--ink-soft);
  border: 2px solid var(--cream); padding: clamp(22px, 2.6vw, 32px);
  color: var(--cream); display: flex; flex-direction: column;
}}
.section.cream .traj-card {{ background: var(--cream-deep); border-color: var(--ink); color: var(--ink); }}
.traj-card .st-name {{
  font-family: var(--f-display); font-size: clamp(36px, 4.4cqi, 52px);
  letter-spacing: 0.5px; line-height: 1; margin-bottom: 18px;
}}
.traj-line {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 12px; margin-bottom: 20px;
  border-top: 2px solid var(--cream); border-bottom: 2px solid var(--cream);
  padding: 16px 0;
}}
.section.cream .traj-line {{ border-top-color: var(--ink); border-bottom-color: var(--ink); }}
.traj-step .yr {{
  font-family: var(--f-mono); font-size: 10px;
  letter-spacing: 1.5px; text-transform: uppercase;
  opacity: 0.65; margin-bottom: 4px;
}}
.traj-step .val {{
  font-family: var(--f-display); font-size: clamp(28px, 3.5cqi, 40px);
  line-height: 1;
}}
.traj-step.now .val {{ color: var(--red); }}
.traj-step .tag {{
  font-family: var(--f-mono); font-size: 9px;
  letter-spacing: 1.5px; opacity: 0.6; margin-top: 4px;
}}
.traj-card .question {{
  font-family: var(--f-slab); font-size: 15px; line-height: 1.55;
  margin-top: auto;
}}
.traj-card .question::before {{
  content: "Question · ";
  font-family: var(--f-mono); font-size: 11px;
  letter-spacing: 2px; text-transform: uppercase;
  font-weight: 700; color: var(--red); display: block;
  margin-bottom: 8px;
}}

/* ── Methods table ── */
.methods table {{
  width: 100%; border-collapse: collapse;
  font-family: var(--f-mono); font-size: 12px;
  margin: 20px 0;
}}
.methods th, .methods td {{
  text-align: left; padding: 8px 10px;
  border-bottom: 1px solid var(--ink);
}}
.methods th {{
  background: var(--ink); color: var(--cream);
  font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}}
.methods tr.anom td {{ color: var(--red); }}
.methods td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.methods h3 {{
  font-family: var(--f-display); font-size: 32px; letter-spacing: 0.5px;
  text-transform: uppercase; margin: 24px 0 12px;
}}

/* Collapsible Methods block — keeps the long-form sources, deflator
   note, caveats, and per-state CAGR table out of the reader's path
   unless they ask. Matches the bib-collapse pattern from the homepage
   and data page: black-bordered button, mono uppercase label, red +/−
   marker, cream background. */
.bib-collapse {{
  margin-top: 24px;
}}
.bib-collapse > summary {{
  list-style: none;
  cursor: pointer;
  user-select: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 2px solid var(--ink);
  background: transparent;
  font-family: var(--f-mono); font-size: 11px; font-weight: 700;
  letter-spacing: 3px; text-transform: uppercase;
  color: var(--ink);
  transition: background 0.15s, color 0.15s;
}}
.bib-collapse > summary::-webkit-details-marker {{ display: none; }}
.bib-collapse > summary::after {{
  content: "+";
  font-family: var(--f-mono); font-size: 16px; font-weight: 700;
  color: var(--red); line-height: 1;
}}
.bib-collapse[open] > summary::after {{ content: "−"; }}
.bib-collapse > summary:hover,
.bib-collapse > summary:focus-visible {{
  background: var(--ink); color: var(--cream); outline: none;
}}
.bib-collapse > summary:hover::after,
.bib-collapse > summary:focus-visible::after {{ color: var(--cream); }}
.bib-collapse[open] > summary {{ margin-bottom: 24px; }}

/* ── Print button · matches the .print-btn on /, /data/, /inequality/.
   Placed in Section 7 (ink background) so we use cream-on-red instead
   of the default cream-on-ink, otherwise the button would blend into
   the background. ── */
.print-btn {{
  display: inline-block;
  margin-top: 32px;
  padding: 14px 26px;
  font-family: var(--f-mono); font-size: 13px;
  letter-spacing: 2px; text-transform: uppercase; font-weight: 700;
  color: var(--cream);
  background: var(--red);
  border: 2px solid var(--red);
  cursor: pointer;
  text-decoration: none;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}}
.print-btn:hover, .print-btn:focus {{
  background: var(--cream); color: var(--red); border-color: var(--cream);
}}
.print-btn:focus-visible {{
  outline: 3px solid var(--cream); outline-offset: 3px;
}}
.print-hint {{
  margin: 14px 0 0;
  font-family: var(--f-mono); font-size: 11px; letter-spacing: 1px;
  color: var(--cream-deep); line-height: 1.6;
  max-width: 640px;
}}

/* ── Footer (matches .page-footer on other pages: cream background,
   ink-soft text, WIP notice + colophon) ── */
footer {{
  background: var(--cream); color: var(--ink-soft);
  padding: 32px clamp(20px, 4vw, 56px) 48px;
  border-top: 2px solid var(--ink);
  font-family: var(--f-mono); font-size: 12px;
  line-height: 1.7;
}}
footer a {{ color: inherit; text-decoration: underline; text-underline-offset: 3px; }}
footer a:hover {{ color: var(--red); }}
footer .wip-notice {{
  color: var(--red); border-color: var(--red);
  margin-top: 8px; margin-bottom: 24px;
}}
footer .colophon-line {{
  margin-top: 12px; padding-top: 12px;
  color: var(--ink-soft); letter-spacing: 1px;
}}

/* ── Responsive ── */
@media (max-width: 700px) {{
  .stat-grid {{ grid-template-columns: 1fr; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* ── Print stylesheet · matches the pattern in assets/styles.css used
   by /, /data/, /inequality/. Renders A4 with chrome hidden, colours
   forced through, Methods <details> auto-opened so the PDF is a
   self-contained citable artefact. ── */
@media print {{
  @page {{
    size: A4;
    margin: 14mm 12mm 14mm;
  }}
  *, *::before, *::after {{
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    box-shadow: none !important;
    animation: none !important;
    transition: none !important;
  }}
  html, body {{
    background: var(--cream) !important;
    margin: 0; padding: 0;
    color: var(--ink) !important;
  }}
  .pamphlet {{
    max-width: 100% !important; width: 100% !important;
    background: var(--cream) !important;
  }}
  /* Hide on-screen chrome */
  .skip-link,
  .data-backbar,
  .strip,
  .actbar,
  .grain,
  .tip,
  .print-btn,
  .print-hint {{ display: none !important; }}
  /* Sections lose their stacked vertical padding to compress page count */
  .section {{
    padding: 14mm 0 8mm !important;
    background: var(--cream) !important;
    color: var(--ink) !important;
    border: none !important;
  }}
  .section.ink, .section.ink * {{
    background: var(--cream) !important;
    color: var(--ink) !important;
  }}
  .section.ink .eyebrow, .section.cream .eyebrow {{ color: var(--red) !important; }}
  .section.ink .red, .section.cream .red, .red {{ color: var(--red) !important; }}
  /* Methods section begins on a new physical page so readers who only
     want the analysis can print "pages 1-N" and skip the methodology
     appendix. */
  section.methods {{
    page-break-before: always !important;
    break-before: page !important;
  }}
  /* Methods <details> open in print so the PDF is self-contained */
  details.bib-collapse > summary {{ display: none; }}
  details.bib-collapse > *:not(summary) {{ display: block !important; }}
  /* Page-break hints */
  h1, h2 {{ page-break-after: avoid; break-after: avoid; }}
  h3 {{ page-break-after: avoid; break-after: avoid; }}
  .stat-grid, .killer, .traj-states-card, table {{
    page-break-inside: avoid; break-inside: avoid;
  }}
  /* SVG charts must scale to print width */
  svg {{ max-width: 100% !important; height: auto !important; }}
  /* Hide the footer-internal GitHub icon link target (still visible as text) */
  footer {{ border-top: 1px solid var(--ink) !important; padding-top: 8mm !important; }}
  footer .wip-notice {{ break-inside: avoid; page-break-inside: avoid; }}
}}
</style>
</head>
<body>

<a class="skip-link" href="#main-content">Skip to content</a>

<main class="pamphlet" id="main-content">

  <div class="strip">
    <span>Right to Read · The Data</span>
    <span class="accent">Per Capita Public Library Spend · 2014–2025</span>
  </div>

  <div class="backbar">
    <a href="/">← Back to the pamphlet</a>
    <a href="/data/">→ Other data</a>
  </div>

  <!-- ═══════════════════════════════ HERO -->
  <section class="section cream">
    <div class="stack hero-inner">
      <div class="eyebrow">Money · per person · per year</div>
      <h1>WHAT INDIA SPENDS<br>ON <span class="red">PUBLIC LIBRARIES.</span></h1>
      <p class="lede">
        Kulkarni, Balaji &amp; Dhanamjaya (2025) put the number at <strong>₹11.62 per Indian per year</strong>
        (nominal) for 2018-19 — the highest point on record. We re-ran their analysis with the government's
        own annual population projections (TG 2020) and the MoSPI implicit GDP deflator (NAS, base 2011-12).
        After those two corrections, and after extrapolating state-level CAG accounts through 2024-25, the
        real story is this:
      </p>

      <div class="killer">
        <div>
          <div class="label">India · 2024-25 · real terms (2011-12 ₹)</div>
          <div class="figure">₹4.66</div>
        </div>
        <div class="sub">
          per Indian, per year, on every public library in the country. Less than a local bus ticket.
          Less than what the State spends on a single one of its statue commissions. Lower than 2014-15.
        </div>
      </div>
    </div>
  </section>

  <!-- "Builds on" credit moved to Methods/Sources at the bottom — the
       three citations already live in <ol class="bib-list">, this strip
       was a duplicate. -->

  <!-- ═══════════════════════════════ SECTION 1: THE ARC -->
  <section class="section cream">
    <div class="stack">
      <div class="eyebrow">Section 1 · the arc</div>
      <h2>RISE, PEAK, <span class="red">RETREAT.</span></h2>
      <p class="lede">
        Between 2014-15 and 2018-19, state expenditure on public libraries (budget head MH 2205-105)
        nearly doubled in nominal terms. Adjusted with the MoSPI implicit GDP deflator (base 2011-12),
        the real-terms gain was modest but real: from <strong>₹4.16</strong> to <strong>₹7.87</strong>
        per Indian per year. From 2019-20 onwards, the line bends down — and according to the trend in
        the underlying CAG accounts, it has not bent back up. <strong class="t-red">By 2024-25, almost
        all the post-2014 real-terms gain has retreated.</strong>
      </p>

      <div class="stat-grid">
        <div class="stat">
          <div class="yr">2014-15 · start</div>
          <div class="real-lbl">Real · 2011-12 ₹</div>
          <div class="real">₹4.16</div>
          <div class="real-unit">per Indian, per year</div>
          <div class="nom-row">
            <span class="nom">₹4.93</span>
            <span class="nom-lbl">nominal</span>
          </div>
          <div class="caption">Where the decade started. CAG actual.</div>
        </div>
        <div class="stat peak">
          <div class="yr">2018-19 · peak</div>
          <div class="real-lbl">Real · 2011-12 ₹</div>
          <div class="real">₹7.87</div>
          <div class="real-unit">per Indian, per year</div>
          <div class="nom-row">
            <span class="nom">₹10.63</span>
            <span class="nom-lbl">nominal</span>
          </div>
          <div class="caption">Highest year on record. CAG actual.</div>
        </div>
        <div class="stat now">
          <div class="yr">2024-25 · estimate</div>
          <div class="real-lbl">Real · 2011-12 ₹</div>
          <div class="real">₹4.66</div>
          <div class="real-unit">per Indian, per year</div>
          <div class="nom-row">
            <span class="nom">₹8.20</span>
            <span class="nom-lbl">nominal</span>
          </div>
          <div class="caption">CAGR extrapolation. <strong>41% below 2018-19 peak.</strong></div>
        </div>
      </div>

      <div class="legend">
        <span class="pill"><span class="swatch" style="background:var(--ink)"></span>Nominal · Census 2011 fixed (Balaji et al.)</span>
        <span class="pill"><span class="swatch" style="background:var(--blue)"></span>Nominal · TG 2020 projected population</span>
        <span class="pill"><span class="swatch" style="background:var(--red)"></span>Real · 2011-12 prices · TG population</span>
        <span class="pill dashed"><span class="swatch" style="background:transparent; border-top:2px dashed var(--ink); height:0; width:18px;"></span>CAGR extrapolation 2021-25</span>
      </div>

      <div class="chart-wrap"><div class="chart-canvas" style="height:380px"><canvas id="chart1"></canvas></div></div>
      <p class="chart-caption">
        NATIONAL PER CAPITA EXPENDITURE ON PUBLIC LIBRARIES · ₹/PERSON/YEAR · INCLUDES UNION GOVT.
        SOLID = CAG ACTUALS (2014-21). DASHED = CAGR EXTRAPOLATION FROM 2021-22 (SEE METHODS).
        THE 2019-20 DROP IS DRIVEN BY WEST BENGAL CESS RECLASSIFICATION, NOT POLICY.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 2: THE SPREAD -->
  <section class="section ink">
    <div class="grain"></div>
    <div class="stack">
      <div class="eyebrow">Section 2 · the spread</div>
      <h2>FROM ₹0.10<br>TO <span class="red">₹87.94.</span></h2>
      <p class="lede">
        31 states and UTs across nearly four orders of magnitude. Jharkhand at one end.
        Goa at the other. The bottom half clusters near zero; the top is stretched thin.
        Read the strip below before the regional breakdown — and the two phenomena
        that distort everything that follows.
      </p>

      <div class="spread-strip">
        {STRIP_PLOT_SVG}
      </div>

      <div class="spread-panels">

        <!-- Cess Paradox panel -->
        <div class="spread-panel">
          <div class="p-label">The Cess Paradox</div>
          <div class="p-title">FIVE STATES,<br>FIVE TRAJECTORIES.</div>
          <div class="p-viz">{CESS_SPARKS_SVG}</div>
          <p class="p-text">
            Five states wrote library <em>cess</em> into their Public Libraries Acts —
            a small statutory levy, ring-fenced for libraries outside the annual budget.
            Tamil Nadu in 1948, before the Constitution. Kerala in 1989, just before
            liberalisation closed the door. <strong>Tamil Nadu's line is steady. The other
            four are not.</strong> West Bengal's expenditure jumps 35× between adjacent years.
            The cess does not stabilise library funding. It makes the line unreadable.
          </p>
          <div class="p-q">
            A cess is meant to make funding more secure, not less visible. What does
            it mean that the only states that took this protection seriously produce
            the data least amenable to public scrutiny?
          </div>
        </div>

        <!-- Goa Exception panel -->
        <div class="spread-panel">
          <div class="p-label">The Goa Exception</div>
          <div class="p-title">ONE STATE,<br>OFF THE SCALE.</div>
          <div class="p-viz">{GOA_STACK_SVG}</div>
          <p class="p-text">
            Goa has 1.6 million people — about one outer Mumbai suburb — tourist revenues
            that outpace its population, and a Portuguese inheritance in which libraries
            are civic ornament. The press cites the <strong>unweighted state average of
            ₹11.33</strong> as "India's library spend." Goa alone is what pulls that
            number above the population-weighted reality of ₹7.87 (2018-19 real, 2011-12 ₹).
          </p>
          <div class="p-q">
            Is Goa a model that can be scaled to a state of 230 million people whose
            CMs never visit a public library — or is the press using an artefact to
            make the rest of the country look better than it is?
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 3: THE STATE'S OWN MAP -->
  <section class="section cream">
    <div class="stack">
      <div class="eyebrow">Section 3 · MHA Zonal Councils (1956) + North-Eastern Council (1972)</div>
      <h2>THE STATE'S <span class="red">OWN MAP.</span></h2>
      <p class="lede">
        In 1956, Nehru proposed grouping the reorganised states into Zonal Councils —
        advisory bodies meant to "develop the habit of cooperative working" between
        linguistically and culturally adjacent States. The States Reorganisation Act,
        1956 set up five such Councils. The North Eastern Council was added by statute
        in 1972. <strong>These are the State's own regional categories.</strong>
        Read the library line against them and the picture sharpens — particularly in
        the Central zone, where the State has grouped its largest population block
        with its lowest library investment.
      </p>

      <div class="region-grid">

        <!-- CENTRAL ZONAL COUNCIL — highlighted, the key finding -->
        <div class="region-card" style="border-left: 12px solid var(--red); grid-column: 1 / -1;">
          <div class="reg-head">
            <div class="reg-name">CENTRAL ZONAL COUNCIL</div>
            <div class="reg-meta">4 states · ~361M people · <strong>26.5% of India</strong><br><span class="reg-avg">₹0.94</span> avg · <strong>every state below ₹2</strong></div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Uttar Pradesh</span><span class="v low">₹0.70</span></li>
            <li><span class="st">Madhya Pradesh</span><span class="v low">₹0.81</span></li>
            <li><span class="st">Chhattisgarh</span><span class="v low">₹0.93</span></li>
            <li><span class="st">Uttarakhand</span><span class="v low">₹1.33</span></li>
          </ul>
          <div class="question">
            The MHA grouped UP — the world's largest sub-national unit by population after China's
            provinces — with MP, Chhattisgarh, and Uttarakhand in its Central zone. Over a quarter
            of India lives here. Every single state spends less than <strong>₹2 per Indian per year</strong>
            on public libraries. When the State invokes "Bharat" against "India," it is invoking,
            geographically, this zone. What does it mean that the State's own Central zone is also
            its blank space on public reading?
          </div>
        </div>

        <!-- NORTHERN ZC -->
        <div class="region-card">
          <div class="reg-head">
            <div class="reg-name">NORTHERN ZC</div>
            <div class="reg-meta">6 states · ~180M people · 13%<br><span class="reg-avg">₹4.08</span> avg</div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Punjab</span><span class="v low">₹0.73</span></li>
            <li><span class="st">Haryana</span><span class="v low">₹1.10</span></li>
            <li><span class="st">Rajasthan</span><span class="v low">₹1.10</span></li>
            <li><span class="st">Delhi</span><span class="v">₹3.19</span></li>
            <li><span class="st">Himachal Pradesh</span><span class="v">₹8.63</span></li>
            <li><span class="st">Jammu &amp; Kashmir</span><span class="v">₹9.74</span></li>
          </ul>
          <div class="question">
            The MHA Northern Council groups Punjab — site of the Phulkian state libraries
            of the 1880s and the Singh Sabha reading-room movement — with HP and J&amp;K
            (princely-state library inheritances). Why has Punjab, with deeper pre-1947
            library infrastructure than either, fallen below <strong>₹1 per capita</strong>,
            while smaller HP and J&amp;K manage ₹11-13?
          </div>
        </div>

        <!-- EASTERN ZC -->
        <div class="region-card">
          <div class="reg-head">
            <div class="reg-name">EASTERN ZC</div>
            <div class="reg-meta">4 states · ~308M people · 23%<br><span class="reg-avg">₹3.96</span> avg · <strong>₹0.42 w/o WB</strong></div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Jharkhand</span><span class="v low">₹0.10</span></li>
            <li><span class="st">Bihar</span><span class="v low">₹0.27</span></li>
            <li><span class="st">Odisha</span><span class="v low">₹0.90</span></li>
            <li><span class="st">West Bengal</span><span class="v cess">₹14.58</span></li>
          </ul>
          <div class="question">
            The Eastern zone produced the Bengal Renaissance, the Brahmo Samaj reading rooms,
            Serampore's missionary press, the Bihar Vidyapith adult-literacy networks, and
            (geographically, before 1193) Nalanda. Strip West Bengal's cess-distorted figure
            and the zone averages <strong>₹0.42</strong>. What does it mean that the zone
            with India's deepest historical literacy traditions has its worst public-library
            budgets — and that the historical literacy itself came overwhelmingly from
            non-state institutions?
          </div>
        </div>

        <!-- WESTERN ZC -->
        <div class="region-card">
          <div class="reg-head">
            <div class="reg-name">WESTERN ZC</div>
            <div class="reg-meta">3 states · ~193M people · 14%<br><span class="reg-avg">₹33.61</span> avg · <strong>₹6.46 w/o Goa</strong></div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Gujarat</span><span class="v low">₹3.72</span></li>
            <li><span class="st">Maharashtra</span><span class="v">₹9.20</span></li>
            <li><span class="st">Goa</span><span class="v">₹87.94</span></li>
          </ul>
          <div class="question">
            Strip Goa and the West averages ₹6.46 — below the national figure. Gujarat at
            <strong>₹3.72</strong> — the state most loudly celebrated as India's development
            model — is half the corrected national average. The zone only looks "rich"
            because of one small ex-Portuguese coastal enclave. What is the development
            model, if it does not extend to libraries?
          </div>
        </div>

        <!-- SOUTHERN ZC -->
        <div class="region-card">
          <div class="reg-head">
            <div class="reg-name">SOUTHERN ZC</div>
            <div class="reg-meta">5 states + Puducherry · ~274M people · 20%<br><span class="reg-avg">₹20.42</span> avg · <strong>all cess-legislated</strong></div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Telangana</span><span class="v cess">₹10.34</span></li>
            <li><span class="st">Tamil Nadu</span><span class="v cess">₹12.02</span></li>
            <li><span class="st">Kerala</span><span class="v cess">₹18.26</span></li>
            <li><span class="st">Andhra Pradesh</span><span class="v cess">₹18.32</span></li>
            <li><span class="st">Karnataka</span><span class="v cess">₹26.08</span></li>
            <li><span class="st">Puducherry (UT)</span><span class="v">₹37.47</span></li>
          </ul>
          <div class="question">
            Every state in the Southern zone has — or inherits — Public Libraries Act
            legislation with cess provisions. TN 1948. AP 1960. Karnataka 1965.
            Kerala 1989. Telangana (AP-inherited; own Act 2015). Did the Dravidian /
            Self-Respect / Communist political traditions force the State to legislate
            public reading here in a way the Hindi belt never did — or are we mistaking
            the visibility of cess for the substance of investment?
          </div>
        </div>

        <!-- NORTH EASTERN COUNCIL -->
        <div class="region-card">
          <div class="reg-head">
            <div class="reg-name">NORTH EASTERN COUNCIL</div>
            <div class="reg-meta">8 states (incl. Sikkim, 2002) · ~50M · 3.7%<br><span class="reg-avg">₹11.21</span> avg · 12× Central</div>
          </div>
          <ul class="reg-states">
            <li><span class="st">Nagaland</span><span class="v">₹2.47</span></li>
            <li><span class="st">Assam</span><span class="v">₹3.49</span></li>
            <li><span class="st">Manipur</span><span class="v">₹5.09</span></li>
            <li><span class="st">Tripura</span><span class="v">₹7.85</span></li>
            <li><span class="st">Meghalaya</span><span class="v">₹8.23</span></li>
            <li><span class="st">Mizoram</span><span class="v">₹12.44</span></li>
            <li><span class="st">Sikkim</span><span class="v">₹14.57</span></li>
            <li><span class="st">Arunachal Pradesh</span><span class="v">₹35.56</span></li>
          </ul>
          <div class="question">
            The NEC was created in 1972 because the standard Zonal Councils could not handle
            the region's "special problems." Most member states operate under sixth-schedule
            or Article-371 fiscal arrangements — formally the most "dependent" region. And
            yet the NEC outspends the Central zone <strong>12 to 1</strong>. Arunachal alone
            (₹48) spends fifty times UP. What does that tell us about whether public
            libraries are produced by fiscal capacity, or by political choice?
          </div>
        </div>

      </div>

      <p class="body" style="margin-top:24px;">
        The MHA's own classification, read against its own budget data, produces a verdict
        the State does not advertise: the zone the Centre treats as most fiscally dependent
        (NEC) spends the most per capita on public libraries; the zone holding over a quarter
        of India (Central) spends the least. Read together with Section 5's legal-architecture
        breakdown — every Central-zone state is in the no-Act group — this is not coincidence.
        It is the residue of seventy-six years of legislative choice.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 4: TWO MAPS, ONE BUDGET LINE -->
  <section class="section ink">
    <div class="grain"></div>
    <div class="stack">
      <div class="eyebrow">Section 4 · MHA (1956) vs Ministry of Culture (1985)</div>
      <h2>TWO MAPS.<br>ONE <span class="red">BUDGET LINE.</span></h2>
      <p class="lede">
        The State of India has drawn its regional map twice. The Ministry of Home Affairs
        in 1956 grouped reorganised states into <strong>five non-overlapping Zonal Councils</strong>
        for administrative cooperation. The Ministry of Culture in 1985 drew <strong>seven
        overlapping Cultural Zones</strong> for "preserving and promoting" culture. Neither
        classification is neutral — each is a claim about what counts as a region of India.
        The charts below show <strong>one bubble per zone</strong> in each scheme: position
        is the zone's average ₹/person, area is the zone's population share. The leftmost
        red bubble — the underspend zone — stays red across both classifications.
      </p>

      <div class="dual-charts">
        <div class="dual-chart">{MHA_BUBBLES_SVG}</div>
        <div class="dual-chart">{MOC_BUBBLES_SVG}</div>
      </div>
      <p class="chart-caption">
        EACH BUBBLE = ONE ZONE · X-POSITION = ZONE'S AVG ₹/PERSON (LOG SCALE) ·
        BUBBLE AREA = ZONE'S SHARE OF INDIA'S POPULATION ·
        COLOUR = TRAFFIC-LIGHT BY AVG ₹ (RED = LOWEST, GREEN = HIGHEST) ·
        HATCHED ON RIGHT = MoC ZONES OVERLAP, SO MEMBER SHARES SUM &gt; 100% ·
        HOVER FOR ZONE DETAIL.
      </p>

      <p class="body" style="margin-top:18px;">
        On the left chart, the deep-red bubbles belong to the MHA's Central Zonal Council:
        UP, MP, Chhattisgarh, Uttarakhand — four states, <strong>~361 million people,
        27% of India</strong>, all under ₹2 per capita. On the right chart, those same
        four bubbles are still red, but they're now joined by Bihar, Delhi, Haryana, and
        Rajasthan: the MoC's North Central Cultural Zone, headquartered at
        Prayagraj (Allahabad), covering <strong>~584 million people, 41% of India</strong>.
        The classifications differ; the underspend doesn't.
      </p>

      <p class="body" style="margin-top:18px;">
        <strong>The MoC's North Central Cultural Zone — headquartered at Prayagraj (Allahabad) — captures
        the underspend even more widely than MHA Central.</strong> It pulls in Bihar (which MHA
        places in the East), Delhi (MHA: North), Haryana (MHA: North) and Rajasthan (MHA: North),
        on top of UP / MP / Uttarakhand. Result: <strong>~584 million people</strong>
        — 41% of India, headquartered at the Hindi belt's cultural capital — averaging
        <strong>₹1.21 per person per year</strong> on public libraries.
      </p>

      <p class="body">
        And the MoC's classification reveals a second pattern the MHA grouping hides: <strong>several
        states sit in multiple cultural zones</strong>. Rajasthan is in three (North, North Central,
        West). Andhra Pradesh, Karnataka, Telangana straddle South and South Central. Assam,
        Manipur, Tripura sit in both East and North-East. The State can't settle on which
        "culture" each state belongs to — but settles, in both maps, on the same underspend.
      </p>

      <div class="overlap-wrap">{OVERLAP_SVG}</div>
      <p class="chart-caption">
        STATES SITTING IN MULTIPLE MoC CULTURAL ZONES · RED ROWS = STATES IN 3+ ZONES.
      </p>

      <div class="question-block">
        India has two official State-drawn regional maps, drafted thirty years apart by two
        different ministries with different political logics. On <em>both</em>, the zones
        containing UP and the Hindi heartland are the zones where the State invests least
        in public libraries. The classifications differ. The underfunding doesn't.
        <strong>What kind of structural fact is so robust that it survives reclassification?</strong>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 5: FOUR ANSWERS TO ONE QUESTION -->
  <section class="section ink">
    <div class="grain"></div>
    <div class="stack">
      <div class="eyebrow">Section 5 · post-2021 receipts</div>
      <h2>FOUR STATES.<br><span class="red">FOUR ANSWERS.</span></h2>
      <p class="lede">
        CAG accounts for 2021-22 onwards are not yet published for most states.
        For Assam, Goa, Rajasthan, and Odisha we extracted figures from state
        demand-for-grants documents through 2024-25. These four are not a
        representative sample. They are what we have. Read them as four answers
        to one question: <em>when CAG actuals catch up, will the post-2018 retreat
        bend upward, stay flat, or keep falling?</em>
      </p>

      <div class="traj-grid">

        <div class="traj-card">
          <div class="st-name">GOA</div>
          <div class="traj-line">
            <div class="traj-step"><div class="yr">2014-15</div><div class="val">₹56.17</div><div class="tag">Actual</div></div>
            <div class="traj-step"><div class="yr">2018-19 · peak</div><div class="val">₹87.94</div><div class="tag">Actual</div></div>
            <div class="traj-step now"><div class="yr">2024-25</div><div class="val">₹161.52</div><div class="tag">Budget Est.</div></div>
          </div>
          <div class="question">
            Goa kept climbing — through 2019-20, through COVID, through 2024. By 2024-25 (BE) it
            is at <strong>₹284 per capita</strong>, comparable to Greece or Portugal.
            The question is not whether Goa is exceptional. It is whether Goa is also
            <em>instructive</em> — whether a coastal ex-Portuguese economy of 1.6 million can
            tell us anything about how to build libraries in a state of 230 million whose
            CMs never visit one.
          </div>
        </div>

        <div class="traj-card">
          <div class="st-name">ASSAM</div>
          <div class="traj-line">
            <div class="traj-step"><div class="yr">2014-15</div><div class="val">₹3.37</div><div class="tag">Actual</div></div>
            <div class="traj-step"><div class="yr">2018-19</div><div class="val">₹3.49</div><div class="tag">Actual</div></div>
            <div class="traj-step now"><div class="yr">2024-25</div><div class="val">₹3.96</div><div class="tag">Budget Est.</div></div>
          </div>
          <div class="question">
            Assam is the only one of the four where the recent budget estimate (₹4.59 in 2023-24 BE,
            ₹3.96 in 2024-25 BE) exceeds the 2018-19 actual. Caveat: Assam's state-budget figures
            cover MH 105 only and likely undercount by ~22% versus CAG accounts. <em>If</em> the BE
            converts into actual spending, Assam will be the first non-cess state in the data to
            recover above its pre-COVID library line. Will the BE actually convert?
          </div>
        </div>

        <div class="traj-card">
          <div class="st-name">RAJASTHAN</div>
          <div class="traj-line">
            <div class="traj-step"><div class="yr">2014-15</div><div class="val">₹1.07</div><div class="tag">Actual</div></div>
            <div class="traj-step"><div class="yr">2018-19</div><div class="val">₹1.10</div><div class="tag">Actual</div></div>
            <div class="traj-step now"><div class="yr">2024-25</div><div class="val">₹1.16</div><div class="tag">Revised Est.</div></div>
          </div>
          <div class="question">
            Rajasthan's per-capita library budget has grown from ₹0.94 to ₹1.16 over a decade —
            a 60% nominal increase, perhaps 5% in real terms. For a state of <strong>83 million</strong>,
            ₹2 per person per year is not investment. It is a token. The question is: at what
            point does a token become an admission — that the State has decided libraries are
            not what its public should expect?
          </div>
        </div>

        <div class="traj-card">
          <div class="st-name">ODISHA</div>
          <div class="traj-line">
            <div class="traj-step"><div class="yr">2014-15</div><div class="val">₹0.77</div><div class="tag">Actual</div></div>
            <div class="traj-step"><div class="yr">2018-19</div><div class="val">₹0.90</div><div class="tag">Actual</div></div>
            <div class="traj-step now"><div class="yr">2024-25</div><div class="val">₹0.65</div><div class="tag">Budget Est.</div></div>
          </div>
          <div class="question">
            Odisha has been celebrated for two decades as India's well-governed state — disaster
            response, fiscal discipline, mining royalties redirected to welfare. Its public-library
            line has not moved meaningfully from <strong>₹0.95 to ₹1.10</strong> across any year
            of this analysis. If a state that gets governance right cannot find its way to investing
            in libraries, where does that leave the states that get governance wrong?
          </div>
        </div>

      </div>

      <p class="body" style="margin-top:24px;">
        Three of these four states' answers to the question are: <em>flat or token</em>. One —
        Goa — kept climbing but does so under conditions that do not generalise. The fourth —
        Assam — might break upward, but only if a Budget Estimate becomes an actual disbursement,
        and only by ~22% above what CAG would report. This is the empirical anchor for the
        national extrapolation in Section 1. It is consistent with retreat, not recovery.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 5: LAW · CESS · TAX · ABSENCE -->
  <section class="section cream">
    <div class="stack">
      <div class="eyebrow">Section 6 · the legal architecture</div>
      <h2>ACT. CESS. TAX.<br><span class="red">ABSENCE.</span></h2>
      <p class="lede">
        Spending is downstream of legislation. Before a State can fund public libraries
        sustainably, it has to commit, in statute, that public libraries are a thing
        the State maintains. India has had three generations of state library legislation —
        and 76 years into the Republic, a fourth group: <strong>16 states, ~700 million
        people, no library law at all.</strong>
      </p>
      <p class="body">
        Read the numbers in Sections 1–3 against this legal architecture and the data
        speaks differently. Acts don't guarantee spending. Cess doesn't guarantee
        stability. The "free libraries" Act doesn't guarantee free libraries. But the
        inverse holds reliably: the states that never legislated public libraries are
        the states that don't fund them.
      </p>

      <div class="gen-stack">

        <!-- GEN I -->
        <div class="gen-card gen-1">
          <div class="gen-head">
            <div>
              <div class="label">Generation I · 1948–1989 · Act + Cess</div>
              <div class="h3">THE CESS TRADITION.</div>
            </div>
            <div class="meta">5 states<br><span class="avg">₹17.85</span>avg per capita</div>
          </div>
          <div class="gen-states">
            <span class="st-pill">Tamil Nadu <span class="yr">1948</span><span class="v">₹12.02</span></span>
            <span class="st-pill">Andhra Pradesh <span class="yr">1960</span><span class="v">₹18.32</span></span>
            <span class="st-pill">Karnataka <span class="yr">1965</span><span class="v">₹26.08</span></span>
            <span class="st-pill">West Bengal <span class="yr">1979</span><span class="v">₹14.58</span></span>
            <span class="st-pill">Kerala <span class="yr">1989</span><span class="v">₹18.26</span></span>
          </div>
          <p class="gen-text">
            Five states. All wrote a library cess into their Public Libraries Act: a small
            statutory levy — typically on property tax or stamp duty — collected by local
            bodies and dedicated, by law, to library development. Tamil Nadu did this
            <strong>before the Constitution</strong>: the Madras Public Libraries Act 1948
            was drafted with Ranganathan's input. Kerala did it in 1989 — two years before
            liberalisation closed the door on this kind of legislation.
          </p>
          <p class="gen-text">
            These are the only states in India that have, in law, treated library funding
            as a public obligation removed from annual budget politics. They also produced
            the most volatile expenditure data (see Cess Paradox, Section 2) — because the
            visibility of cess in CAG books is itself opaque. But the commitment is there.
            It is reversible only by legislative action, not by a budget cut.
          </p>
          <div class="gen-question">
            All five cess Acts came from regions with strong anti-caste or social-reform
            traditions — Periyar and the Dravidian movement in TN, the Communist movement
            in Kerala and Bengal, the Lingayat-reform inheritance in Karnataka, the Telugu
            self-respect tradition in AP. Is library cess legislation what happens when
            a literacy-as-political-praxis movement reaches the State and forces it to
            commit to reading as a public obligation?
          </div>
        </div>

        <!-- GEN II -->
        <div class="gen-card gen-2">
          <div class="gen-head">
            <div>
              <div class="label">Generation II · 1967–1989 · Act, no Cess</div>
              <div class="h3">THE TAX TRADITION.</div>
            </div>
            <div class="meta">4 states<br><span class="avg">₹6.43</span>avg per capita</div>
          </div>
          <div class="gen-states">
            <span class="st-pill">Maharashtra <span class="yr">1967</span><span class="v">₹9.20</span></span>
            <span class="st-pill">Manipur <span class="yr">1988</span><span class="v">₹5.09</span></span>
            <span class="st-pill">Haryana <span class="yr">1989 · "free"</span><span class="v low">₹1.10</span></span>
            <span class="st-pill">Telangana <span class="yr">1960 / 2015</span><span class="v">₹10.34</span></span>
          </div>
          <p class="gen-text">
            Four states. Wrote Acts but chose tax-funding — library spending must compete
            with everything else in the annual budget, every year. Maharashtra's 1967 Act
            built on the Kolhapur Princely State's 1945 Public Libraries Act (the earliest
            on the subcontinent). Telangana inherited the AP 1960 framework on bifurcation
            and enacted its own version in 2015.
          </p>
          <p class="gen-text">
            <strong>Haryana 1989 is the anomaly.</strong> Section 2(e) of the Haryana
            Public Libraries Act defines a public library as one that <em>"permits members
            of the public to use it for reference or borrowing without charging fee or
            subscription."</em> This is the only Indian Act that legally defines public
            libraries as free. It passed two years before liberalisation. Haryana's
            per-capita library spend: <strong>₹1.10</strong>.
          </p>
          <div class="gen-question">
            What does it mean to have a law that says "libraries are free" — and spend
            ₹1.10 per person on them? Is the law a placeholder for a politics that hasn't
            arrived yet, or a placeholder for a politics that has already arrived in
            another form — the State having decided that the statute is enough, and the
            funding is optional?
          </div>
        </div>

        <!-- GEN III -->
        <div class="gen-card gen-3">
          <div class="gen-head">
            <div>
              <div class="label">Generation III · 1993–2009 · Post-Liberalisation Soft Acts</div>
              <div class="h3">THE PAPER COMMITMENT.</div>
            </div>
            <div class="meta">6 states<br><span class="avg">₹2.32</span>avg w/o Goa &amp; Arunachal</div>
          </div>
          <div class="gen-states">
            <span class="st-pill">Goa <span class="yr">1993</span><span class="v">₹87.94</span></span>
            <span class="st-pill">Gujarat <span class="yr">2001</span><span class="v">₹3.72</span></span>
            <span class="st-pill">Odisha <span class="yr">2002</span><span class="v low">₹0.90</span></span>
            <span class="st-pill">Uttarakhand <span class="yr">2005</span><span class="v low">₹1.33</span></span>
            <span class="st-pill">Chhattisgarh <span class="yr">2006</span><span class="v low">₹0.93</span></span>
            <span class="st-pill">Arunachal Pradesh <span class="yr">2009</span><span class="v">₹35.56</span></span>
          </div>
          <p class="gen-text">
            Six states. <strong>Every Library Act passed in India after 1990 has been
            tax-funded.</strong> No state since Kerala 1989 has written cess into a public
            libraries Act. Strip the two small-population outliers (Goa, Arunachal) and the
            generation-III average is <strong>₹2.32 per person per year</strong> — barely
            distinguishable from the no-Act group.
          </p>
          <p class="gen-text">
            The Chattopadhyay Committee (1986) had already recommended a National Public
            Libraries Act with dedicated funding. Then 1991 happened. The National Knowledge
            Commission (2007) reframed libraries as "knowledge economy infrastructure" —
            digital, technocratic, not a constitutional public good. NEP 2020 reduced
            libraries to "one nation, one digital library." A Generation-III Library Act
            in this context is paper. Acts without funding-flow architecture.
          </p>
          <div class="gen-question">
            Did India lose the capacity to legislate cess for libraries in 1991 — or did
            it lose the political will to think of libraries as the kind of public good
            that deserves cess protection? Why is the cess option, present in every Act
            from 1948 to 1989, absent from every Act since?
          </div>
        </div>

        <!-- ABSENCE -->
        <div class="gen-card gen-absent">
          <div class="gen-head">
            <div>
              <div class="label">No Generation · No Library Act</div>
              <div class="h3">THE ABSENCE.</div>
            </div>
            <div class="meta">16 states<br><span class="avg">~700M</span>people</div>
          </div>
          <div class="gen-states">
            <span class="st-pill low">Uttar Pradesh<span class="v">₹0.70</span></span>
            <span class="st-pill low">Bihar<span class="v">₹0.27</span></span>
            <span class="st-pill low">Madhya Pradesh<span class="v">₹0.81</span></span>
            <span class="st-pill low">Jharkhand<span class="v">₹0.10</span></span>
            <span class="st-pill low">Punjab<span class="v">₹0.73</span></span>
            <span class="st-pill low">Rajasthan<span class="v">₹1.10</span></span>
            <span class="st-pill">Assam<span class="v">₹3.49</span></span>
            <span class="st-pill">Delhi<span class="v">₹3.19</span></span>
            <span class="st-pill">Himachal<span class="v">₹8.63</span></span>
            <span class="st-pill">J&amp;K<span class="v">₹9.74</span></span>
            <span class="st-pill">Meghalaya<span class="v">₹8.23</span></span>
            <span class="st-pill">Mizoram<span class="v">₹12.44</span></span>
            <span class="st-pill">Nagaland<span class="v">₹2.47</span></span>
            <span class="st-pill">Sikkim<span class="v">₹14.57</span></span>
            <span class="st-pill">Tripura<span class="v">₹7.85</span></span>
            <span class="st-pill">Puducherry<span class="v">₹37.47</span></span>
          </div>
          <p class="gen-text">
            Sixteen states. Of the eight lowest-spending in India, <strong>six are in this
            group</strong>: Jharkhand ₹0.10, Bihar ₹0.27, UP ₹0.70, Punjab ₹0.73, MP ₹0.81,
            Rajasthan ₹1.10. UP alone — 230 million people, more than the population of
            Brazil — has no statute naming public libraries as something the State maintains.
          </p>
          <p class="gen-text">
            The data refuses a clean story even here. Arunachal Pradesh, which the live
            government roster has been slow to update with its 2009 Act, spends ₹48 per
            capita. Mizoram, no Act, spends ₹12.44. Some no-Act states (the NE small ones)
            spend well; the large no-Act states all spend nothing. The absence is not a
            uniform condition — but it is a reliable predictor of underspend at scale.
          </p>
          <p class="gen-text">
            <strong>76 years.</strong> Tamil Nadu legislated in 1948. The Constitution
            commenced in 1950. UP has had three-quarters of a century to write a Public
            Libraries Act and has not. Bihar — the state of Nalanda — has not. Madhya
            Pradesh has not. Punjab — where the Phulkian princes founded state libraries
            in the 1880s — has not. This is not an oversight. It is, after three generations
            of opportunity, a positive political choice.
          </p>
          <div class="gen-question">
            What does it tell us about Indian democracy that the right to read — Phule's
            right, Periyar's right, Ambedkar's right — has not been legislated into law
            for over half the country? Whose Republic is it, if Republic-as-statute does
            not extend to the public infrastructure of literacy in the territories where
            most of its members live?
          </div>
        </div>

      </div>

      <p class="body" style="margin-top:24px;">
        Read this way, the per-capita data in earlier sections becomes a map of the State's
        legislative choices over four generations. The cess states wrote the strongest
        commitment and produced the most opaque accounting. The post-1991 Act states wrote
        soft commitments and produced flat budgets. The no-Act states wrote nothing and
        spend the least. There is one direction available to the Indian State now that
        it has not tried: a <strong>National Public Library Law</strong>, drafted under
        Chattopadhyay (1986) and again in 2024, never enacted. Whether such a law would
        compel funding, or simply create a federal version of Haryana's "free" Act, is the
        open question.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════ SECTION 6: SO WHAT -->
  <section class="section ink">
    <div class="grain"></div>
    <div class="stack">
      <div class="eyebrow">Section 7 · what this means</div>
      <h2>A DECADE.<br>NO <span class="red">REAL PROGRESS.</span></h2>
      <p class="lede">
        Public libraries are not a luxury. They are one of the few genuinely universal
        public goods — a place where a child from a poor family reads the same book
        as a child from a rich one. India's public library system, where it exists at
        all in the large northern states, is chronically underfunded.
      </p>
      <p class="body">
        The ₹11–12 figure that has circulated as a benchmark came from Balaji et al.'s
        careful 2025 study. Corrected for a growing population and rising prices using
        the MoSPI implicit GDP deflator (base 2011-12), India's peak real expenditure was
        <strong>₹7.87 per person in 2018-19</strong>. By 2024-25 that figure had retreated
        to <strong>₹4.66 — 41% below peak</strong>, almost entirely undoing the post-2014
        real-terms gain.
      </p>
      <p class="body">
        For scale: the central government alone spends over <strong>₹1,000 per capita
        per year on defence</strong>. State spending on education runs ₹200–400 per
        capita. ₹4.66 for libraries is not even a rounding error in that arithmetic.
        It is what a State that has decided libraries do not matter looks like.
      </p>
      <p class="body">
        The data also shows that this is not inevitable. Kerala, Tamil Nadu, Andhra
        Pradesh, and Karnataka built genuine library infrastructure over decades.
        Several small north-eastern states punch well above their weight. The
        political will exists somewhere in India. It just does not extend to the
        states where most Indians live.
      </p>
      <button type="button" class="print-btn" onclick="window.print()"
              aria-label="Print this analysis as an A4 PDF — pages 1-16 are the analysis, 17-18 are methodology and sources">
        Print this analysis (A4) →
      </button>
      <p class="print-hint">
        Pages 1–16 are the analysis. Pages 17–18 are sources, methodology, and the per-state CAGR table — choose "pages 1-16" in your print dialog to skip the methodology appendix.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════ METHODS -->
  <section class="section cream methods">
    <div class="stack">
      <details class="bib-collapse">
        <summary>Sources, data &amp; citations</summary>

      <p class="body">
        <strong>What we used and where it came from.</strong>
        State-level expenditure data for 2014-15 → 2020-21 from
        Kulkarni, Balaji &amp; Dhanamjaya (Source 1 below). State-level
        expenditure data for 2021-22 → 2024-25 from state demand-for-grants
        documents (Assam, Goa, Rajasthan, Odisha) accessed via Open Budgets
        India (Source 3). Annual state-level population from the MoHFW
        Technical Group's projections (Source 2). All replication checks
        against Kulkarni-Balaji-Dhanamjaya's 2018-19 per-capita figures
        pass within ±₹0.20 of their published nominal values.
      </p>

      <p class="body">
        <strong>Deflation to 2011-12 ₹.</strong>
        All real-terms per-capita figures on this page are deflated using
        the <strong>MoSPI implicit GDP deflator</strong> derived from
        National Accounts Statistics (GDP at current prices ÷ GDP at
        constant 2011-12 prices), using the latest published revision per
        year — Third Revised Estimates 2014-15 to 2020-21, Second Revised
        2021-22, Final Estimates 2022-23, First Revised 2023-24,
        Provisional Estimates 2024-25. This is the standard deflator for
        real government-spending analysis used in the IMF Government
        Finance Statistics Manual (GFSM 2014), OECD Government at a
        Glance, World Bank Public Expenditure Review methodology, and
        the RBI's annual <em>State Finances: A Study of Budgets</em>.
        Single-year state and zone cross-sections are deflated by the
        2018-19 factor (0.7404, i.e. a cumulative GDP-deflator level of
        1.3506 since the 2011-12 base). Per-state inflation differs
        slightly from the national factor; we use the national one for
        cross-state comparability. Kulkarni-Balaji-Dhanamjaya's original
        published nominal figures are recoverable by dividing by the
        same factor.
      </p>

      <h3>Sources</h3>
      <ol class="bib-list" style="font-family: var(--f-body); font-size: 15px; line-height: 1.6; padding-left: 28px;">
        <li style="margin-bottom: 14px;">
          Kulkarni, S. R., B. P. Balaji, and M. Dhanamjaya. "What Is the Per
          Capita Expenditure on Public Libraries in India? An Empirical
          Analysis." In <em>Book of Abstracts: Global Library Summit on
          Library Diplomacy</em>, South Asian University, New Delhi, 5–7
          February 2025, 125–32. New Delhi: LIS Academy, 2025.
        </li>
        <li style="margin-bottom: 14px;">
          National Commission on Population. <em>Population Projections for
          India and States, 2011–2036: Report of the Technical Group on
          Population Projections</em>. Chaired by K. S. James. New Delhi:
          Ministry of Health and Family Welfare, Government of India,
          July 2020.
          <a href="https://nhm.gov.in/New_Updates_2018/Report_Population_Projection_2019.pdf"
             target="_blank" rel="noopener"
             style="color:var(--red); text-decoration:underline;">nhm.gov.in/New_Updates_2018/Report_Population_Projection_2019.pdf</a>.
        </li>
        <li style="margin-bottom: 14px;">
          CivicDataLab and Centre for Budget and Governance Accountability.
          "Open Budgets India." Accessed May 2026.
          <a href="https://openbudgetsindia.org/" target="_blank" rel="noopener"
             style="color:var(--red); text-decoration:underline;">openbudgetsindia.org</a>.
          State demand-for-grants documents for Assam, Goa, Rajasthan, and
          Odisha (2021–22 through 2024–25) accessed through the OBI corpus.
        </li>
        <li style="margin-bottom: 14px;">
          Ministry of Statistics and Programme Implementation, Government
          of India. <em>National Accounts Statistics: Gross Domestic
          Product at Current and Constant 2011-12 Prices</em>.
          Annual series, base year 2011-12. Implicit GDP deflator
          computed as GDP-current-prices ÷ GDP-constant-2011-12-prices.
          Latest published revision per year used (Third Revised
          Estimates 2014-15 to 2020-21, Second Revised 2021-22, Final
          Estimates 2022-23, First Revised 2023-24, Provisional
          Estimates 2024-25). Accessed via the MoSPI public API,
          May 2026.
        </li>
      </ol>

      <p class="body" style="margin-top:18px;">
        <strong>Caveats.</strong> Budget Estimates and Revised Estimates are
        not actuals; actual spending may differ. Assam state-budget figures
        likely undercount by ~22% versus the CAG methodology. For states
        without published 2021–25 figures we use CAGR (2016-17 → 2020-21)
        extrapolation from the 2020-21 base — see the assumptions block
        below.
      </p>

      <h3>Extrapolation assumptions for replication</h3>
      <p class="body">
        These figures are estimates. They indicate trajectory, not confirmed actuals.
        Anyone replicating should verify against state budgets as they become available.
      </p>
      <p class="body">
        <strong>Method:</strong> For each state, compute compound annual growth rate (CAGR)
        of CAG library expenditure over 2016-17 to 2020-21 (4-year window).
        Project forward: <em>Exp(t) = Exp(2020-21) × (1 + CAGR)<sup>(t − 2020-21)</sup></em>.
      </p>
      <p class="body">
        <strong>Anomalous states</strong> (West Bengal, Karnataka, Telangana):
        included in national totals but flagged red below; cess reclassification
        and formation-year effects make their CAGRs unreliable for individual
        trend claims.
      </p>

      <table>
        <thead>
          <tr><th>State / Body</th><th>CAGR 16-21</th><th>2020-21 ₹L base</th><th>Notes</th></tr>
        </thead>
        <tbody>
          <tr><td>Andhra Pradesh</td><td class="num">+8.9%</td><td class="num">10,486</td><td>—</td></tr>
          <tr><td>Arunachal Pradesh</td><td class="num">+4.7%</td><td class="num">901</td><td>—</td></tr>
          <tr><td>Assam</td><td class="num">+8.4%</td><td class="num">1,711</td><td>Actuals 2021-24 override</td></tr>
          <tr><td>Bihar</td><td class="num">+3.0%</td><td class="num">262</td><td>—</td></tr>
          <tr><td>Chhattisgarh</td><td class="num">+7.5%</td><td class="num">312</td><td>—</td></tr>
          <tr><td>Delhi</td><td class="num">−2.5%</td><td class="num">579</td><td>—</td></tr>
          <tr><td>Goa</td><td class="num">+8.8%</td><td class="num">2,050</td><td>Actuals 2022-25 override</td></tr>
          <tr><td>Gujarat</td><td class="num">+10.7%</td><td class="num">3,276</td><td>—</td></tr>
          <tr><td>Haryana</td><td class="num">+36.3%</td><td class="num">1,136</td><td>2020-21 spike inflates CAGR</td></tr>
          <tr><td>Himachal Pradesh</td><td class="num">+9.9%</td><td class="num">539</td><td>—</td></tr>
          <tr><td>Jammu &amp; Kashmir</td><td class="num">−1.7%</td><td class="num">1,245</td><td>—</td></tr>
          <tr><td>Jharkhand</td><td class="num">−27.3%</td><td class="num">33</td><td>Trends to zero</td></tr>
          <tr class="anom"><td>Karnataka ⚠</td><td class="num">−10.0%</td><td class="num">7,321</td><td>Cess spike 2018-19</td></tr>
          <tr><td>Kerala</td><td class="num">−14.5%</td><td class="num">2,591</td><td>Cess volatility</td></tr>
          <tr><td>Madhya Pradesh</td><td class="num">+13.8%</td><td class="num">1,066</td><td>—</td></tr>
          <tr><td>Maharashtra</td><td class="num">−2.6%</td><td class="num">11,399</td><td>—</td></tr>
          <tr><td>Manipur</td><td class="num">−2.5%</td><td class="num">171</td><td>—</td></tr>
          <tr><td>Meghalaya</td><td class="num">+9.7%</td><td class="num">377</td><td>—</td></tr>
          <tr><td>Mizoram</td><td class="num">+6.1%</td><td class="num">201</td><td>—</td></tr>
          <tr><td>Nagaland</td><td class="num">+5.8%</td><td class="num">92</td><td>—</td></tr>
          <tr><td>Odisha</td><td class="num">+3.8%</td><td class="num">497</td><td>Actuals 2022-25 override</td></tr>
          <tr><td>Puducherry</td><td class="num">−2.1%</td><td class="num">707</td><td>—</td></tr>
          <tr><td>Punjab</td><td class="num">−3.2%</td><td class="num">254</td><td>—</td></tr>
          <tr><td>Rajasthan</td><td class="num">+4.2%</td><td class="num">1,098</td><td>Actuals 2023-25 override</td></tr>
          <tr><td>Sikkim</td><td class="num">+7.2%</td><td class="num">142</td><td>—</td></tr>
          <tr><td>Tamil Nadu</td><td class="num">+7.6%</td><td class="num">13,094</td><td>—</td></tr>
          <tr class="anom"><td>Telangana ⚠</td><td class="num">+6.9%</td><td class="num">5,278</td><td>Formation-year effect</td></tr>
          <tr><td>Tripura</td><td class="num">−70.6%</td><td class="num">3</td><td>2020-21 recording error</td></tr>
          <tr><td>Uttar Pradesh</td><td class="num">+32.9%</td><td class="num">2,314</td><td>—</td></tr>
          <tr><td>Uttarakhand</td><td class="num">+2.6%</td><td class="num">194</td><td>—</td></tr>
          <tr class="anom"><td>West Bengal ⚠</td><td class="num">−4.0%</td><td class="num">14,855</td><td>Cess reclassification</td></tr>
          <tr><td>Union Government</td><td class="num">−6.7%</td><td class="num">17,225</td><td>Central library grants declining</td></tr>
        </tbody>
      </table>

      </details>

    </div>
  </section>

  <footer>
    <div class="wip-notice">
      Work in progress · 2021-25 figures are extrapolations and will be revised
      as CAG actuals are published.
    </div>
    <div class="colophon-line">
      Last updated May 2026 ·
      Code: <a href="https://polyformproject.org/licenses/noncommercial/1.0.0">PolyForm-NC 1.0</a> ·
      Data: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a> ·
      <a class="github-link" href="https://github.com/CommonerLLP/theright2read" target="_blank" rel="noopener" aria-label="GitHub repository: CommonerLLP/theright2read" title="CommonerLLP/theright2read">
        <svg class="github-icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
          <title>GitHub</title>
          <path d="M8 0C3.58 0 0 3.67 0 8.2c0 3.62 2.29 6.69 5.47 7.77.4.08.55-.18.55-.4 0-.19-.01-.84-.01-1.53-2.01.38-2.53-.5-2.69-.96-.09-.24-.48-.96-.82-1.16-.28-.16-.68-.56-.01-.57.63-.01 1.08.59 1.23.83.72 1.24 1.87.89 2.33.68.07-.53.28-.89.51-1.09-1.78-.21-3.64-.91-3.64-4.04 0-.89.31-1.62.82-2.19-.08-.21-.36-1.04.08-2.16 0 0 .67-.22 2.2.84A7.4 7.4 0 0 1 8 3.95c.68 0 1.36.09 2 .28 1.53-1.06 2.2-.84 2.2-.84.44 1.12.16 1.95.08 2.16.51.57.82 1.3.82 2.19 0 3.14-1.87 3.83-3.65 4.04.29.25.54.76.54 1.54 0 1.11-.01 2-.01 2.27 0 .22.15.48.55.4A8.09 8.09 0 0 0 16 8.2C16 3.67 12.42 0 8 0Z" />
        </svg>
        <span>GitHub</span>
      </a>
    </div>
  </footer>

</main>

<div class="tip" id="tip"></div>

<script>
// Hover tooltip for SVG bubbles and bars. Reads data-tip from the hovered
// element, renders pipe-separated lines into the fixed-positioned #tip div.
(function() {{
  var tip = document.getElementById('tip');

  function place(x, y) {{
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var nx = x + 16, ny = y + 16;
    if (nx + w > window.innerWidth  - 8) nx = x - w - 16;
    if (ny + h > window.innerHeight - 8) ny = y - h - 16;
    tip.style.left = nx + 'px';
    tip.style.top  = ny + 'px';
  }}

  document.addEventListener('mouseover', function(e) {{
    var t = e.target;
    var info = (t && t.getAttribute) ? t.getAttribute('data-tip') : null;
    if (!info) return;
    var parts = info.split('|');
    var head = parts.shift();
    var html = '<b>' + head + '</b>';
    for (var i = 0; i < parts.length; i++) html += '<span>' + parts[i] + '</span>';
    tip.innerHTML = html;
    tip.style.display = 'block';
    // CRITICAL: set position on the same event, not just on mousemove —
    // otherwise the tooltip flashes at (0,0) until the cursor moves.
    place(e.clientX, e.clientY);
  }});

  document.addEventListener('mousemove', function(e) {{
    if (tip.style.display === 'block') place(e.clientX, e.clientY);
  }});

  document.addEventListener('mouseout', function(e) {{
    var t = e.target;
    if (t && t.getAttribute && t.getAttribute('data-tip')) {{
      tip.style.display = 'none';
    }}
  }});
}})();
</script>

<!-- ═══════════════════════════════ CHART.JS -->
<script>
const YRS_ALL  = {json.dumps(years_all)};
const LAST_ACT = {LAST_ACTUAL_IDX};

// Pamphlet palette
const C_INK   = '#0e0e0e';
const C_INKS  = '#2a2a2a';
const C_CREAM = '#f1e8d3';
const C_RED   = '#dc2a14';
const C_BLUE  = '#1936a8';

// Dash everything from the last-actual point onwards
function segDash(ctx) {{
  return ctx.p0DataIndex >= LAST_ACT ? [7, 5] : undefined;
}}

// ── Chart 1: National trend (cream section) ────────────────────────────────
new Chart(document.getElementById('chart1'), {{
  type: 'line',
  data: {{
    labels: YRS_ALL,
    datasets: [
      {{ label: 'A · Nominal / Census 2011 (Balaji)',
         data: {json.dumps(nat_A)},
         borderColor: C_INK, backgroundColor: 'transparent',
         borderWidth: 2.5, pointRadius: 3.5, pointBackgroundColor: C_INK,
         tension: 0.25, fill: false,
         segment: {{ borderDash: segDash }} }},
      {{ label: 'B · Nominal / TG projected pop',
         data: {json.dumps(nat_B)},
         borderColor: C_BLUE, backgroundColor: 'transparent',
         borderWidth: 2.5, pointRadius: 3.5, pointBackgroundColor: C_BLUE,
         tension: 0.25, fill: false,
         segment: {{ borderDash: segDash }} }},
      {{ label: 'C · Real (2011-12 ₹) / TG pop',
         data: {json.dumps(nat_C)},
         borderColor: C_RED, backgroundColor: 'transparent',
         borderWidth: 3, pointRadius: 4, pointBackgroundColor: C_RED,
         tension: 0.25, fill: false,
         segment: {{ borderDash: segDash }} }},
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    font: {{ family: "'Inter Tight', sans-serif" }},
    plugins: {{
      legend: {{ position: 'bottom',
        labels: {{ font: {{ family: "'JetBrains Mono', monospace", size: 11 }},
                   boxWidth: 14, color: C_INK }} }},
      tooltip: {{
        backgroundColor: C_INK, titleFont: {{ family: "'JetBrains Mono', monospace" }},
        bodyFont: {{ family: "'Inter Tight', sans-serif" }},
        callbacks: {{ label: ctx => ' ₹' + ctx.parsed.y.toFixed(2) + ' / person' }}
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(14,14,14,0.08)' }},
            ticks: {{ font: {{ family: "'JetBrains Mono', monospace", size: 10 }}, color: C_INK }} }},
      y: {{ title: {{ display: true, text: '₹ per person per year',
                       font: {{ family: "'JetBrains Mono', monospace", size: 11 }}, color: C_INK }},
            grid: {{ color: 'rgba(14,14,14,0.08)' }},
            ticks: {{ font: {{ family: "'JetBrains Mono', monospace", size: 10 }}, color: C_INK }},
            min: 0 }}
    }}
  }}
}});

// Charts 2, 3, 4 removed in favour of structured HTML/CSS callouts
// (Cess Paradox + Goa Exception in Section 2, Region cards in Section 3,
// State trajectory cards in Section 4, Generation cards in Section 5).

// Open every <details> when the user prints, so the PDF artefact is
// self-contained (Methods + per-state CAGR table included). Restore
// original state after the print dialog closes. The print CSS forces
// section.methods onto its own page so readers who only want the
// analysis can choose "pages 1-N" and skip the methodology appendix.
(function setupPrintExpansion() {{
  const remember = new WeakMap();
  window.addEventListener('beforeprint', () => {{
    document.querySelectorAll('details').forEach(d => {{
      remember.set(d, d.open);
      d.open = true;
    }});
  }});
  window.addEventListener('afterprint', () => {{
    document.querySelectorAll('details').forEach(d => {{
      if (remember.has(d)) d.open = remember.get(d);
    }});
  }});
}})();
</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Written: {OUT}")
print(f"Size: {len(html):,} bytes")
