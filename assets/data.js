/* ============================================================
   data.js — canonical data and constants for the pamphlet.
   Single source of truth. Both / and /data/ load this.

   Update numbers here and they propagate everywhere that reads them
   from window.CONSTANTS / window.DATA. HTML strings still need the
   {{TOKEN}} substitution dance — see helpers.js / substituteConstants.
   ============================================================ */

// ─── CANONICAL NUMBERS ────────────────────────────────────────────
// One place to update. Reference window.CONSTANTS.NAME from JS,
// or {{NAME}} from HTML (with substituteConstants on load).
const CONSTANTS = {
  STATUE_OF_UNITY_CR:   2989,    // ₹ crore — Statue of Unity construction cost (Govt. of Gujarat, 2018)
  NATIONAL_PER_CAPITA:  15.30,   // ₹ / person / year — state-level avg. per-capita library spend (KBD 2025)
  CENTRE_PER_CAPITA:    2.07,    // ₹ / person / year — Centre's per-capita library spend (KBD 2025)
  COMBINED_PER_CAPITA:  11.62,   // ₹ / person / year — peak national combined (state + Centre)
  RRRLF_20YR_TOTAL_CR:  197,     // ₹ crore — RRRLF total 2003-2023
  BOOK_PRICE:           250,     // ₹ — typical Indian-published paperback (illustrative)

  CENTRE_BUDGET:        4800000, // ₹ crore — Union Budget 2024-25 BE
  CENTRE_LIBRARIES:     195,     // ₹ crore — Centre's full library spend (CAG 2205-105 avg 2014-21)
  CENTRE_ADS:           644,     // ₹ crore — Govt advertising FY 2024-25 actual
  CORP_TAX_CUT:         145000,  // ₹ crore — revenue forgone from 2019 corporate tax cut, FY 2019-20
  STANDARD_DEDUCTION:   75000    // ₹ — Income tax standard deduction (FY 2024-25 New Regime)
};
window.CONSTANTS = CONSTANTS;

// ─── STATE PER-CAPITA SPEND ───────────────────────────────────────
// 7 years: 2014-15 to 2020-21. ₹ per person per year. Source: MoC.
const YEARS = ['2014-15','2015-16','2016-17','2017-18','2018-19','2019-20','2020-21'];

const STATE_DATA = {
  "Goa": [68.14,93.48,100.43,118.31,124.91,137.97,140.55],
  "Puducherry": [52.25,60.66,61.58,59.64,60.06,56.23,56.62],
  "Arunachal Pradesh": [43.61,55.13,54.09,53.13,51.82,59.97,65.12],
  "Andhra Pradesh": [8.39,8.59,15.10,20.50,26.07,26.30,21.23],
  "Sikkim": [14.68,15.66,17.69,19.17,21.24,28.61,23.32],
  "West Bengal": [0.53,0.54,19.19,19.44,20.82,0.46,16.28],
  "Karnataka": [16.54,16.01,18.27,19.56,37.74,19.71,11.98],
  "Mizoram": [11.73,12.22,14.48,15.37,18.13,20.29,18.32],
  "Tamil Nadu": [10.93,11.36,13.52,14.90,16.98,18.86,18.15],
  "Telangana": [0.75,23.35,11.49,19.46,14.70,14.18,15.00],
  "Jammu & Kashmir": [6.15,10.85,10.61,10.95,13.78,null,9.92],
  "Maharashtra": [9.73,15.07,11.28,12.60,13.43,9.19,10.14],
  "Himachal Pradesh": [4.34,4.42,5.39,5.76,12.34,8.89,7.86],
  "Meghalaya": [9.20,9.19,8.77,9.53,11.98,12.15,12.71],
  "Tripura": [9.30,9.75,9.89,11.35,11.46,11.77,0.07],
  "Kerala": [5.04,16.22,14.52,25.08,25.85,10.17,7.76],
  "Manipur": [6.23,4.51,6.64,6.89,7.42,5.16,5.99],
  "Gujarat": [3.06,3.33,3.61,4.62,5.60,5.85,5.42],
  "Assam": [4.16,3.60,3.97,5.61,5.14,5.18,5.48],
  "Delhi": [3.09,3.00,3.82,3.81,5.02,3.04,3.45],
  "Nagaland": [2.11,2.86,3.71,3.51,3.59,3.70,4.65],
  "Uttarakhand": [1.44,1.55,1.73,1.98,1.96,1.92,1.92],
  "Rajasthan": [1.34,1.30,1.36,1.43,1.66,1.62,1.60],
  "Haryana": [1.24,1.41,1.30,1.61,1.66,1.76,4.48],
  "Chhattisgarh": [0.95,0.85,0.91,1.75,1.40,1.11,1.22],
  "Odisha": [0.92,0.99,1.02,1.15,1.26,1.25,1.18],
  "Madhya Pradesh": [0.86,0.84,0.88,1.00,1.22,1.28,1.47],
  "Punjab": [1.12,1.12,1.04,1.04,1.05,1.08,0.92],
  "Uttar Pradesh": [0.32,0.36,0.37,0.42,1.05,1.10,1.16],
  "Bihar": [0.25,0.11,0.22,0.25,0.41,0.25,0.25],
  "Jharkhand": [0.20,0.31,0.36,0.12,0.15,0.12,0.10]
};

