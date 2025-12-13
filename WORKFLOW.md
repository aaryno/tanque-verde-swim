# Tanque Verde Swimming Website - Maintenance Workflow

**Last Updated:** December 12, 2025

> **📖 Primary Documentation:** See `claude.md` for comprehensive project context, script categories, data formats, and all workflows.

This document provides quick-reference commands for common maintenance tasks.

---

## Quick Commands

### Regenerate Entire Website
```bash
python3 scripts/generate_website.py
git add -A && git commit -m "Regenerate website" && git push
```

### After Adding New Records
```bash
# Edit records/records-boys.md or records/records-girls.md
# Then:
python3 scripts/generate_website.py
git add -A && git commit -m "New record: [event] [time] [athlete]" && git push
```

### After Adding Class Records
```bash
# Edit data/class_records_history.json
# Then:
python3 scripts/enrich_previous_record_locations.py
python3 scripts/generate_website.py
git add -A && git commit -m "Add class records for 20XX-XX" && git push
```

### After Updating Relay Splits
```bash
# Edit data/historical_splits/splits_YYYY-YY.json
# Then:
python3 scripts/rebuild_relay_pages.py
git add -A && git commit -m "Update relay splits" && git push
```

---

## Script Reference

| Command | Purpose |
|---------|---------|
| `python3 scripts/generate_website.py` | Regenerate all HTML pages |
| `python3 scripts/generate_annual_pages.py` | Regenerate only annual summary pages |
| `python3 scripts/rebuild_relay_pages.py` | Regenerate only relay pages |
| `python3 scripts/enrich_previous_record_locations.py` | Add meet info to previous records |

---

## File Locations

### Edit These (Source of Truth)
- `records/records-boys.md` - Boys individual records
- `records/records-girls.md` - Girls individual records  
- `records/relay-records-boys.md` - Boys relay records
- `records/relay-records-girls.md` - Girls relay records
- `data/class_records_history.json` - Class records with history

### Generated Output (Don't Edit)
- `docs/records/*.html` - Generated from markdown
- `docs/top10/*.html` - Generated from markdown
- `docs/annual/*.html` - Generated from markdown

### Manual Maintenance
- `docs/index.html` - Splash page (edit directly)
- `docs/css/style.css` - Website styling

---

## Detailed Documentation

For complete documentation including:
- Python environment setup
- Data file formats with examples
- Script categories and purposes
- Troubleshooting guide
- Relationship to swim-data-tool

See: **`claude.md`**

---

## Contact

**Maintainer:** aaryno@gmail.com

