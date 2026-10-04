# darjeelingtourplan.com

Django site for Darjeeling Tour Plan: affordable, well-run trips in the Darjeeling hills, Kalimpong, Gangtok and
East Sikkim, North Sikkim, West and South Sikkim, Bhutan and the Dooars.

Every page is rendered from JSON in `content/` (no database content). The database only stores enquiries and
newsletter sign-ups, which appear in the Django admin.

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser        # to read enquiries at /admin/
python manage.py runserver
```

With `DJANGO_DEBUG=1` (the default) the content reloads when any JSON file changes.

## Content

- `content/SCHEMA.md` describes every file type (regions, places, journeys, stays, guides, festivals, routes)
  and the house writing rules.
- `content/JOURNAL_SCHEMA.md` describes the dated stories under `/stories/`.
- `content/themes.json` holds the trip styles; `content/outlines.json` the map outlines (`tools/build_outlines.py`).
- `content/images.json` holds credited Wikimedia Commons photos. Build or refresh it with
  `python tools/fetch_images.py [region ...]` (incremental; `--force` to redo).

Check content before committing:

```bash
python tools/check_region.py darjeeling --wiki   # one land; --wiki confirms Wikipedia titles exist
python tools/check_journal.py                    # stories
python tools/smoke.py                            # renders every URL in the sitemap
```

## Configuration (environment variables)

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Required in production |
| `DJANGO_DEBUG` | `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names |
| `DTP_EMAIL`, `DTP_PHONE`, `DTP_WHATSAPP` | Contact details shown site-wide (WhatsApp: digits with country code) |
| `DTP_GA4` | Optional Google Analytics 4 ID |
| `DTP_HASHED_STATIC` | `1` after `collectstatic` for cache-busting file names |

## Before launch

Placeholders in square brackets still need real business details:

- `dtp/settings.py` → `SITE["address"]` and `SITE["hours"]` (email/phone come from the env vars above).
- `templates/hills/about.html` → legal name, tourism registration number, GSTIN.
- `hills/policies.py` → deposit and cancellation percentages, payment methods and gateway, complaints email,
  court city, and the other `[…]` values. Have these terms reviewed before taking bookings.
- `templates/hills/how_we_work.html` → deposit and balance terms (keep in line with the policies).

## Deploy

```bash
export DJANGO_DEBUG=0 DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=darjeelingtourplan.com,www.darjeelingtourplan.com
python manage.py migrate
python manage.py collectstatic --noinput
DTP_HASHED_STATIC=1 gunicorn dtp.wsgi        # or any WSGI server; WhiteNoise serves /static/
```
