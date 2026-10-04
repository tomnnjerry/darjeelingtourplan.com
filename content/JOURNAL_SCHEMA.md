# Stories (journal) schema

Stories are dated, answer-first articles at `/stories/<slug>/`, one file each in `content/journal/<slug>.json`.
All writing rules, banned words and fact rules in `SCHEMA.md` apply. Validate with `python tools/check_journal.py`.

```json
{
  "slug": "same-as-filename",
  "title": "≤ 65 chars, no full stop",
  "category": "Planning | Budget | Seasons | History | Food | Wildlife",   // free text; becomes /stories/topic/<slug>/
  "date": "2026-09-18",                                                  // ISO date
  "regions": ["darjeeling", "east-sikkim"],                              // first one sets the page colours
  "meta_description": "≤ 158 chars",
  "summary": "40–60 words, answer first",
  "key_takeaways": ["…", "…", "…", "…"],                                 // exactly 4
  "sections": [                                                          // 1,050+ words in total, at least one table
    {"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"],
     "table": {"head": ["…"], "rows": [["…"]]},                          // optional per section
     "links": [{"type": "journey | place | stay | guide | festival", "slug": "existing-slug"}]}   // optional
  ],
  "related_journeys": ["journey-slug"],                                  // optional
  "related_places": ["place-slug"],                                      // optional
  "cta": {"title": "≤ 40 chars", "text": "one sentence"},
  "faqs": [{"q": "…", "a": "40–90 words"}],                              // exactly 5
  "image_query": "3–6 words for a Commons photo", "wiki": ""            // optional
}
```
