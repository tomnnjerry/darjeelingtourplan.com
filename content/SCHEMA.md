# Darjeeling Tour Plan: content schema and house rules

Darjeeling Tour Plan (darjeelingtourplan.com) plans **affordable, well-run trips** in the eastern Himalaya and its
foothills, in seven lands only:

| slug | Land | Covers |
|---|---|---|
| `darjeeling` | Darjeeling Hills | Darjeeling town, Ghum, Tiger Hill, Kurseong, Mirik, Sandakphu–Singalila, Tinchuley, Takdah, Lamahatta, Sittong… |
| `kalimpong` | Kalimpong and Neora | Kalimpong, Lava, Lolegaon, Rishyap, Pedong, Sillery Gaon, Icchey Gaon, Neora Valley… |
| `east-sikkim` | Gangtok and East Sikkim | Gangtok, Tsomgo, Nathu La, Baba Mandir, Zuluk, Aritar, Rumtek, Pakyong… |
| `north-sikkim` | North Sikkim | Lachung, Yumthang, Lachen, Gurudongmar, Thangu, Dzongu, Chungthang, Mangan… |
| `west-sikkim` | West and South Sikkim | Pelling, Yuksom, Khecheopalri, Tashiding, Rinchenpong, Uttarey, Ravangla, Namchi, Temi… |
| `bhutan` | Bhutan | Phuentsholing, Thimphu, Paro, Punakha, Haa, Phobjikha, Bumthang, Trongsa… |
| `dooars` | Dooars and the Terai | Siliguri, Jaldapara, Gorumara, Lataguri, Chilapata, Murti, Samsing, Suntalekhola, Buxa, Jayanti… |

Byline on everything: "Darjeeling Tour Plan Desk". Voice: local, warm, straight-talking, first person plural ("we"),
like a planner who has ridden the shared jeeps and knows the cook at the homestay. Plain English, short sentences.
Audience: value-minded travellers — families from Kolkata, Delhi, Mumbai, Bengaluru and Dhaka, couples, students,
first-timers, and international visitors — who want a trip that is **well priced, honest and properly organised**.

The site has two promises: (1) **affordable** — every page helps people spend less without a worse trip
(shared jeeps vs reserved cars, off-season months, homestays, what is free, what is a tourist trap);
(2) **stories that are rooted** — the local history, language, people, food and small facts that generic sites skip.
Lepcha, Limbu, Bhutia, Gorkha/Nepali, Rajbanshi, Mech, Toto, Drukpa and Tibetan histories, the tea industry, the
Darjeeling Himalayan Railway, the old wool and mule trade over Nathu La and Jelep La, the Dzongs. Tell them accurately.

All content is JSON, UTF-8, under `content/<region-slug>/`. The JSON must parse (no comments, no trailing commas).
Slugs are lowercase-hyphenated ASCII and unique within their type across the WHOLE site (prefix with the place if
needed, e.g. `ghum-batasia-loop-morning`). Validate with `python tools/check_region.py <slug> --wiki` until it prints OK.

## Writing rules (strict)

- Headings and titles: no full stop at the end; short, one line on desktop (≤ 60 characters).
- Plain and specific: numbers over adjectives (km, hours, metres, INR, months, °C, seats in a shared jeep).
- BANNED words/phrases: nestled, breathtaking, hidden gem, paradise, tapestry, embark, delve, unleash, vibrant,
  bustling, mesmerizing, stunning, magical, heaven on earth, a feast for the eyes, something for everyone,
  whether you're, look no further, ultimate guide, in this blog, in conclusion, unforgettable, world-class,
  seamless, curated, elevate, immerse, timeless, jewel, boasts, queen of the hills (cliché: say it once at most
  in the whole Darjeeling region, and only to explain the nickname), abode, serene (max once per file).
- No emoji. No exclamation marks.
- Facts that change (permits, Protected Area Permits, Restricted Area Permits, Bhutan SDF, road and pass openings,
  landslide closures, park closures in monsoon (Jaldapara/Gorumara close mid-June to mid-September), toy-train
  timetables, fees, shared-jeep fares, flight routes): state the rule as you understand it and add
  "check current status before you travel".