// `free: true` = Act explicitly defines public libraries as free of fees (only Haryana 2021).
const LEGISLATION = {
  "Andhra Pradesh": {has_act: true, year: 1960, free: false},
  "Arunachal Pradesh": {has_act: false},
  "Assam": {has_act: true, year: 1989, free: false},
  "Bihar": {has_act: false},
  "Chhattisgarh": {has_act: true, year: 2006, free: false},
  "Delhi": {has_act: false},
  "Goa": {has_act: true, year: 1993, free: false},
  "Gujarat": {has_act: true, year: 2001, free: false},
  "Haryana": {has_act: true, year: 2021, free: true},
  "Himachal Pradesh": {has_act: false},
  "Jammu & Kashmir": {has_act: false},
  "Jharkhand": {has_act: false},
  "Karnataka": {has_act: true, year: 1965, free: false},
  "Kerala": {has_act: true, year: 1989, free: false},
  "Madhya Pradesh": {has_act: false},
  "Maharashtra": {has_act: true, year: 1967, free: false},
  "Manipur": {has_act: true, year: 1988, free: false},
  "Meghalaya": {has_act: false},
  "Mizoram": {has_act: false},
  "Nagaland": {has_act: false},
  "Odisha": {has_act: true, year: 2002, free: false},
  "Puducherry": {has_act: false},
  "Punjab": {has_act: false},
  "Rajasthan": {has_act: false},
  "Sikkim": {has_act: false},
  "Tamil Nadu": {has_act: true, year: 1948, free: false},
  "Telangana": {has_act: true, year: 1960, free: false},
  "Tripura": {has_act: false},
  "Uttar Pradesh": {has_act: false},
  "Uttarakhand": {has_act: true, year: 2005, free: false},
  "West Bengal": {has_act: true, year: 1979, free: false}
};

