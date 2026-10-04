import json
from datetime import date

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import KINDS, MONTH_SHORT, MONTHS, catalogue, month_bar
from .forms import EnquiryForm, SubscribeForm
from .models import Subscriber
from .policies import POLICIES, UPDATED

COMPANY_FAQS = [
    {"q": "What does Darjeeling Tour Plan do?",
     "a": "We plan trips in Darjeeling, Kalimpong, Sikkim, Bhutan and the Dooars, and nowhere else. You get a day-by-day plan, a car and driver or shared-jeep advice, hotels or homestays at the price level you choose, permits where they are needed and one person to call while you travel."},
    {"q": "Are your prices fixed?",
     "a": "No. Prices on the site are indicative 'from' prices in INR per person, twin sharing, starting at Bagdogra, NJP or Siliguri. Each package shows a budget, comfort and premium fare. Your final price depends on dates, hotel availability and vehicle type, and we send a written quote with every line listed before you pay anything."},
    {"q": "What is the cheapest way to do these hills?",
     "a": "Travel outside the peak weeks (April to mid-June, the October Puja holidays and Christmas to New Year), use shared jeeps on transfer days, stay in homestays or government tourist lodges, and plan two or three bases instead of five. Our budget fares are built this way; the affordable page explains each saving."},
    {"q": "Can you change a package on the site?",
     "a": "Yes, and most people do. The packages show routes that work. We swap hotels, add or drop nights, change the vehicle and combine lands, such as Darjeeling with Gangtok or the Dooars with Bhutan, then send a new plan and price."},
    {"q": "How far ahead should we book?",
     "a": "For the Puja holidays in October, Christmas week and April to June, book six to ten weeks ahead, because rooms and cars in Darjeeling, Gangtok and Pelling fill early. Bhutan festival dates and Dooars safari slots also go early. For the quieter months two to three weeks is usually enough."},
    {"q": "Who will we deal with?",
     "a": "One planner handles your trip from the first message to the drop at the airport or station, and is on WhatsApp while you travel. Drivers and homestay hosts are people we have used on the same routes."},
    {"q": "Where do your photos come from?",
     "a": "Every photo comes from Wikimedia Commons under a free licence. We name the author and licence under each photo and list all of them, with links to the originals, on our photo credits page."},
    {"q": "Do you arrange permits for Sikkim and Bhutan?",
     "a": "Yes. Restricted and protected areas in Sikkim (Tsomgo, Nathu La, North Sikkim, Zuluk, Dzongu) need permits applied for through registered operators, and Bhutan needs an entry permit and the Sustainable Development Fee. We tell you which documents to carry. Rules change: check current status before you travel."},
    {"q": "Is travel insurance included?",
     "a": "No. We recommend insurance that covers medical evacuation, and for North Sikkim, Nathu La or trekking routes, cover for the highest altitude on your route."},
]


def ld(*items):
    """Render JSON-LD blocks safely."""
    return [json.dumps(i, ensure_ascii=False).replace("</", "<\\/") for i in items]


def crumbs(*pairs):
    items = [("Home", reverse("home"))] + list(pairs)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": settings.SITE["url"] + u}
        for i, (n, u) in enumerate(items)]}
    return items, data


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]}


def img_url(obj):
    imgs = obj.get("images") or []
    return imgs[0]["thumb"] if imgs else None


def org_ld():
    s = settings.SITE
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": s["name"], "url": s["url"],
            "areaServed": ["Darjeeling", "Kalimpong", "Sikkim", "Bhutan", "Dooars"]}


def _get(store, slug):
    obj = store.get(slug)
    if not obj:
        raise Http404
    return obj


def _month_now():
    return date.today().month - 1