- Never invent reviews, awards, statistics, star ratings, founders, staff names, client counts or "since 19xx".
- **Stories and "did you know" facts must be TRUE and checkable** (Wikipedia, district gazetteers, the DHR's UNESCO
  listing, park authorities, well-known histories). Where a story is a legend or oral tradition, say so ("Lepcha
  tradition holds that…"). Do not invent etymologies, dates, people or legends. If unsure, choose another fact.
- Prices are **indicative INR**. Packages: per person, twin sharing, from Bagdogra (IXB) / NJP / Siliguri, round to
  the nearest 500. Realistic for this market, e.g. a 5-night Darjeeling–Gangtok trip: budget ≈ ₹13,000–17,000,
  comfort ≈ ₹22,000–30,000, premium ≈ ₹50,000–80,000 per person. Shared jeep seats, entry fees, vehicle hire:
  state as a range, "indicative, 2026".
- Stays: REAL, currently operating properties only. Mix tiers: government tourist lodges (WBTDC, Sikkim Tourism,
  Bhutan hotels), well-known budget hotels and homestays, comfortable mid-range hotels, and the heritage/premium ones
  (Windamere, Glenburn, Mayfair, Elgin, Cochrane Place, Elgin Nor-Khill, Taj Guras Kutir, Six Senses, COMO Uma,
  Amankora, etc.). If unsure a property still operates, leave it out. Do not invent amenities, room counts or prices;
  `rate_band` is an indicative range per room per night and must be plausible.
- `best_months` is ALWAYS an array of 12 integers, Jan..Dec: 2 = best, 1 = good, 0 = avoid/closed.
- `wiki` = the EXACT title of an existing English Wikipedia article about that thing (used to fetch photos with
  credits). Use "" if none exists. Do not guess — the validator checks every title with `--wiki`.
- `image_query` = 3–6 words that would find a real photo of exactly that subject on Wikimedia Commons
  (e.g. "Batasia Loop Darjeeling toy train", "Tsomgo Lake Sikkim").
- FAQs: real questions travellers search for ("Is Sandakphu safe in April", "How much is a shared jeep from NJP to
  Darjeeling"); answers 40–90 words, answer first, specific.

## Files to write for each region `<r>`

### 1. `content/<r>/region.json`
```json
{
  "slug": "darjeeling", "name": "Darjeeling Hills", "country": "India",
  "tagline": "≤ 8 words",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para (60–110 words)", "para", "para", "para"],
  "story": {"title": "≤ 55 chars", "paras": ["70–120 words", "…", "…"], "source": "what it rests on, e.g. 'Treaty of 1835 with the Chogyal of Sikkim; O'Malley, Darjeeling District Gazetteer (1907)'"},
  "did_you_know": ["one true, checkable sentence", "…", "…", "…", "…"],          // exactly 5
  "facts": [["Best months", "Oct – May"], ["Gateway", "Bagdogra (IXB), NJP"], ["Ideal length", "…"], ["Currency", "…"], ["Languages", "…"], ["Permits", "…"], ["Altitude range", "…"]],
  "best_months": [1,1,2,2,2,0,0,0,1,2,2,2],
  "highlights": [{"title": "…", "text": "35–60 words"}],          // exactly 6
  "getting_there": "90–150 words",
  "permits": "60–120 words, or '' if none apply",
  "budget": {
    "summary": "60–100 words: how to do this land for less without a worse trip",
    "costs": [["Shared jeep NJP → Darjeeling", "₹250–400 a seat"], ["Reserved Bolero NJP → Darjeeling", "₹3,500–4,500"]],   // 6–8 rows, indicative
    "tips": ["one sentence", "…"]                                   // exactly 5
  },
  "wiki": "Darjeeling district",
  "lat": 27.04, "lng": 88.26, "zoom": 8,
  "months": [                                                      // exactly 12, Jan..Dec
    {"month": "January", "rating": 1, "weather": "Darjeeling 2–9 °C, dry, clear", "summary": "60–100 words",
     "go": ["place-slug", "place-slug", "place-slug"], "events": ["festival-slug"], "tip": "one sentence",
     "price_note": "one sentence on rates/crowds this month (e.g. off-season hotel discounts)"}
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 2. `content/<r>/places/<place-slug>.json` (one file per place; count given in your task)
```json
{
  "slug": "kurseong", "name": "Kurseong", "region": "darjeeling",
  "kind": "hill town | tea country | village | viewpoint | national park | wildlife sanctuary | lake | pass | valley | monastery town | river town | trek route | city | fort town",
  "wiki": "Kurseong", "image_query": "Kurseong tea garden hill",
  "lat": 26.88, "lng": 88.28, "altitude_m": 1458,
  "tagline": "≤ 70 chars",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para 70–120 words", "para", "para"],
  "story": {"title": "≤ 55 chars", "paras": ["70–120 words", "…"], "source": "short note on where this comes from"},
  "did_you_know": ["one true, checkable sentence", "…", "…"],     // exactly 3
  "local_name": {"text": "Kharsang", "language": "Lepcha", "meaning": "land of the white orchid"},   // OPTIONAL: omit the key entirely unless you are sure
  "facts": [["Best months", "…"], ["Nights we suggest", "1–2"], ["Nearest airport", "…"], ["From Siliguri", "≈ 32 km · 1.5 h"], ["Altitude", "1,458 m"], ["Known for", "…"]],
  "best_months": [1,1,2,2,2,0,0,0,1,2,2,1],
  "nights": "1–2",
  "highlights": [{"title": "…", "text": "35–60 words"}],          // 5–6
  "how_to_reach": [{"mode": "Shared jeep", "text": "…"}, {"mode": "Reserved car", "text": "…"}, {"mode": "Rail / Air", "text": "…"}],
  "where_to_stay": "70–120 words naming areas and real properties across budgets",
  "stays": ["stay-slug"],                                         // slugs from your stays.json in this place (may be [])
  "costs": [["Entry, Batasia Loop", "₹20–50"], ["Shared jeep from Siliguri", "₹150–250"]],   // 4–6 rows, indicative 2026
  "budget_tip": "one specific sentence that saves money here",
  "tips": ["one sentence", "…"],                                   // 5
  "themes": ["tea-gardens", "budget-trips"],                        // from THEMES below
  "nearby": ["place-slug"],                                        // 2–4 other places in this region
  "experiences": [                                                 // exactly 4
    {"slug": "kurseong-makaibari-tea-walk", "title": "≤ 55 chars",
     "kind": "culture | spiritual | nature | wildlife | food | adventure | tea | rail | village | craft",
     "duration": "2 hours", "best_time": "Mornings, Mar–May (first flush)", "cost": "₹300–600 per person, indicative | Free",
     "image_query": "Makaibari tea estate", "wiki": "Makaibari",
     "summary": "35–55 words", "body": ["para 70–120 words", "para", "para"],
     "good_for": ["couples", "families", "first-timers", "photographers", "solo", "seniors", "students"],
     "faqs": [{"q": "…", "a": "…"}]}                                // exactly 3
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 3. `content/<r>/journeys/<journey-slug>.json` (count given in your task)
Journeys are the **packages** customers buy. Mix of lengths (2–10 nights), budgets and styles; several should cross
into a neighbouring land when natural (e.g. Darjeeling + Gangtok): `stops[].place` must be a place in YOUR region
or one of the SHARED HUB SLUGS below. Title must make the length clear in the slug (`…-5n`).
```json
{
  "slug": "darjeeling-kurseong-mirik-4n", "title": "≤ 50 chars", "region": "darjeeling",
  "nights": 4, "themes": ["tea-gardens", "toy-train"],
  "stops": [{"place": "darjeeling", "nights": 3}, {"place": "mirik", "nights": 1}],   // nights sum = nights
  "start": "Bagdogra Airport (IXB) or NJP station", "end": "Bagdogra Airport (IXB) or NJP station",
  "price_from_inr": 14500,
  "fares": {"budget": 14500, "comfort": 24000, "premium": 52000},     // per person twin sharing, indicative
  "fare_notes": {"budget": "what budget means here: hotels/homestays class, vehicle, meals", "comfort": "…", "premium": "…"},
  "best_months": [1,1,2,2,2,0,0,0,1,2,2,1],
  "pace": "Easy | Balanced | Active", "max_altitude_m": 2590,
  "meta_description": "≤ 158 chars including 'N nights' and 'from ₹'",
  "summary": "40–60 words", "intro": ["para 70–120 words", "para"],
  "highlights": ["…"],                                                          // 5
  "days": [{"day": 1, "title": "≤ 45 chars", "place": "darjeeling", "overnight": "Darjeeling", "drive": "≈ 70 km · 3 h or ''", "text": "70–130 words", "meals": "Dinner"}],  // days = nights + 1
  "stays": ["stay-slug"],
  "includes": ["…"], "excludes": ["…"],
  "save_more": ["one way to make it cheaper, e.g. travel in shoulder months, shared jeep for transfer days"],   // 3
  "good_to_know": ["…"],
  "faqs": [{"q": "…", "a": "…"}]                                                // exactly 9
}
```

### 4. `content/<r>/stays.json` — array (count given in your task; mix tiers)
```json
[{"slug": "windamere-hotel-darjeeling", "name": "Windamere Hotel", "place": "darjeeling",
  "tier": "budget | comfort | premium",
  "kind": "heritage hotel | tea bungalow | homestay | government lodge | hotel | resort | boutique hotel | forest lodge | farmstay",
  "rate_band": "₹14,000–22,000 per room night, indicative",
  "wiki": "", "image_query": "Windamere Hotel Darjeeling",
  "summary": "35–55 words", "body": ["para 70–110 words", "para"],
  "why": ["one line", "one line", "one line"], "best_for": ["couples", "…"],
  "watch_out": "one honest sentence (steep walk up, shared bathrooms, no lift, patchy hot water…)",
  "website": "official URL only if certain, else ''",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 3
```

### 5. `content/<r>/guides/<guide-slug>.json` (count given in your task)
```json
{"slug": "darjeeling-on-a-budget", "title": "≤ 60 chars", "region": "darjeeling",
 "category": "planning | budget | seasons | stays | culture | food | wildlife | practical | journeys | history",
 "meta_description": "≤ 158 chars", "summary": "40–60 words answer-first",
 "sections": [{"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"], "table": {"head": ["…"], "rows": [["…"]]}}],
 "related_places": ["place-slug"],
 "faqs": [{"q": "…", "a": "…"}]}                                                 // exactly 9
```
Guides: 1,100–1,600 words of body across 5–8 sections; `list` and `table` are optional per section (use a table in
at least one section). At least 2 of a region's guides must be category `budget` and 1 must be `history`.

### 6. `content/<r>/festivals.json` — array (count given in your task)
```json
[{"slug": "losar-in-darjeeling", "name": "Losar", "place": "darjeeling", "wiki": "Losar",
  "image_query": "Losar festival monastery dance", "when": "Feb–Mar, Tibetan new year (lunar calendar)", "month_nums": [2, 3],
  "summary": "35–55 words", "body": ["para 70–110 words", "para", "para"], "tips": ["…", "…", "…"],
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```

### 7. `content/<r>/routes.json` — array (count given in your task): getting between two places in this region
```json
[{"slug": "njp-to-darjeeling", "from": "siliguri", "to": "darjeeling", "distance_km": 72,
  "summary": "35–55 words",
  "options": [{"mode": "Shared jeep", "time": "3 h", "cost": "₹250–400 a seat", "text": "50–90 words"}, {"mode": "Reserved car", "time": "3 h", "cost": "₹3,500–4,500 per car", "text": "…"}, {"mode": "Toy train", "time": "7 h", "cost": "…", "text": "…"}],
  "stops_on_way": ["…"], "tip": "one sentence",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```
`from` and `to` must be place slugs you created or SHARED HUB SLUGS (at least one of the two must be yours).

## THEMES (use these slugs only)
tea-gardens, toy-train, monasteries, mountain-views, high-passes, wildlife-safaris, treks-and-walks,
village-homestays, honeymoons, family-trips, food-and-markets, festivals, budget-trips, birding-and-orchids

## Shared hub slugs (owned by one region, usable by all in journeys `stops`/`days[].place` and routes)
siliguri (dooars) · lataguri (dooars) · darjeeling (darjeeling) · kurseong (darjeeling) · mirik (darjeeling) ·
kalimpong (kalimpong) · lava (kalimpong) · gangtok (east-sikkim) · zuluk (east-sikkim) · lachung (north-sikkim) ·
lachen (north-sikkim) · pelling (west-sikkim) · ravangla (west-sikkim) · phuentsholing (bhutan) · thimphu (bhutan) ·
paro (bhutan) · punakha (bhutan).
The owning region MUST create a place file with exactly that slug. Use `siliguri` as the plains gateway
(it covers NJP station and Bagdogra airport).

## Cross-references
Every other slug you reference (places, stays, festivals in `events`, `nearby`) must exist in your own region's files.