// Jurisdiction-level contacts for the dual-addressee letter (CM + PM cc).
// PMO has no public direct email — uses the official "Write to the PM" form
// at pmindia.gov.in. CPGRAMS (pgportal.gov.in) is the unified central
// grievance portal — every submission receives a docket + response timeline.
// State CMO emails + state grievance portal URLs are PLACEHOLDERS — verify
// from each state's official CMO / Vidhan Sabha source before launch.
const JURISDICTION_CONTACTS = {
  _centre: {
    title: "Hon'ble Prime Minister of India",
    email: null,
    portal: "https://www.pmindia.gov.in/en/interact-with-honble-pm/",
    central_grievance: "https://pgportal.gov.in"
  },
  "Andhra Pradesh":    { title: "Hon'ble Chief Minister, Government of Andhra Pradesh",    email: null, portal: null },
  "Arunachal Pradesh": { title: "Hon'ble Chief Minister, Government of Arunachal Pradesh", email: null, portal: null },
  "Assam":             { title: "Hon'ble Chief Minister, Government of Assam",             email: null, portal: null },
  "Bihar":             { title: "Hon'ble Chief Minister, Government of Bihar",             email: null, portal: null },
  "Chhattisgarh":      { title: "Hon'ble Chief Minister, Government of Chhattisgarh",      email: null, portal: null },
  "Delhi":             { title: "Hon'ble Chief Minister, Government of NCT of Delhi",       email: null, portal: null, note: "Delhi Public Library is run by the Centre — the PM cc is especially relevant here." },
  "Goa":               { title: "Hon'ble Chief Minister, Government of Goa",               email: null, portal: null },
  "Gujarat":           { title: "Hon'ble Chief Minister, Government of Gujarat",           email: null, portal: null },
  "Haryana":           { title: "Hon'ble Chief Minister, Government of Haryana",           email: null, portal: null },
  "Himachal Pradesh":  { title: "Hon'ble Chief Minister, Government of Himachal Pradesh",  email: null, portal: null },
  "Jammu & Kashmir":   { title: "Hon'ble Chief Minister, Government of J&K",               email: null, portal: null },
  "Jharkhand":         { title: "Hon'ble Chief Minister, Government of Jharkhand",         email: null, portal: null },
  "Karnataka":         { title: "Hon'ble Chief Minister, Government of Karnataka",         email: null, portal: null },
  "Kerala":            { title: "Hon'ble Chief Minister, Government of Kerala",            email: null, portal: null },
  "Madhya Pradesh":    { title: "Hon'ble Chief Minister, Government of Madhya Pradesh",    email: null, portal: null },
  "Maharashtra":       { title: "Hon'ble Chief Minister, Government of Maharashtra",       email: null, portal: null },
  "Manipur":           { title: "Hon'ble Chief Minister, Government of Manipur",           email: null, portal: null },
  "Meghalaya":         { title: "Hon'ble Chief Minister, Government of Meghalaya",         email: null, portal: null },
  "Mizoram":           { title: "Hon'ble Chief Minister, Government of Mizoram",           email: null, portal: null },
  "Nagaland":          { title: "Hon'ble Chief Minister, Government of Nagaland",          email: null, portal: null },
  "Odisha":            { title: "Hon'ble Chief Minister, Government of Odisha",            email: null, portal: null },
  "Puducherry":        { title: "Hon'ble Chief Minister, Government of Puducherry",        email: null, portal: null },
  "Punjab":            { title: "Hon'ble Chief Minister, Government of Punjab",            email: null, portal: null },
  "Rajasthan":         { title: "Hon'ble Chief Minister, Government of Rajasthan",         email: null, portal: null },
  "Sikkim":            { title: "Hon'ble Chief Minister, Government of Sikkim",            email: null, portal: null },
  "Tamil Nadu":        { title: "Hon'ble Chief Minister, Government of Tamil Nadu",        email: null, portal: null },
  "Telangana":         { title: "Hon'ble Chief Minister, Government of Telangana",         email: null, portal: null },
  "Tripura":           { title: "Hon'ble Chief Minister, Government of Tripura",           email: null, portal: null },
  "Uttar Pradesh":     { title: "Hon'ble Chief Minister, Government of Uttar Pradesh",     email: null, portal: null },
  "Uttarakhand":       { title: "Hon'ble Chief Minister, Government of Uttarakhand",       email: null, portal: null },
  "West Bengal":       { title: "Hon'ble Chief Minister, Government of West Bengal",       email: null, portal: null }
};

// Annual RRRLF grant disbursement (₹ Lakhs, 2003-2023)
const RRMLF_DATA = {
  2003:378.53, 2004:177.00, 2005:390.00, 2006:207.00,
  2008:332.00, 2010:887.43, 2012:2350.00, 2013:2670.30,
  2014:1139.32, 2015:710.00, 2016:2046.47, 2017:1493.40,
  2018:1363.61, 2019:697.36, 2020:745.73, 2021:782.83,
  2022:2680.64, 2023:645.74
};

// 2021-24 RRRLF utilisation by state (released, ₹ Lakhs, summed across years)
const RRRLF_RELEASED = {
  // computed from Q.1316 — values approximate; meaningful (>5L) entries by state
  "Gujarat": 933, "Tamil Nadu": 145, "Maharashtra": 372, "West Bengal": 442,
  "Karnataka": 397, "Goa": 40, "Mizoram": 122, "Nagaland": 110,
  "Telangana": 179, "Kerala": 154, "Tripura": 136, "Himachal Pradesh": 32,
  "Uttar Pradesh": 12, "Andhra Pradesh": 4, "Manipur": 4, "Madhya Pradesh": 9,
  "Arunachal Pradesh": 115, "Assam": 49, "Bihar": 124, "Delhi": 16,
  "Haryana": 78, "Jammu & Kashmir": 147, "Meghalaya": 38, "Odisha": 42,
  "Rajasthan": 134, "Sikkim": 1, "Uttarakhand": 1, "Chhattisgarh": 3,
  "Puducherry": 0, "Punjab": 0, "Jharkhand": 0
};

