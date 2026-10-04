"""In-memory catalogue built from content/*.json.

Every page on the site is rendered from this catalogue. In DEBUG the catalogue
reloads when any content file changes, so writers see edits on refresh.
"""
import json
import re
import zlib
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.urls import reverse

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_SHORT = [m[:3] for m in MONTHS]
REGION_ORDER = ["darjeeling", "kalimpong", "east-sikkim", "north-sikkim", "west-sikkim", "bhutan", "dooars"]
# Each land wears the colours it is known for.
# ground = dark sections, accent = highlights and buttons on dark, ink = accent text on light, tint = light wash
# alt = the altitude printed on the land's station board, gate = where the climb starts
LANDS = {
    "darjeeling": {"palette": "Toy-train blue and muscatel gold", "short": "Darjeeling", "ground": "#10284A", "ground2": "#1A3A66",
                   "accent": "#F0C05A", "ink": "#875A00", "tint": "#E8EEF7", "alt": 2042, "board": "DARJEELING", "line": "Tea, toy train and the long view"},
    "kalimpong": {"palette": "Fern nursery and orchid pink", "short": "Kalimpong", "ground": "#173826", "ground2": "#21482F",
                  "accent": "#F28DB2", "ink": "#A3305F", "tint": "#E6F1E8", "alt": 1247, "board": "KALIMPONG", "line": "Orchids, wool-trade bazaars, forest villages"},
    "east-sikkim": {"palette": "Tsomgo turquoise and marigold", "short": "Gangtok", "ground": "#0B3A40", "ground2": "#12494F",
                    "accent": "#F6A93B", "ink": "#955000", "tint": "#E0F2F1", "alt": 1650, "board": "GANGTOK", "line": "Capital ridge, lakes and the old Silk Route"},
    "north-sikkim": {"palette": "High-glacier indigo and rhododendron", "short": "North Sikkim", "ground": "#1E2350", "ground2": "#2A3066",
                     "accent": "#FF8A80", "ink": "#B3262E", "tint": "#ECEDF8", "alt": 2700, "board": "LACHUNG", "line": "Valleys of snow, yak and rhododendron"},
    "west-sikkim": {"palette": "Kangchenjunga dawn and snow", "short": "Pelling", "ground": "#3B1F3F", "ground2": "#4C2A51",
                    "accent": "#FFB38A", "ink": "#A2421A", "tint": "#F6E9EE", "alt": 2150, "board": "PELLING", "line": "Monasteries facing the third-highest peak"},
    "bhutan": {"palette": "Dzong red and royal saffron", "short": "Bhutan", "ground": "#5A1410", "ground2": "#6E1E17",
               "accent": "#F7B500", "ink": "#875900", "tint": "#FBEBDD", "alt": 2334, "board": "THIMPHU", "line": "Dzongs, archery and the thunder dragon"},
    "dooars": {"palette": "Sal forest and elephant grass", "short": "Dooars", "ground": "#22351A", "ground2": "#2C4422",
               "accent": "#E3CF73", "ink": "#665500", "tint": "#EEF0DC", "alt": 122, "board": "SILIGURI", "line": "Rhino, elephant and the doors to Bhutan"},
}

# Shiny gradients per land: `grad` = ground (dark, 3 stops), `foil` = metallic accent (light → mid → deep).
GRADIENTS = {
    "darjeeling": {"grad": ("#0A1A33", "#163A6B", "#25579A"), "foil": ("#FFF0B8", "#F0C05A", "#B9861C")},
    "kalimpong": {"grad": ("#0C2417", "#1D4A2E", "#2D6A43"), "foil": ("#FFD6E6", "#F28DB2", "#C2477A")},
    "east-sikkim": {"grad": ("#04252A", "#0B4B52", "#13707A"), "foil": ("#FFE2A8", "#F6A93B", "#C9750F")},
    "north-sikkim": {"grad": ("#0E1030", "#262C6B", "#4A4F9A"), "foil": ("#FFD6D2", "#FF8A80", "#CC4B4B")},
    "west-sikkim": {"grad": ("#1F0F24", "#4A2551", "#7A3B6E"), "foil": ("#FFE3CF", "#FFB38A", "#D96E3A")},
    "bhutan": {"grad": ("#330A07", "#6E1A12", "#9A2A18"), "foil": ("#FFF0A0", "#F7C21E", "#C98A00")},
    "dooars": {"grad": ("#121F0D", "#2A4520", "#466B2E"), "foil": ("#FFF6C2", "#E3CF73", "#A8902A")},
}
for _slug, _g in GRADIENTS.items():
    LANDS[_slug].update(_g)