# ---------------- home and indexes ----------------
def home(request):
    cat = catalogue()
    regions = list(cat.regions.values())
    featured = []
    for r in regions:  # one mid-priced package per land
        js = sorted(r["journeys"], key=lambda j: j.get("price_from_inr", 0))
        if js:
            featured.append(js[len(js) // 2])
    for j in cat.budget_journeys():  # always full rows of four
        if featured and len(featured) % 4 == 0:
            break
        if j not in featured:
            featured.append(j)
    budget = [j for j in cat.budget_journeys() if j not in featured][:4]
    m = _month_now()
    in_season = [p for p in cat.places.values() if (p.get("best_months") or [0] * 12)[m] == 2 and p.get("images")][:8]
    if len(in_season) > 4 and len(in_season) % 4:
        in_season = in_season[:len(in_season) - len(in_season) % 4]
    fests = [f for f in cat.festivals.values() if (m + 1) in f.get("month_nums", []) or (m + 2) in f.get("month_nums", [])][:3]
    stories = [r for r in regions if r.get("story")][:3]
    facts = [(r, f) for r in regions for f in r.get("did_you_know", [])[:1]][:5]
    return render(request, "hills/home.html", {
        "regions": regions, "featured": featured[:8], "budget": budget,
        "min_price": min((j.get("price_from_inr") or 10 ** 9 for j in cat.journeys.values()), default=0), "month": MONTHS[m], "month_i": m,
        "in_season": in_season, "festivals": fests, "stories": stories, "facts": facts,
        "guides": [g for g in cat.guides.values() if g.get("category") in ("budget", "history")][:3],
        "themes": list(cat.themes.values()), "months_short": MONTH_SHORT, "months_full": MONTHS,
        "posts": list(cat.posts.values())[:3],
        "ld": ld(org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": settings.SITE["name"], "url": settings.SITE["url"]}),
    })


AFFORDABLE_FAQS = [
    {"q": "What is the cheapest month to visit Darjeeling and Sikkim?",
     "a": "Hotel rates are usually lowest in the monsoon (July to mid-September) and from mid-January to February, outside the Christmas and New Year week. The monsoon brings landslides and hidden mountains; late January and February bring cold, clear days and lower prices. Late November and early December balance price and views well."},
    {"q": "How much does a budget trip to Darjeeling cost?",
     "a": "A 3-night Darjeeling trip using a shared jeep from NJP or Siliguri, a clean budget hotel or homestay and local sightseeing by shared taxi can cost roughly ₹7,000 to ₹10,000 per person, twin sharing, plus food. A reserved car for sightseeing and a mid-range hotel roughly doubles that. These are indicative figures; check current rates."},
    {"q": "Is a shared jeep safe for families?",
     "a": "Shared jeeps are how most locals travel, on fixed routes from fixed stands, with drivers who know these roads. They are cramped, with ten or eleven passengers and luggage on the roof, so for small children, older travellers or long routes a reserved car is more comfortable. Ask for the front seats."},
    {"q": "Are homestays cheaper than hotels?",
     "a": "Usually, once meals are counted. Many village homestays charge a per-person rate that includes dinner and breakfast, often less than a budget hotel room plus meals in town. In Darjeeling and Gangtok town, budget hotels can be cheaper than homestays in peak weeks, so we compare both for your dates."},
    {"q": "What can we see for free?",
     "a": "Most monasteries, the Mall and Chowrasta in Darjeeling, MG Marg in Gangtok, many viewpoints and walks, village trails, haats and tea-garden roads cost nothing. Fees apply to the zoo and mountaineering institute, the Batasia Loop, ropeways, Tiger Hill vehicle entry, national parks and toy-train rides."},
    {"q": "Does the cheapest package skip anything important?",
     "a": "Our budget fares keep the same route, safety and permits as the comfort fare. The differences are hotel class, whether transfers are shared or reserved, the vehicle and how many meals are included. Each package lists exactly what its budget fare covers."},
]


def affordable(request):
    cat = catalogue()
    items, bc = crumbs(("Affordable trips", reverse("affordable")))
    cheap = cat.budget_journeys()
    bands = [
        {"key": "under-15k", "name": "Under ₹15,000"},
        {"key": "15-25k", "name": "₹15,000 – 25,000"},
        {"key": "25k-plus", "name": "₹25,000 and above"},
    ]
    return render(request, "hills/affordable.html", {
        "crumbs": items, "regions": list(cat.regions.values()), "cheap": cheap, "bands": bands, "faqs": AFFORDABLE_FAQS,
        "stays": cat.budget_stays(), "guides": [g for g in cat.guides.values() if g.get("category") == "budget"],
        "theme": cat.themes.get("budget-trips"),
        "ld": ld(bc, faq_ld(AFFORDABLE_FAQS)),
    })


def lands(request):
    cat = catalogue()
    items, bc = crumbs(("Destinations", reverse("lands")))
    return render(request, "hills/lands.html", {"regions": list(cat.regions.values()), "crumbs": items,
                                                "months_short": MONTH_SHORT, "ld": ld(bc)})


def region(request, region):
    cat = catalogue()
    r = _get(cat.regions, region)
    items, bc = crumbs(("Destinations", reverse("lands")), (r["name"], r["url"]))
    exps = [e for p in r["places"] for e in p.get("experiences", [])[:1]]
    styles = [cat.themes[t] for (rr, t) in cat.region_theme_pairs() if rr == region]
    months = [{"name": MONTHS[i], "slug": MONTHS[i].lower(), "rating": (r.get("best_months") or [0] * 12)[i],
               "weather": (r.get("months") or [{}] * 12)[i].get("weather", "") if i < len(r.get("months", [])) else ""}
              for i in range(12)]
    place_ld = {"@context": "https://schema.org", "@type": "TouristDestination", "name": r["name"],
                "description": r.get("summary"), "url": settings.SITE["url"] + r["url"],
                "includesAttraction": [{"@type": "TouristAttraction", "name": p["name"]} for p in r["places"]]}
    return render(request, "hills/region.html", {
        "r": r, "crumbs": items, "experiences": exps, "styles": styles, "months": months, "month_now": _month_now(),
        "kinds": [(k, KINDS[k][0]) for rr, k in cat.region_kind_pairs() if rr == region],
        "ld": ld(bc, place_ld, faq_ld(r.get("faqs", []))),
        "map_points": json.dumps([{"name": p["name"], "lat": p.get("lat"), "lng": p.get("lng"), "url": p["url"],
                                   "kind": p.get("kind", "")} for p in r["places"] if p.get("lat")]),
    })


def region_month(request, region, month):
    cat = catalogue()
    r = _get(cat.regions, region)
    names = [m.lower() for m in MONTHS]
    if month not in names:
        raise Http404
    i = names.index(month)
    md = r.get("months", [])[i] if i < len(r.get("months", [])) else {}
    go = [cat.places[s] for s in md.get("go", []) if s in cat.places]
    events = [cat.festivals[s] for s in md.get("events", []) if s in cat.festivals]
    journeys = [j for j in r["journeys"] if (j.get("best_months") or [0] * 12)[i] == 2]
    rating = (r.get("best_months") or [0] * 12)[i]
    others = [{"r": rr, "rating": (rr.get("best_months") or [0] * 12)[i]} for rr in cat.regions.values() if rr["slug"] != region]
    items, bc = crumbs(("Destinations", reverse("lands")), (r["name"], r["url"]), (f"{MONTHS[i]}", request.path))
    title = f"{r['name']} in {MONTHS[i]}"
    faqs = [
        {"q": f"Is {MONTHS[i]} a good time to visit {r['name']}?",
         "a": (md.get("summary") or "")[:600] or f"See our month-by-month notes for {r['name']}."},
        {"q": f"What is the weather like in {r['name']} in {MONTHS[i]}?",
         "a": f"{md.get('weather', 'Weather varies across the region')}. Conditions differ by altitude and coast, so check the forecast for each stop a week before you travel."},
        {"q": f"Where should we go in {r['name']} in {MONTHS[i]}?",
         "a": ("We suggest " + ", ".join(p["name"] for p in go) + ". " if go else "") + (md.get("tip") or "")},
    ]
    return render(request, "hills/region_month.html", {
        "r": r, "i": i, "month": MONTHS[i], "month_slug": names[i], "md": md, "go": go, "events": events, "journeys": journeys,
        "rating": rating, "others": others, "crumbs": items, "title": title, "faqs": faqs,
        "prev": names[(i - 1) % 12], "next": names[(i + 1) % 12], "prev_name": MONTHS[(i - 1) % 12], "next_name": MONTHS[(i + 1) % 12],
        "ld": ld(bc, faq_ld(faqs)),
    })


def region_theme(request, region, theme):
    cat = catalogue()
    r = _get(cat.regions, region)
    t = _get(cat.themes, theme)
    if (region, theme) not in cat.region_theme_pairs():
        raise Http404
    data = cat.theme_items(theme, region)
    items, bc = crumbs(("Destinations", reverse("lands")), (r["name"], r["url"]), (t["name"], request.path))
    return render(request, "hills/region_theme.html", {"r": r, "t": t, **data, "crumbs": items, "ld": ld(bc)})


def place(request, region, place):
    cat = catalogue()
    p = _get(cat.places, place)
    if p["region"] != region:
        return redirect(p["url"], permanent=True)
    r = p["region_obj"]
    items, bc = crumbs(("Destinations", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]))
    dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": p["name"],
            "description": p.get("summary"), "url": settings.SITE["url"] + p["url"], "image": img_url(p)}
    if p.get("lat"):
        dest["geo"] = {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lng"]}
    return render(request, "hills/place.html", {
        "p": p, "r": r, "crumbs": items, "ld": ld(bc, dest, faq_ld(p.get("faqs", []))),
        "map_points": json.dumps([{"name": x["name"], "lat": x.get("lat"), "lng": x.get("lng"), "url": x["url"], "main": x is p}
                                  for x in [p] + p["nearby_objs"] if x.get("lat")]),
    })


def experience(request, region, place, exp):
    cat = catalogue()
    e = _get(cat.experiences, exp)
    p = e["place_obj"]
    if p["slug"] != place or e["region"] != region:
        return redirect(e["url"], permanent=True)
    r = e["region_obj"]
    siblings = [x for x in p.get("experiences", []) if x is not e]
    items, bc = crumbs(("Destinations", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]), (e["title"], e["url"]))
    attraction = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": e["title"],
                  "description": e.get("summary"), "image": img_url(e),
                  "containedInPlace": {"@type": "Place", "name": p["name"]}}
    return render(request, "hills/experience.html", {
        "e": e, "p": p, "r": r, "siblings": siblings, "crumbs": items,
        "ld": ld(bc, attraction, faq_ld(e.get("faqs", []))),
    })