// State population (millions, ~2020 mid-year — used for the statue-test
// math). Census 2011 + standard projections.
const STATE_POP_MN = {
  "Andhra Pradesh": 53, "Arunachal Pradesh": 1.5, "Assam": 35, "Bihar": 124,
  "Chhattisgarh": 30, "Delhi": 19, "Goa": 1.7, "Gujarat": 67, "Haryana": 28,
  "Himachal Pradesh": 7.4, "Jammu & Kashmir": 14, "Jharkhand": 38,
  "Karnataka": 67, "Kerala": 36, "Madhya Pradesh": 85, "Maharashtra": 124,
  "Manipur": 3.2, "Meghalaya": 3.4, "Mizoram": 1.2, "Nagaland": 2.2,
  "Odisha": 46, "Puducherry": 1.5, "Punjab": 30, "Rajasthan": 80,
  "Sikkim": 0.7, "Tamil Nadu": 79, "Telangana": 38, "Tripura": 4.0,
  "Uttar Pradesh": 235, "Uttarakhand": 11, "West Bengal": 100
};
// STATUE_OF_UNITY_CR moved into CONSTANTS at the top of this file.
// Backwards-compatible alias for code that references it as a global:
const STATUE_OF_UNITY_CR = CONSTANTS.STATUE_OF_UNITY_CR;

const NML_STATES = new Set(['Arunachal Pradesh','Goa','Mizoram','Rajasthan','Telangana','Uttar Pradesh',
  'West Bengal','Assam','Madhya Pradesh','Maharashtra','Nagaland','Tamil Nadu','Karnataka',
  'Bihar','Himachal Pradesh','Haryana','Chhattisgarh','Odisha','Uttarakhand','Jammu & Kashmir',
  'Sikkim','Manipur','Meghalaya','Kerala','Puducherry','Punjab','Jharkhand']);

// India vs World (₹ per capita per year — nominal). Three-country comparison only:
// India, China, USA. India listed first as the anchor; longer list parked.
const WORLD = [
  { name: "India",  value: 15.30, india: true },
  { name: "China",  value: 250,   india: false },
  { name: "USA",    value: 2900,  india: false }
];
// PARKED full list (for /data/ subpage later):
// const WORLD_FULL = [
//   { name: "Finland",    value: 5500, india: false },
//   { name: "USA",        value: 2900, india: false },
//   { name: "Australia",  value: 2400, india: false },
//   { name: "UK",         value: 1820, india: false },
//   { name: "Canada",     value: 1700, india: false },
//   { name: "China",      value: 250,  india: false },
//   { name: "India · State avg", value: 15.30, india: true },
//   { name: "India · Centre",    value: 0.07,  india: true }
// ];

const STANDARDS = [
  { n: "01", short: "Free", long: "No fees, no subscription, no membership cost. Ever." },
  { n: "02", short: "Anti-caste", long: "No discrimination on caste, class, gender, sexuality, ability, religion, language." },
  { n: "03", short: "Universal access", long: "Provisions for persons with disabilities. Hours that fit working lives." },
  { n: "04", short: "Internet", long: "Free, fast, private, uncensored Wi-Fi and devices for all members." },
  { n: "05", short: "Local", long: "Collections in the languages of the community. Books that look back at the reader." },
  { n: "06", short: "Private", long: "What you read is your business. No surveillance. No data sold." },
  { n: "07", short: "Funded", long: "Public money. Per capita allocations tied to standards. Audited." }
];

const EXCLUDED = [
  { id: "dalit",      label: "Dalit, Bahujan, Adivasi" },
  { id: "women",      label: "Women, non-binary & trans people" },
  { id: "disabled",   label: "Persons with disabilities" },
  { id: "working",    label: "The working class & rural poor" },
  { id: "muslim",     label: "Religious minorities" },
  { id: "linguistic", label: "Speakers of non-dominant languages" }
];

