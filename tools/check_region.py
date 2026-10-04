"""Validate one region's content against content/SCHEMA.md.

Usage: python tools/check_region.py <region-slug> [--wiki]
--wiki also confirms every `wiki` title exists on English Wikipedia.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"
THEMES = set("tea-gardens toy-train monasteries mountain-views high-passes wildlife-safaris treks-and-walks "
             "village-homestays honeymoons family-trips food-and-markets festivals budget-trips "
             "birding-and-orchids".split())
KINDS = set("culture spiritual nature wildlife food adventure tea rail village craft".split())
TIERS = {"budget", "comfort", "premium"}
HUBS = {"siliguri": "dooars", "lataguri": "dooars", "darjeeling": "darjeeling", "kurseong": "darjeeling",
        "mirik": "darjeeling", "kalimpong": "kalimpong", "lava": "kalimpong", "gangtok": "east-sikkim",
        "zuluk": "east-sikkim", "lachung": "north-sikkim", "lachen": "north-sikkim", "pelling": "west-sikkim",
        "ravangla": "west-sikkim", "phuentsholing": "bhutan", "thimphu": "bhutan", "paro": "bhutan",
        "punakha": "bhutan"}
BANNED = ["nestled", "breathtaking", "hidden gem", "paradise", "tapestry", "embark", "delve", "unleash",
          "vibrant", "bustling", "mesmeriz", "stunning", "magical", "heaven on earth", "feast for the eyes",
          "something for everyone", "whether you're", "look no further", "ultimate guide", "in this blog",
          "in conclusion", "unforgettable", "world-class", "seamless", "elevate", "immerse", "timeless",
          "boasts", "curated", "abode", "!"]
errors, warns = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(p, f"invalid JSON ({e})")
        return None


def months(where, v):
    if not (isinstance(v, list) and len(v) == 12 and all(x in (0, 1, 2) for x in v)):
        err(where, "best_months must be 12 ints of 0/1/2")


def faqs(where, v, n):
    if not isinstance(v, list) or len(v) != n:
        err(where, f"needs exactly {n} faqs (has {len(v) if isinstance(v, list) else 0})")
        return
    for f in v:
        if not f.get("q") or not f.get("a"):
            err(where, "faq missing q/a")


def heading(where, t):
    if t and t.rstrip().endswith("."):
        err(where, f"heading ends with full stop: {t!r}")


def story(where, v, minp=2):
    if not isinstance(v, dict) or not v.get("title") or len(v.get("paras", [])) < minp or not v.get("source"):
        err(where, f"story needs title, >= {minp} paras and source")
    else:
        heading(where, v["title"])


def nlist(where, v, n, name):
    if not isinstance(v, list) or len(v) != n:
        err(where, f"needs exactly {n} {name} (has {len(v) if isinstance(v, list) else 0})")


def scan_banned(where, obj):
    text = json.dumps(obj, ensure_ascii=False).lower()
    for b in BANNED:
        if b in text:
            warns.append(f"{where}: banned word/phrase '{b}'")


def main():
    r = sys.argv[1]
    base = ROOT / r
    wiki_titles = []
    reg = load(base / "region.json")
    places, stays, fests = {}, {}, {}
    for p in sorted((base / "places").glob("*.json")):
        d = load(p)
        if d:
            places[d["slug"]] = d
    for s in load(base / "stays.json") or []:
        stays[s["slug"]] = s
    for f in load(base / "festivals.json") or []:
        fests[f["slug"]] = f

    if reg:
        months("region", reg.get("best_months"))
        faqs("region", reg.get("faqs"), 9)
        if len(reg.get("highlights", [])) != 6:
            err("region", "needs 6 highlights")
        if len(reg.get("months", [])) != 12:
            err("region", "needs 12 months")
        for m in reg.get("months", []):
            for g in m.get("go", []):
                if g not in places:
                    err(f"region month {m.get('month')}", f"unknown place '{g}'")
            for e in m.get("events", []):
                if e not in fests:
                    err(f"region month {m.get('month')}", f"unknown festival '{e}'")
        story("region", reg.get("story"))
        nlist("region", reg.get("did_you_know"), 5, "did_you_know")
        b = reg.get("budget") or {}
        if not b.get("summary") or not (6 <= len(b.get("costs", [])) <= 8) or len(b.get("tips", [])) != 5:
            err("region", "budget needs summary, 6-8 costs, 5 tips")
        for m in reg.get("months", []):
            if not m.get("price_note"):
                err(f"region month {m.get('month')}", "missing price_note")
        wiki_titles.append(reg.get("wiki"))
        scan_banned("region", reg)

    exp_slugs = set()
    for slug, d in places.items():
        w = f"place {slug}"
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("tagline"))
        if d.get("region") != r:
            err(w, f"region field must be '{r}'")
        story(w, d.get("story"))
        nlist(w, d.get("did_you_know"), 3, "did_you_know")
        if not (4 <= len(d.get("costs", [])) <= 6):
            err(w, "needs 4-6 costs rows")
        if not d.get("budget_tip"):
            err(w, "missing budget_tip")
        if "local_name" in d and not all(d["local_name"].get(k) for k in ("text", "language", "meaning")):
            err(w, "local_name needs text, language, meaning (or omit it)")
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        for n in d.get("nearby", []):
            if n not in places:
                err(w, f"unknown nearby '{n}'")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        ex = d.get("experiences", [])
        if len(ex) != 4:
            err(w, f"needs 4 experiences (has {len(ex)})")
        for e in ex:
            heading(f"{w} exp", e.get("title"))
            if e.get("kind") not in KINDS:
                err(f"{w} exp {e.get('slug')}", f"unknown kind '{e.get('kind')}'")
            if not e.get("cost"):
                err(f"{w} exp {e.get('slug')}", "missing cost")
            faqs(f"{w} exp {e.get('slug')}", e.get("faqs"), 3)
            if e["slug"] in exp_slugs:
                err(w, f"duplicate experience slug {e['slug']}")
            exp_slugs.add(e["slug"])
            if e.get("wiki"):
                wiki_titles.append(e["wiki"])
        wiki_titles.append(d.get("wiki"))
        scan_banned(w, d)

    for p in sorted((base / "journeys").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"journey {d.get('slug')}"
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        total = sum(s.get("nights", 0) for s in d.get("stops", []))
        if total != d.get("nights"):
            err(w, f"stop nights {total} != nights {d.get('nights')}")
        if len(d.get("days", [])) != d.get("nights", 0) + 1:
            err(w, "days must equal nights + 1")
        for s in d.get("stops", []):
            if s["place"] not in places and s["place"] not in HUBS:
                err(w, f"unknown stop '{s['place']}'")
        for dd in d.get("days", []):
            if dd.get("place") and dd["place"] not in places and dd["place"] not in HUBS:
                err(w, f"day {dd.get('day')}: unknown place '{dd['place']}'")
        f = d.get("fares") or {}
        if set(f) != TIERS or not all(isinstance(f[k], int) for k in f):
            err(w, "fares must have int budget/comfort/premium")
        elif not (f["budget"] < f["comfort"] < f["premium"]) or d.get("price_from_inr") != f["budget"]:
            err(w, "fares must rise budget<comfort<premium and price_from_inr == fares.budget")
        if set((d.get("fare_notes") or {})) != TIERS:
            err(w, "fare_notes needs budget/comfort/premium")
        nlist(w, d.get("save_more"), 3, "save_more")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        scan_banned(w, d)

    for slug, s in stays.items():
        w = f"stay {slug}"
        faqs(w, s.get("faqs"), 3)
        if s.get("tier") not in TIERS:
            err(w, f"tier must be budget/comfort/premium")
        if not s.get("rate_band") or not s.get("watch_out"):
            err(w, "needs rate_band and watch_out")
        if s.get("place") not in places:
            err(w, f"unknown place '{s.get('place')}'")
        if s.get("wiki"):
            wiki_titles.append(s["wiki"])
        scan_banned(w, s)

    for p in sorted((base / "guides").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"guide {d.get('slug')}"
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
        if words < 1000:
            warns.append(f"{w}: only {words} words")
        for s in d.get("sections", []):
            heading(w, s.get("heading"))
        for rp in d.get("related_places", []):
            if rp not in places:
                err(w, f"unknown related place '{rp}'")
        scan_banned(w, d)

    for slug, f in fests.items():
        w = f"festival {slug}"
        faqs(w, f.get("faqs"), 4)
        if f.get("place") not in places:
            err(w, f"unknown place '{f.get('place')}'")
        if f.get("wiki"):
            wiki_titles.append(f["wiki"])
        scan_banned(w, f)

    cats = []
    for p in sorted((base / "guides").glob("*.json")):
        d = load(p)
        if d:
            cats.append(d.get("category"))
    if cats and (cats.count("budget") < 2 or cats.count("history") < 1):
        warns.append("guides: need >= 2 'budget' and >= 1 'history' category")
    for slug in [h for h, reg_ in HUBS.items() if reg_ == r]:
        if slug not in places:
            err("hubs", f"this region must create place '{slug}'")
    for rt in load(base / "routes.json") or []:
        w = f"route {rt.get('slug')}"
        faqs(w, rt.get("faqs"), 4)
        for k in ("from", "to"):
            if rt.get(k) not in places and rt.get(k) not in HUBS:
                err(w, f"unknown {k} '{rt.get(k)}'")
        if rt.get("from") not in places and rt.get("to") not in places:
            err(w, "at least one end must be a place in this region")
        for o in rt.get("options", []):
            if not o.get("cost"):
                err(w, f"option {o.get('mode')} missing cost")
        scan_banned(w, rt)

    if "--wiki" in sys.argv:
        titles = sorted({t for t in wiki_titles if t})
        for i in range(0, len(titles), 40):
            q = urllib.parse.urlencode({"action": "query", "titles": "|".join(titles[i:i + 40]),
                                        "redirects": 1, "format": "json", "formatversion": 2})
            req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                         headers={"User-Agent": "DarjeelingTourPlanBuild/1.0"})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            for pg in data["query"]["pages"]:
                if pg.get("missing"):
                    err("wiki", f"no Wikipedia article titled {pg['title']!r} (use '' or fix)")

    counts = (f"places={len(places)} experiences={len(exp_slugs)} stays={len(stays)} festivals={len(fests)} "
              f"journeys={len(list((base / 'journeys').glob('*.json')))} guides={len(list((base / 'guides').glob('*.json')))}")
    print(counts)
    for w in warns:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