KINDS = OrderedDict([
    ("culture", ("Culture", "Bazaars, old bungalows and the people who keep them", "Walks with people who grew up here: the history of each hill town told street by street, from the British sanatorium years to today.")),
    ("spiritual", ("Monasteries and faith", "Gompas, dzongs, chortens and temples", "Prayer halls at prayer hours, with someone to explain what you see and how to behave inside.")),
    ("nature", ("Views and nature", "Sunrise points, lakes, valleys and waterfalls", "Viewpoints at the right hour and walks in the forest, timed to the clear-sky months.")),
    ("wildlife", ("Wildlife", "Rhino, elephant, red panda and birds", "Jeep safaris, watchtowers and forest walks in the Dooars and the high sanctuaries, booked to the zone and the season.")),
    ("food", ("Food", "Momo, thukpa, churpi and the tea-shop table", "Market mornings, home kitchens and the bakeries and tea rooms that have fed the hills for a century.")),
    ("adventure", ("Treks and adventure", "Ridges, rivers and high passes", "Treks and active days graded honestly by hours, height and terrain, with guides who know the trail.")),
    ("tea", ("Tea", "Estates, factories and tastings", "Walk the bushes with a planter, watch withering and rolling, taste the flushes side by side.")),
    ("rail", ("Toy train", "The Darjeeling Himalayan Railway", "Steam joy rides, the loops and the zig-zags of a UNESCO World Heritage line built in 1881.")),
    ("village", ("Village stays", "Homestays, farms and forest villages", "Sleep in family homes, eat what the farm grows and spend money where it stays in the village.")),
    ("craft", ("Craft", "Thangka, weaving, carving and paper", "Studios and cooperatives where the work is made, with no commission on what you buy.")),
])

_cache = {"stamp": None, "cat": None}


def _read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _stamp(root):
    return max((p.stat().st_mtime for p in root.rglob("*.json")), default=0)


def catalogue():
    root = Path(settings.CONTENT_DIR)
    if _cache["cat"] is None or settings.DEBUG:
        stamp = _stamp(root)
        if stamp != _cache["stamp"]:
            _cache["cat"] = Catalogue(root)
            _cache["stamp"] = stamp
    return _cache["cat"]


def month_bar(best):
    """[{'m': 'Jan', 'v': 2}, ...] for the 12-month strip."""
    best = best or [0] * 12
    return [{"m": MONTH_SHORT[i], "full": MONTHS[i], "v": best[i] if i < len(best) else 0} for i in range(12)]


def best_range(best):
    """'Oct – Mar' style label from a 12-int array (rating 2 = best)."""
    if not best:
        return ""
    good = {i for i, v in enumerate(best) if v == 2} or {i for i, v in enumerate(best) if v >= 1}
    if not good:
        return ""
    if len(good) == 12:
        return "All year"
    runs = []  # runs on a circular calendar, e.g. Oct..Mar
    for i in range(12):
        if i in good and (i - 1) % 12 not in good:
            run, j = [i], (i + 1) % 12
            while j in good:
                run.append(j)
                j = (j + 1) % 12
            runs.append(run)
    labels = []
    for run in runs:
        labels.append(MONTH_SHORT[run[0]] if len(run) == 1 else f"{MONTH_SHORT[run[0]]} – {MONTH_SHORT[run[-1]]}")
    return " · ".join(labels)