// Narrowed focus: the two specific State efforts that failed/are failing.
// Phule, Ambedkar, Ranganathan, Birsa, Baroda, Haryana, FLN draft, China 2017
// preserved in HISTORY_PARKED below for re-use later (current voice excludes them
// to sharpen the indictment to the Centre's actual policy record).
const HISTORY = [
  { year: "1986", title: "Chattopadhyay Committee — drafted, then shelved", body: "A government-appointed committee declared what should have been obvious: public libraries must be free, and the State must fund them. The Union Government received the report. Forty years on, no national library policy has been adopted. The recommendations sit on a shelf — the same shelf the books are not on." },
  { year: "2014", title: "National Mission on Libraries — too small to matter", body: "The Union Government launched NML to modernise sixty-four public libraries. Sixty-four. In a country of 1.4 billion people. ₹78.7 crore sanctioned in total — roughly the price of one luxury apartment in South Mumbai. ₹20.6 crore of that remains undisbursed. NML is not a policy. It is a press release." }
];

const HISTORY_PARKED = [
  { year: "1848", title: "Phule opens a school", body: "Jotirao and Savitribai Phule open a school for Dalit-Bahujan girls in Pune. Reading is the first political act." },
  { year: "1873", title: "Satyashodhak Samaj", body: "Phule's Society of Truth-Seekers names knowledge-gatekeeping for what it is — a brahminical lock on the public mind." },
  { year: "1910", title: "Baroda makes a free library", body: "Sayajirao Gaekwad III, inspired by American public libraries, opens the Baroda Central Library — free, open to all. He also funds Ambedkar's scholarship to Columbia." },
  { year: "1931", title: "Ranganathan's Five Laws", body: "Books are for use. Every reader her book. Every book its reader. Save the time of the reader. The library is a growing organism. Free was the first one." },
  { year: "1948", title: "Tamil Nadu Library Act", body: "India's first state library act — drafted with Ranganathan's input, but restricts membership to paying users, contradicting his own First Law." },
  { year: "1956", title: "Ambedkar's library", body: "Babasaheb dies. He leaves behind a personal library of more than 35,000 books — an indictment of the country that would not let him be educated easily." },
  { year: "2017", title: "China enacts a Public Library Law", body: "A comparably-sized democracy enshrines public libraries as a statutory right. India still has no equivalent." },
  { year: "2021", title: "Haryana — the only state", body: "Haryana passes a Library Act that defines the public library as actually free. To this day, the only Indian state to do so." },
  { year: "2024", title: "FLN drafts the policy", body: "The Free Libraries Network publishes the People's National Library Policy — the document the state has refused to write for seventy-five years." },
  { year: "2026", title: "You read this", body: "What happens next is up to people who have a bookshelf at home and a friend who is a Member of Parliament." }
];

// `iso` = BCP 47 / ISO 639 language code for the `text` field. Used in `lang=`
// attribute on the rendered <blockquote> so screen readers + browsers pick the
// right phoneme inventory and font fallback.
const QUOTES = [
  { iso: "mr", script: "deva",  text: "विद्ये विना मती गेली। मती विना नीती गेली।", attr: "महात्मा फुले", en: "Without learning, intellect was lost. Without intellect, morality was lost.", attrEn: "Jyotirao Phule" },
  { iso: "en",                  text: "Cultivate the mind. Educate. Agitate. Organise.", attr: "Dr. B. R. Ambedkar" },
  { iso: "ta", script: "tamil", text: "பகுத்தறிவு இல்லாதவன் மனிதன் அல்ல.", attr: "தந்தை பெரியார்", en: "One without rational thought is not yet human.", attrEn: "Periyar E. V. Ramasamy" },
  { iso: "hi", script: "deva",  text: "अबुआ दिशुम, अबुआ राज।", attr: "बिरसा मुंडा", en: "Our country, our rule.", attrEn: "Birsa Munda" },
  { iso: "mr", script: "deva",  text: "शिकलेली बाई घर सुधारते, गाव सुधारते.", attr: "सावित्रीबाई फुले", en: "An educated woman improves the home and the village.", attrEn: "Savitribai Phule" },
  { iso: "en",                  text: "Books are for use. Every reader her book. Every book its reader.", attr: "S. R. Ranganathan, Five Laws of Library Science" }
];