def journeys(request):
    cat = catalogue()
    items, bc = crumbs(("Tour packages", reverse("journeys")))
    return render(request, "hills/journeys.html", {"journeys": list(cat.journeys.values()), "regions": list(cat.regions.values()),
                                                   "themes": list(cat.themes.values()), "crumbs": items, "ld": ld(bc)})


def journey(request, slug):
    cat = catalogue()
    j = _get(cat.journeys, slug)
    r = j["region_obj"]
    items, bc = crumbs(("Tour packages", reverse("journeys")), (j["title"], j["url"]))
    trip = {"@context": "https://schema.org", "@type": "TouristTrip", "name": j["title"], "description": j.get("summary"),
            "image": img_url(j), "touristType": [cat.themes[t]["name"] for t in j.get("themes", []) if t in cat.themes],
            "itinerary": {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": s["obj"]["name"]}}
                for i, s in enumerate(j["stop_objs"])]},
            "offers": {"@type": "Offer", "priceCurrency": "INR", "price": j.get("price_from_inr"),
                       "description": "Indicative price per person, twin sharing"}}
    related = [x for x in r["journeys"] if x is not j][:4]
    return render(request, "hills/journey.html", {
        "j": j, "r": r, "crumbs": items, "related": related,
        "ld": ld(bc, trip, faq_ld(j.get("faqs", []))),
        "map_points": json.dumps([{"name": s["obj"]["name"], "lat": s["obj"].get("lat"), "lng": s["obj"].get("lng"),
                                   "url": s["obj"]["url"], "nights": s["nights"]} for s in j["stop_objs"] if s["obj"].get("lat")]),
    })