class Catalogue:
    def __init__(self, root):
        self.root = root
        self.themes = OrderedDict((t["slug"], t) for t in _read(root / "themes.json"))
        img_file = root / "images.json"
        self.images = _read(img_file) if img_file.exists() else {}
        self.regions = OrderedDict()
        self.places = OrderedDict()
        self.experiences = OrderedDict()
        self.journeys = OrderedDict()
        self.stays = OrderedDict()
        self.guides = OrderedDict()
        self.festivals = OrderedDict()
        self.routes = OrderedDict()
        for slug in REGION_ORDER:
            base = root / slug
            if (base / "region.json").exists():
                self._load_region(slug, base)
        self.posts = OrderedDict()
        for p in (root / "journal").glob("*.json") if (root / "journal").exists() else []:
            d = _read(p)
            d["url"] = reverse("post", args=[d["slug"]])
            self.posts[d["slug"]] = d
        self.posts = OrderedDict(sorted(self.posts.items(), key=lambda kv: kv[1].get("date", ""), reverse=True))
        self._link()
        self._link_posts()

    # ---------- loading ----------
    def _load_region(self, slug, base):
        r = _read(base / "region.json")
        r["slug"] = slug
        pal = LANDS[slug]
        r.update(pal)
        r["pigment"], r["deep"] = pal["accent"], pal["ink"]
        r["num"] = f"{REGION_ORDER.index(slug) + 1:02d}"
        r["url"] = reverse("region", args=[slug])
        r["places"], r["journeys"], r["stays"], r["guides"], r["festivals"], r["routes"] = [], [], [], [], [], []
        self.regions[slug] = r
        for p in sorted((base / "places").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("place", args=[slug, d["slug"]])
            self.places[d["slug"]] = d
            r["places"].append(d)
            for e in d.get("experiences", []):
                e["place"] = d["slug"]
                e["region"] = slug
                e["url"] = reverse("experience", args=[slug, d["slug"], e["slug"]])
                self.experiences[e["slug"]] = e
        for p in sorted((base / "journeys").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("journey", args=[d["slug"]])
            self.journeys[d["slug"]] = d
            r["journeys"].append(d)
        for name, store, key, view in (("stays.json", self.stays, "stays", "stay"),
                                       ("festivals.json", self.festivals, "festivals", "festival"),
                                       ("routes.json", self.routes, "routes", "route")):
            f = base / name
            for d in (_read(f) if f.exists() else []):
                d["region"] = slug
                d["url"] = reverse(view, args=[d["slug"]])
                store[d["slug"]] = d
                r[key].append(d)
        for p in sorted((base / "guides").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("guide", args=[d["slug"]])
            self.guides[d["slug"]] = d
            r["guides"].append(d)

    def _imgs(self, *keys):
        for k in keys:
            if self.images.get(k):
                return self.images[k]
        return []

    def _link(self):
        # drop routes whose places do not exist (yet)
        for slug in [s for s, rt in self.routes.items() if rt.get("from") not in self.places or rt.get("to") not in self.places]:
            dead = self.routes.pop(slug)
            self.regions[dead["region"]]["routes"].remove(dead)
        for r in self.regions.values():
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["places"][:6] for i in self._imgs(f"place:{p['slug']}")[:1]]
            r["best_label"] = best_range(r.get("best_months"))
            r["bar"] = month_bar(r.get("best_months"))
        for p in self.places.values():
            p["region_obj"] = self.regions[p["region"]]
            p["images"] = self._imgs(f"place:{p['slug']}")
            p["best_label"] = best_range(p.get("best_months"))
            p["bar"] = month_bar(p.get("best_months"))
            p["nearby_objs"] = [self.places[s] for s in p.get("nearby", []) if s in self.places]
            p["stay_objs"] = [self.stays[s] for s in p.get("stays", []) if s in self.stays]
            p["journey_objs"] = [j for j in self.journeys.values()
                                 if any(s["place"] == p["slug"] for s in j.get("stops", []))]
            p["festival_objs"] = [f for f in self.festivals.values() if f.get("place") == p["slug"]]
            p["serial"] = f"{zlib.crc32(p['slug'].encode()) % 9000 + 1000:04d}"
            p["route_objs"] = [rt for rt in self.routes.values() if p["slug"] in (rt.get("from"), rt.get("to"))]
        for r in self.regions.values():
            # the places most journeys stop at lead menus and supply the land's lead photos
            r["top_places"] = sorted(r["places"], key=lambda p: (-len(p["journey_objs"]), p["name"]))
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["top_places"][:6] for i in p["images"][:1]]
        for e in self.experiences.values():
            place = self.places[e["place"]]
            e["place_obj"] = place
            e["region_obj"] = place["region_obj"]
            e["images"] = self._imgs(f"exp:{e['slug']}") or place["images"][1:] or place["images"]
            e["themes"] = place.get("themes", [])
        for s in self.stays.values():
            place = self.places.get(s.get("place"))
            s["place_obj"] = place
            s["region_obj"] = self.regions[s["region"]]
            s["images"] = self._imgs(f"stay:{s['slug']}") or (place["images"] if place else [])
            s["journey_objs"] = [j for j in self.journeys.values() if s["slug"] in j.get("stays", [])]
        for j in self.journeys.values():
            j["region_obj"] = self.regions[j["region"]]
            stops = [dict(st, obj=self.places[st["place"]]) for st in j.get("stops", []) if st["place"] in self.places]
            j["stop_objs"] = stops
            j["images"] = self._imgs(f"journey:{j['slug']}") or [
                i for st in stops for i in st["obj"]["images"][:1]]
            j["stay_objs"] = [self.stays[s] for s in j.get("stays", []) if s in self.stays]
            j["best_label"] = best_range(j.get("best_months"))
            j["bar"] = month_bar(j.get("best_months"))
            j["days_count"] = j.get("nights", 0) + 1
            fares, notes = j.get("fares") or {}, j.get("fare_notes") or {}
            j["tiers"] = [{"key": k, "name": k.capitalize(), "inr": fares[k], "note": notes.get(k, "")}
                          for k in ("budget", "comfort", "premium") if k in fares]
            j["serial"] = f"{zlib.crc32(j['slug'].encode()) % 90000 + 10000:05d}"
            j["max_alt"] = max([st["obj"].get("altitude_m") or 0 for st in stops] + [j.get("max_altitude_m") or 0])
            for d in j.get("days", []):
                d["place_obj"] = self.places.get(d.get("place"))
        for g in self.guides.values():
            g["region_obj"] = self.regions[g["region"]]
            rel = [self.places[s] for s in g.get("related_places", []) if s in self.places]
            g["related_objs"] = rel
            g["images"] = self._imgs(f"guide:{g['slug']}") or [i for p in rel for i in p["images"][:1]] or g["region_obj"]["images"]
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in g.get("sections", []))
            g["read_min"] = max(3, round(words / 220))
            for s in g.get("sections", []):
                s["anchor"] = re.sub(r"[^a-z0-9]+", "-", s.get("heading", "").lower()).strip("-")
        for f in self.festivals.values():
            place = self.places.get(f.get("place"))
            f["place_obj"] = place
            f["region_obj"] = self.regions[f["region"]]
            f["images"] = self._imgs(f"fest:{f['slug']}") or (place["images"] if place else [])
        for rt in self.routes.values():
            rt["from_obj"] = self.places.get(rt.get("from"))
            rt["to_obj"] = self.places.get(rt.get("to"))
            rt["region_obj"] = self.regions[rt["region"]]
            rt["images"] = (rt["to_obj"] or {}).get("images", []) + (rt["from_obj"] or {}).get("images", [])[:1]
        for t in self.themes.values():
            t["url"] = reverse("theme", args=[t["slug"]])

    def _link_posts(self):
        from datetime import date
        for d in self.posts.values():
            d["region_objs"] = [self.regions[r] for r in d.get("regions", []) if r in self.regions]
            d["journey_objs"] = [self.journeys[j] for j in d.get("related_journeys", []) if j in self.journeys]
            d["place_objs"] = [self.places[x] for x in d.get("related_places", []) if x in self.places]
            d["images"] = (self._imgs(f"blog:{d['slug']}") or [i for x in d["place_objs"] for i in x["images"][:1]])
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
            d["read_min"] = max(3, round(words / 220))
            d["cat_slug"] = re.sub(r"[^a-z0-9]+", "-", d.get("category", "").lower()).strip("-")
            try:
                d["date_obj"] = date.fromisoformat(d.get("date", ""))
            except ValueError:
                d["date_obj"] = None
            land = d["region_objs"][0]["slug"] if d["region_objs"] else None
            d["land"] = land
            stores = {"journey": self.journeys, "place": self.places, "stay": self.stays, "guide": self.guides, "festival": self.festivals}
            for sec in d.get("sections", []):
                sec["anchor"] = re.sub(r"[^a-z0-9]+", "-", sec.get("heading", "").lower()).strip("-")
                objs = []
                for ln in sec.get("links", []):
                    o = stores.get(ln.get("type"), {}).get(ln.get("slug"))
                    if o:
                        objs.append({"type": ln["type"], "title": o.get("title") or o.get("name"), "url": o["url"],
                                     "img": (o.get("images") or [None])[0]})
                sec["link_objs"] = objs
        self.post_categories = OrderedDict()
        for d in self.posts.values():
            self.post_categories.setdefault(d["cat_slug"], {"slug": d["cat_slug"], "name": d.get("category"), "posts": []})["posts"].append(d)

    # ---------- queries ----------
    def theme_items(self, theme, region=None):
        def ok(x):
            return region is None or x.get("region") == region
        places = [p for p in self.places.values() if theme in p.get("themes", []) and ok(p)]
        journeys = [j for j in self.journeys.values() if theme in j.get("themes", []) and ok(j)]
        place_slugs = {p["slug"] for p in places}
        stays = [s for s in self.stays.values() if s.get("place") in place_slugs and ok(s)]
        experiences = [e for e in self.experiences.values() if e["place"] in place_slugs and ok(e)]
        return {"places": places, "journeys": journeys, "stays": stays, "experiences": experiences}

    def region_theme_pairs(self):
        """(region, theme) pairs with enough content to deserve a page."""
        out = []
        for r in self.regions:
            for t in self.themes:
                items = self.theme_items(t, r)
                if len(items["places"]) >= 2 and (items["journeys"] or len(items["places"]) >= 3):
                    out.append((r, t))
        return out

    def region_kind_pairs(self):
        """(region, kind) pairs with at least 3 experiences."""
        out = []
        for r in self.regions:
            for k in KINDS:
                if sum(1 for e in self.experiences.values() if e["region"] == r and e.get("kind") == k) >= 3:
                    out.append((r, k))
        return out

    def budget_journeys(self, limit=None, region=None):
        js = [j for j in self.journeys.values() if region is None or j["region"] == region]
        js.sort(key=lambda j: (j.get("price_from_inr") or 10 ** 9) / max(j.get("nights") or 1, 1))
        return js[:limit] if limit else js

    def budget_stays(self, region=None):
        return [s for s in self.stays.values() if s.get("tier") == "budget" and (region is None or s["region"] == region)]

    def counts(self):
        return {
            "regions": len(self.regions), "places": len(self.places), "experiences": len(self.experiences),
            "journeys": len(self.journeys), "stays": len(self.stays), "guides": len(self.guides),
            "festivals": len(self.festivals), "routes": len(self.routes), "themes": len(self.themes),
            "posts": len(self.posts),
        }

    def all_images(self):
        seen, out = set(), []
        for key, recs in self.images.items():
            for rec in recs:
                if rec["file"] not in seen:
                    seen.add(rec["file"])
                    out.append(dict(rec, used_for=key))
        return out