const ACTIONS = [
  { n: "01", verb: "WALK", title: "into the nearest public library this week.", body: "Find one. Sit in it. See who is there and who is not. See what books they have, what they don't. See whether they charge. Tell three friends what you saw." },
  { n: "02", verb: "FUND", title: "a free library that already exists.", body: "The Free Libraries Network runs and supports community libraries across India — most of them on a hand-to-mouth budget. ₹1,000 a month from a middle-class household keeps a child reading for a year." },
  { n: "03", verb: "DONATE", title: "books — but only the ones a child would actually read.", body: "Not your old college textbooks. Picture books in the local language. Adolescent fiction. Comics. Books that look like the children who will read them." },
  { n: "04", verb: "ASK", title: "what your state's library budget is.", body: "File an RTI. Most states won't have a clean answer. That is itself the answer. Publish what you find." },
  { n: "05", verb: "TEACH", title: "a reading session, once a week, in your neighbourhood.", body: "Not a curriculum. Not a coaching class. Just reading. Out loud, in any language. With anyone who wants to listen." },
  { n: "06", verb: "VOTE", title: "and ask candidates a public-library question.", body: "Local body, MLA, MP. Ask in writing. Publish the silence. The first politician who answers has noticed something the others haven't." }
];

const PARLIAMENT = [
  { label: "Libraries sanctioned under NML", value: "64", sub: "across all states/UTs — 1 library per ~21 million people." },
  { label: "Total NML sanctioned", value: "₹78.7 Cr", sub: "central + state share combined." },
  { label: "Released to states (74%)", value: "₹58 Cr", sub: "central ₹43 Cr + state ₹9 Cr. ₹20.6 Cr stuck in pipeline." },
  { label: "Unreleased — pipeline", value: "26%", sub: "of sanctioned amount remains undisbursed. Indore, MP got 50% of its sanction; Khandwa got 90%." }
];