def stays(request):
    cat = catalogue()
    items, bc = crumbs(("Stays", reverse("stays")))
    return render(request, "hills/stays.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def stay(request, slug):
    cat = catalogue()
    s = _get(cat.stays, slug)
    items, bc = crumbs(("Stays", reverse("stays")), (s["name"], s["url"]))
    hotel = {"@context": "https://schema.org", "@type": "Hotel", "name": s["name"], "description": s.get("summary"),
             "image": img_url(s), "address": {"@type": "PostalAddress", "addressLocality": (s.get("place_obj") or {}).get("name", "")}}
    if s.get("website"):
        hotel["sameAs"] = s["website"]
    others = [x for x in s["region_obj"]["stays"] if x is not s][:3]
    return render(request, "hills/stay.html", {"s": s, "crumbs": items, "others": others,
                                               "ld": ld(bc, hotel, faq_ld(s.get("faqs", [])))})


def experiences(request):
    cat = catalogue()
    items, bc = crumbs(("Experiences", reverse("experiences")))
    kinds = sorted({e.get("kind", "") for e in cat.experiences.values() if e.get("kind")})
    return render(request, "hills/experiences.html", {"regions": list(cat.regions.values()), "kinds": kinds,
                                                      "kind_links": [(k, v[0]) for k, v in KINDS.items()],
                                                      "count": len(cat.experiences), "crumbs": items, "ld": ld(bc)})


def _kind_page(request, kind, region=None):
    cat = catalogue()
    if kind not in KINDS:
        raise Http404
    name, tagline, intro = KINDS[kind]
    exps = [e for e in cat.experiences.values() if e.get("kind") == kind and (region is None or e["region"] == region)]
    r = cat.regions.get(region) if region else None
    if region and (not r or (region, kind) not in cat.region_kind_pairs()):
        raise Http404
    trail = [("Experiences", reverse("experiences"))]
    if r:
        trail = [("Destinations", reverse("lands")), (r["name"], r["url"]), (f"{name} experiences", request.path)]
    else:
        trail.append((name, request.path))
    items, bc = crumbs(*trail)
    lands = [cat.regions[rr] for rr, k in cat.region_kind_pairs() if k == kind]
    others = [(k, v[0]) for k, v in KINDS.items() if k != kind and (region is None or (region, k) in cat.region_kind_pairs())]
    return render(request, "hills/experience_kind.html", {
        "kind": kind, "name": name, "tagline": tagline, "intro": intro, "exps": exps, "r": r,
        "lands": lands, "others": others, "crumbs": items, "ld": ld(bc)})


def experience_kind(request, kind):
    return _kind_page(request, kind)


def region_kind(request, region, kind):
    return _kind_page(request, kind, region)


def guides(request):
    cat = catalogue()
    items, bc = crumbs(("Guides", reverse("guides")))
    return render(request, "hills/guides.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def guide(request, slug):
    cat = catalogue()
    g = _get(cat.guides, slug)
    r = g["region_obj"]
    items, bc = crumbs(("Guides", reverse("guides")), (g["title"], g["url"]))
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g.get("summary"),
               "image": img_url(g), "author": {"@type": "Organization", "name": settings.SITE["byline"]},
               "publisher": {"@type": "Organization", "name": settings.SITE["name"]}}
    more = [x for x in r["guides"] if x is not g][:3]
    return render(request, "hills/guide.html", {"g": g, "r": r, "crumbs": items, "more": more,
                                                "ld": ld(bc, article, faq_ld(g.get("faqs", [])))})


def festivals(request):
    cat = catalogue()
    items, bc = crumbs(("Festivals", reverse("festivals")))
    by_month = []
    for i, m in enumerate(MONTHS):
        fs = [f for f in cat.festivals.values() if (i + 1) in f.get("month_nums", [])]
        by_month.append({"name": m, "festivals": fs})
    return render(request, "hills/festivals.html", {"by_month": by_month, "count": len(cat.festivals), "crumbs": items, "ld": ld(bc)})


def festival(request, slug):
    cat = catalogue()
    f = _get(cat.festivals, slug)
    items, bc = crumbs(("Festivals", reverse("festivals")), (f["name"], f["url"]))
    journeys = [j for j in f["region_obj"]["journeys"] if "festivals" in j.get("themes", [])][:3]
    return render(request, "hills/festival.html", {"f": f, "crumbs": items, "journeys": journeys,
                                                   "bar": month_bar([2 if (i + 1) in f.get("month_nums", []) else 0 for i in range(12)]),
                                                   "ld": ld(bc, faq_ld(f.get("faqs", [])))})


def routes(request):
    cat = catalogue()
    items, bc = crumbs(("Routes", reverse("routes")))
    return render(request, "hills/routes.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def route(request, slug):
    cat = catalogue()
    rt = _get(cat.routes, slug)
    if not (rt["from_obj"] and rt["to_obj"]):
        raise Http404
    items, bc = crumbs(("Routes", reverse("routes")), (f"{rt['from_obj']['name']} to {rt['to_obj']['name']}", rt["url"]))
    pts = [x for x in (rt["from_obj"], rt["to_obj"]) if x and x.get("lat")]
    return render(request, "hills/route.html", {"rt": rt, "crumbs": items, "ld": ld(bc, faq_ld(rt.get("faqs", []))),
                                                "map_points": json.dumps([{"name": x["name"], "lat": x["lat"], "lng": x["lng"], "url": x["url"]} for x in pts])})


def themes(request):
    cat = catalogue()
    items, bc = crumbs(("Trip styles", reverse("themes")))
    rows = [{"t": t, "n": len(cat.theme_items(t["slug"])["journeys"])} for t in cat.themes.values()]
    return render(request, "hills/themes.html", {"rows": rows, "crumbs": items, "ld": ld(bc)})


def theme(request, slug):
    cat = catalogue()
    t = _get(cat.themes, slug)
    data = cat.theme_items(slug)
    pairs = [cat.regions[r] for (r, tt) in cat.region_theme_pairs() if tt == slug]
    items, bc = crumbs(("Trip styles", reverse("themes")), (t["name"], t["url"]))
    return render(request, "hills/theme.html", {"t": t, **data, "region_pages": pairs, "crumbs": items, "ld": ld(bc)})


def seasons(request):
    cat = catalogue()
    items, bc = crumbs(("Seasons", reverse("seasons")))
    return render(request, "hills/seasons.html", {"regions": list(cat.regions.values()), "months": MONTHS,
                                                  "months_short": MONTH_SHORT, "crumbs": items, "ld": ld(bc)})


# ---------------- tools ----------------
def tools(request):
    items, bc = crumbs(("Trip tools", reverse("tools")))
    return render(request, "hills/tools.html", {"crumbs": items, "ld": ld(bc)})


def tool_season(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Season finder", reverse("tool_season")))
    data = [{"n": p["name"], "u": p["url"], "r": p["region_obj"]["name"], "rs": p["region"], "b": p.get("best_months") or [0] * 12,
             "k": p.get("kind", ""), "i": (p["images"][0]["thumb"] if p["images"] else "")} for p in cat.places.values()]
    return render(request, "hills/tool_season.html", {"crumbs": items, "data": json.dumps(data).replace("</", "<\\/"), "months": MONTHS, "ld": ld(bc),
                                                      "regions": list(cat.regions.values()), "now": _month_now()})


def tool_budget(request):
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Trip cost calculator", reverse("tool_budget")))
    return render(request, "hills/tool_budget.html", {"crumbs": items, "ld": ld(bc), "regions": list(catalogue().regions.values())})


def tool_permits(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Permits", reverse("tool_permits")))
    return render(request, "hills/tool_permits.html", {"crumbs": items, "ld": ld(bc), "regions": list(cat.regions.values())})


# ---------------- enquiry ----------------
def plan(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plan_thanks")
    else:
        initial = {"source_page": request.GET.get("from", "")[:300], "kind": "full"}
        if request.GET.get("land"):
            initial["lands"] = [request.GET["land"]]
        if request.GET.get("budget") in ("under-15k", "15-25k", "25-50k", "50k-plus"):
            initial["budget"] = request.GET["budget"]
        if request.GET.get("month") in MONTHS:
            initial["month"] = request.GET["month"]
        if request.GET.get("journey"):
            initial["message"] = f"I am interested in: {request.GET['journey'][:150]}"
        form = EnquiryForm(initial=initial)
    items, bc = crumbs(("Plan a trip", reverse("plan")))
    return render(request, "hills/plan.html", {"form": form, "crumbs": items, "ld": ld(bc)})


def plan_thanks(request):
    return render(request, "hills/plan_thanks.html", {"crumbs": crumbs(("Plan a trip", reverse("plan")))[0]})


# ---------------- static and utility ----------------
def old_policy(request, page):
    return redirect("policy", slug={"privacy": "privacy", "terms": "booking-terms"}[page], permanent=True)


def static_page(request, page):
    titles = {"about": "About us", "privacy": "Privacy", "terms": "Terms"}
    items, bc = crumbs((titles[page], request.path))
    return render(request, f"hills/{page}.html", {"crumbs": items, "counts": catalogue().counts(), "ld": ld(bc)})


def faq(request):
    cat = catalogue()
    items, bc = crumbs(("FAQ", reverse("faq")))
    groups = [{"name": "Travelling with us", "faqs": COMPANY_FAQS}] + [
        {"name": r["name"], "faqs": r.get("faqs", []), "url": r["url"]} for r in cat.regions.values()]
    return render(request, "hills/faq.html", {"groups": groups, "crumbs": items, "ld": ld(bc, faq_ld(COMPANY_FAQS))})


def photo_credits(request):
    cat = catalogue()
    items, bc = crumbs(("Photo credits", reverse("photo_credits")))
    return render(request, "hills/photo_credits.html", {"images": cat.all_images(), "crumbs": items, "ld": ld(bc)})


def html_sitemap(request):
    cat = catalogue()
    items, bc = crumbs(("Sitemap", reverse("html_sitemap")))
    return render(request, "hills/sitemap.html", {"cat": cat, "regions": list(cat.regions.values()), "crumbs": items,
                                                  "pairs": [(cat.regions[r], cat.themes[t]) for r, t in cat.region_theme_pairs()],
                                                  "kind_pairs": [(cat.regions[r], k, KINDS[k][0]) for r, k in cat.region_kind_pairs()],
                                                  "month_slugs": [(m, m.lower()) for m in MONTHS], "ld": ld(bc)})


def robots(request):
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /plan/thank-you/\n\nSitemap: {settings.SITE['url']}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def llms(request):
    cat = catalogue()
    lines = [f"# {settings.SITE['name']}", "",
             "> Affordable, well-planned trips in Darjeeling, Kalimpong, Sikkim, Bhutan and the Dooars, with budget, comfort and premium fares, permits and local stories.", ""]
    for r in cat.regions.values():
        lines.append(f"## {r['name']}")
        lines.append(f"- [{r['name']} overview]({settings.SITE['url']}{r['url']}): {r.get('summary', '')}")
        for p in r["places"]:
            lines.append(f"- [{p['name']}]({settings.SITE['url']}{p['url']}): {p.get('summary', '')}")
        for j in r["journeys"]:
            lines.append(f"- [{j['title']}]({settings.SITE['url']}{j['url']}): {j.get('summary', '')}")
        lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def not_found(request, exception=None):
    return render(request, "hills/404.html", {"crumbs": []}, status=404)
