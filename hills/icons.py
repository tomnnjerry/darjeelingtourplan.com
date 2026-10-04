"""Line icons (24×24, stroke = currentColor). One per land, one per experience kind, one per style, plus UI icons.

Drawn for this site; render with {% icon "darjeeling" %} or {% icon "darjeeling" "icon--lg" %}.
"""

ICONS = {
    # ---- lands
    "darjeeling":  # B-class toy-train engine on the 2-foot line
        '<path d="M2 20.5h20"/><path d="M4 16.5V11h9v5.5"/><path d="M13 16.5V7.5h5.5v9"/><path d="M12 7.5h7.5"/>'
        '<path d="M6 11V8.2h2V11"/><path d="M5.6 6c-.2-1.3.8-2.3 2-2.2.4-1 1.8-1.4 2.6-.6"/><path d="M15 10h2"/>'
        '<path d="M3 16.5h17"/><circle cx="6.5" cy="18.4" r="1.4"/><circle cx="10.5" cy="18.4" r="1.4"/><circle cx="16" cy="18.4" r="1.4"/>',
    "kalimpong":  # orchid: dorsal sepal, petals, lip and stem
        '<path d="M12 11.5c-1.2-2.8-1.2-5.6 0-8 1.2 2.4 1.2 5.2 0 8z"/><path d="M12 11.5c-3-.6-5.8-.2-8 1.2 2.6 1 5.4.8 8-1.2z"/>'
        '<path d="M12 11.5c3-.6 5.8-.2 8 1.2-2.6 1-5.4.8-8-1.2z"/><path d="M12 11.5c-1.8 1.4-3.6 3.6-4 6M12 11.5c1.8 1.4 3.6 3.6 4 6"/>'
        '<path d="M10.2 13c0 2.2.8 3.8 1.8 3.8s1.8-1.6 1.8-3.8"/><path d="M12 16.8V21"/>',
    "east-sikkim":  # Tsomgo: peaks, a high lake and a line of prayer flags
        '<path d="M2 14.5l5-7 3.2 4.2L13.5 7l6.5 7.5"/><path d="M5.5 10.2l1.5 1.3 1.2-1"/><ellipse cx="12" cy="18" rx="8.5" ry="2.6"/>'
        '<path d="M8 18h3M13.5 18.6h2.5"/><path d="M2.5 3.5c3.2 1.6 6.5 1.6 9.5.4"/><path d="M5 4.5v2l1.4-.6M8.5 4.9v2l1.4-.6"/>',
    "north-sikkim":  # yak head with sweeping horns
        '<path d="M8 10.5C5.5 10.3 3.6 8.4 3.8 5"/><path d="M16 10.5c2.5-.2 4.4-2.1 4.2-5.5"/>'
        '<path d="M8 10.5h8l-1 5.8c-.5 2.6-1.6 4.2-3 4.2s-2.5-1.6-3-4.2z"/><path d="M8 10.5c-1.6-.2-3 .6-4 1.8M16 10.5c1.6-.2 3 .6 4 1.8"/>'
        '<path d="M10 13.6h.01M14 13.6h.01"/><path d="M11 18h2"/>',
    "west-sikkim":  # chorten in front of Kangchenjunga's five peaks
        '<path d="M2 11.5l3.5-4 2 2 2.5-4.5 2 2.5 2-3.5 2.5 4 2-1.5L22 11.5"/><path d="M7 21h10"/><path d="M8.2 21v-2h7.6v2"/>'
        '<path d="M8.8 19a3.2 3.2 0 0 1 6.4 0"/><path d="M10.8 15.8h2.4v-1.6h-2.4z"/><path d="M11.4 14.2L12 11l.6 3.2"/><path d="M12 11V9.8"/>',
    "bhutan":  # dzong: tapering walls, central utse tower, layered roofs
        '<path d="M2 21h20"/><path d="M4 21l1-7.5h14l1 7.5"/><path d="M3.5 13.5h17"/><path d="M8.2 13.5l.4-4.8h6.8l.4 4.8"/>'
        '<path d="M6.8 8.7h10.4l-1.6-2.2H8.4z"/><path d="M12 6.5V3.5"/><path d="M10.4 21v-3.2h3.2V21"/><path d="M9.5 11h.01M14.5 11h.01M6.5 16.5h.01M17.5 16.5h.01"/>',
    "dooars":  # one-horned rhinoceros
        '<path d="M4.5 17v-2.6c-1-.7-1.5-1.8-1.3-3.1C3.6 9.4 5.6 8 8.6 8h5.6c1.6 0 2.8.6 3.6 1.6l1.5-2.2.5 2.7c1 .6 1.7 1.6 1.7 2.9h-2.8l-.6 1"/>'
        '<path d="M8.2 17v-2.4M14 17v-2.2M17.4 17v-3"/><path d="M3.8 17h1.6M7.6 17h1.6M13.4 17h1.6M16.8 17h1.6"/>'
        '<path d="M17.1 11h.01"/><path d="M15.5 8.4l.6-1.4"/>',
    # ---- experience kinds
    "culture":  # hill bungalow with chimney
        '<path d="M3 21h18"/><path d="M5 21v-9h14v9"/><path d="M3 12l9-7 9 7"/><path d="M16 7.4V4h2v5"/><path d="M10 21v-4h4v4"/><path d="M7 14.5h2M15 14.5h2"/>',
    "spiritual":  # prayer wheel
        '<rect x="7" y="6" width="10" height="9" rx="1.5"/><path d="M7 9h10M7 12h10"/><path d="M12 6V3.5"/><path d="M12 15v6"/>'
        '<path d="M17 10.5c2 0 3 .8 3 2"/><circle cx="20" cy="13.6" r="1"/>',
    "nature": '<path d="M2 20l7-11 4 6 3-4 6 9z"/><circle cx="17.5" cy="5.5" r="2"/>',
    "wildlife": '<circle cx="6" cy="10" r="1.8"/><circle cx="10" cy="6" r="1.8"/><circle cx="14" cy="6" r="1.8"/><circle cx="18" cy="10" r="1.8"/>'
                '<path d="M8 17c0-3 1.8-5 4-5s4 2 4 5c0 2-1.8 3-4 3s-4-1-4-3z"/>',
    "food":  # momo on a steamer
        '<path d="M4.5 14.5c0-4.2 3.4-7.5 7.5-7.5s7.5 3.3 7.5 7.5z"/><path d="M12 7v3.2M9 7.8l1 2.6M15 7.8l-1 2.6"/>'
        '<path d="M3 14.5h18"/><path d="M4.5 17.5h15"/><path d="M6 14.5v5.5h12v-5.5"/>',
    "adventure":  # summit flag
        '<path d="M2 20l7-12 4 6 2-3 7 9z"/><path d="M9 8V3l4 1.5L9 6"/>',
    "tea":  # two leaves and a bud
        '<path d="M12 21c-.5-5.5 1.5-10 7-13.5.5 6.5-2 11-7 13.5z"/><path d="M12 21c-4-1.5-7-5-7-10.5 4 1.5 6.5 4.5 7 10.5z"/>'
        '<path d="M12 21c.3-3 1.5-6 4-8.5M12 21c-1-2.5-2.5-5-5-7"/><path d="M12.5 7c-.8-1.6-.6-3 .5-4 1 1.2.9 2.6-.5 4z"/>',
    "rail":  # narrow-gauge track running uphill
        '<path d="M8.5 3L5 21M15.5 3L19 21"/><path d="M8 6h8M7.3 9.5h9.4M6.6 13h10.8M5.9 16.5h12.2M5.2 20h13.6"/>',
    "village":  # farmhouse with chimney smoke
        '<path d="M3 21h18"/><path d="M5 21v-8l7-5 7 5v8"/><path d="M10 21v-5h4v5"/><path d="M16 9.6V6h2v5"/><path d="M17 4c0-1 1-1.5 1-2.5"/>',
    "craft":  # thangka scroll
        '<path d="M5 3h14M6 3v16h12V3"/><path d="M4 19h16"/><circle cx="12" cy="9.5" r="3"/><path d="M9 15h6"/><path d="M10 19v2M14 19v2"/>',
    # ---- styles
    "ticket": '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M15 7.5v1.5M15 11v2M15 15v1.5"/>',
    "family": '<circle cx="7.5" cy="6" r="2"/><circle cx="16.5" cy="6" r="2"/><circle cx="12" cy="12" r="1.5"/>'
              '<path d="M4 21v-7a3.5 3.5 0 0 1 7 0M13 21v-7a3.5 3.5 0 0 1 7 0"/><path d="M10 21v-3a2 2 0 0 1 4 0v3"/>',
    "bird": '<path d="M3 13c3 0 5-1.5 6.5-4S13.5 5 16 5c1.5 0 2.5.6 3 1.5L21 7l-2 1c0 5-3.5 9-9 9H6z"/><path d="M9 17l-1.5 4M12 17l.5 4"/><path d="M16.5 7.5h.01"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    # ---- UI
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "jeep": '<path d="M3 16v-5l2-4h10l3 4h3v5"/><path d="M3 16h18"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5.5 11h13M10.5 7v4"/>',
    "altitude": '<path d="M2 20l6-10 4 6 3-4 7 8z"/><path d="M19 9V3M17 5l2-2 2 2"/>',
    "rupee": '<path d="M7 4h10M7 8h10M8 4c4.5 0 6 1.8 6 4s-1.5 4-6 4h-1l7 8"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "bed": '<path d="M3 18V7M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3"/><circle cx="7" cy="11" r="1.6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "flags": '<path d="M2 5.5c5 3.5 15 3.5 20 0"/><path d="M5 7.1v4.4l2.8-1.4M9.5 8.1v4.4l2.8-1.4M14.5 8.1v4.4l2.8-1.4M18.6 7.2v4.4l2.4-1.2"/>',
    "star": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
}


def svg(name, cls=""):
    body = ICONS.get(name) or ICONS["sparkle"]
    return (f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')