// ─── DIVERSION GAME ROUNDS ────────────────────────────────────────
// Each round: India had a real budget, and funded one of the listed
// items. The user picks. The "correct" item is always the vanity
// option. By round 4, the user has internalised the pattern: India
// funds vanity. The diversion is the strategy.
const DIVERSION_ROUNDS = [
  {
    year: 2018,
    budget: "₹2,989 crore",
    prompt: "It's <strong>2018</strong>. India had <strong>₹2,989 crore</strong> on the table. India funded <strong>ONE</strong> of these. Pick which.",
    options: [
      { text: "A new IIT campus", cost: "~₹1,500 cr" },
      { text: "The country's largest public library system, twice over", cost: "~₹1,500 cr" },
      { text: "Universal child stunting elimination across two states", cost: "~₹500 cr" },
      { text: "A 182-metre statue", cost: "₹2,989 cr", correct: true }
    ],
    feedback: "<strong>India built the Statue of Unity.</strong> ₹2,989 crore. The world's tallest statue. With the same money the Centre could have funded its <strong>library foundation for fifteen years</strong>, eliminated child stunting in two whole states, and still had change for an IIT.",
    diversion: "Sold to the public as 'national pride.'"
  },
  {
    year: 2014,
    budget: "₹78.7 crore",
    prompt: "It's <strong>2014</strong>. India had <strong>₹78.7 crore</strong> for the National Mission on Libraries. It modernised <strong>ONE</strong> of these. Pick which.",
    options: [
      { text: "5,000 panchayat-level libraries (one per ~150 villages)", cost: "~₹16 lakh each" },
      { text: "1,000 district libraries with new books and Wi-Fi", cost: "~₹8 lakh each" },
      { text: "64 libraries — total — across all of India", cost: "~₹1.2 cr each", correct: true },
      { text: "200 women's reading rooms in rural districts", cost: "~₹40 lakh each" }
    ],
    feedback: "<strong>India modernised 64 libraries.</strong> Sixty-four. In a country of 1.4 billion people. That works out to <strong>one library per 22 million Indians</strong>. The mission is a press release. ₹20.6 crore of the sanctioned amount remains undisbursed a decade on.",
    diversion: "The press release said 'transformative.'"
  },
  {
    year: 2024,
    budget: "₹3,000 crore",
    prompt: "Across one fiscal year, the Centre spent <strong>~₹3,000 crore</strong> on government advertising — its own image. With the same money, India could have funded <strong>ONE</strong> of these. Which did it actually choose?",
    options: [
      { text: "15× the entire annual public-library budget of every state combined", cost: "~₹3,000 cr" },
      { text: "Free school lunches for 30 million additional children", cost: "~₹3,000 cr" },
      { text: "10,000 primary health sub-centres", cost: "~₹3,000 cr" },
      { text: "Government advertising. Newspapers, TV, hoardings, jingles.", cost: "₹3,000 cr", correct: true }
    ],
    feedback: "<strong>India bought ad space.</strong> Newspapers, TV, hoardings, jingles. Around <strong>₹3,000 crore</strong> on the State's own publicity. That is roughly <strong>15× the country's entire library budget</strong>. The State spent more on telling you it was working than on the work.",
    diversion: "Frames itself as 'public information.'"
  },
  {
    year: 2019,
    budget: "₹1,45,000 crore",
    prompt: "In <strong>2019</strong> the Union government had a <strong>₹1.45 lakh crore</strong> hole to fill in revenue. It chose <strong>ONE</strong> of these.",
    options: [
      { text: "100 years of full library funding for the entire country", cost: "~₹1.4 lakh cr" },
      { text: "A National Public Library Law + 50,000 new libraries", cost: "~₹1.5 lakh cr" },
      { text: "MNREGA expansion + universal free school meals", cost: "~₹1.4 lakh cr" },
      { text: "A corporate tax cut. Permanent. From 30% to 22%.", cost: "₹1,45,000 cr revenue forgone (FY 2019-20)", correct: true }
    ],
    feedback: "<strong>India cut corporate tax.</strong> ₹1.45 lakh crore in revenue forgone — every year, compounding. That is more than <strong>100× the country's annual library spend</strong>, gifted upward, in perpetuity. The promised investment surge never came. The libraries didn't either.",
    diversion: "Sold as 'investment-led growth.'"
  },
  {
    year: 2022,
    budget: "₹20,000 crore",
    prompt: "<strong>Central Vista</strong>, the Delhi redevelopment project — original budget ₹13,450 cr, since revised. Most current estimate: <strong>~₹20,000 crore.</strong> India chose <strong>ONE</strong> of these.",
    options: [
      { text: "A district public library in every one of India's 800 districts", cost: "~₹2,000 cr" },
      { text: "A new AIIMS hospital in 8 underserved states", cost: "~₹16,000 cr" },
      { text: "A new Parliament + new central government office complex + new PM/VP residences", cost: "₹20,000 cr (rising)", correct: true },
      { text: "Free higher education for every Dalit, Adivasi & OBC student for 5 years", cost: "~₹15,000 cr" }
    ],
    feedback: "<strong>India built the Central Vista.</strong> A new Parliament, new offices, new residences. Most recent estimate: ~₹20,000 crore, rising. With the same money India could have built a <strong>district public library in all 800 districts</strong> — and still funded eight new AIIMS hospitals.",
    diversion: "Promoted as 'modernising democracy.'"
  },
  {
    year: 2023,
    budget: "₹4,000 crore (cumulative)",
    prompt: "Renamed cities, stations, airports, highways, schemes. The cumulative cost of just the <strong>renaming-and-rebranding</strong> — new signage, stationery, web infra, GIS updates — runs into <strong>thousands of crores</strong>. India chose <strong>ONE</strong> path.",
    options: [
      { text: "Update every government textbook with current science + civics", cost: "~₹500 cr" },
      { text: "Spend on translation + Devanagari/regional-script open-access digital books", cost: "~₹300 cr" },
      { text: "Rename Allahabad, Faizabad, Aurangabad, Ahmednagar, Mughalsarai — and counting", cost: "~₹4,000 cr (signage / stationery / digital infra)", correct: true },
      { text: "Pay every public-school teacher a 5% raise for 3 years", cost: "~₹3,500 cr" }
    ],
    feedback: "<strong>India renamed cities.</strong> Thousands of crores in signage, stationery, GIS database updates, court-order compliance, train indicators, official letterheads. The textbooks didn't get updated. The teachers didn't get paid. The library was never built. <strong>The map was redrawn instead.</strong>",
    diversion: "Marketed as 'reclaiming heritage.'"
  }
];
