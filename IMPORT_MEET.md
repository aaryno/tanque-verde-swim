# Importing a meet

The routine after every meet with a Hy-Tek results export (`.cl2` / `.hy3`, usually a zip
from the coach). Proven on the Arena High School Classic (Oct 17, 2026, timed finals) and the
Southern Arizona Regional Qualifier (Oct 23–24, 2026, prelims + finals).

## 0. Keep the source

Unzip into a **new, empty directory** (it is untrusted input), then keep the original files:
`~/workspaces/tv-swim/incoming/<YYYY-MM-DD>-<meet-slug>/` (both files plus the zip). The
importer records the `.cl2`'s name and SHA-256 in the meet file, so every row traces back to it.

Branch first: `git switch -c import/<slug>`.

## 1. Report

```bash
python3 scripts/import_meet.py "<path>.cl2" --meet "<Meet Name>" --report-only
# prelims/finals meet: add --finals-date YYYY-MM-DD
```

- **`--meet`** is the name as the records should show it, using the season schedule's name
  (`data/season_<season>.json`), not the file's abbreviation.
- **`--finals-date`**: the `.cl2` carries only the prelim day for individual swims. If the file
  has prelim times the importer refuses to run without this flag. Check it against the `.hy3`:
  `E2P` lines carry the prelim date and `E2F` lines the finals date (columns 88–95).
- Both rounds are kept, one row per swim. A prelim swim is official and counts for records
  and season bests.

The report lists every school (Open) and class record the meet breaks, and where each relay
lands on the relay lists. **Verify each line before you act on it:** look at the swim in the
`.hy3` (`E2F`/`E2P` and the `G1` splits), and confirm the swimmer's grade.

## 2. Records — the hand-kept sources of truth

For each RECORD line:

1. `records/records-<gender>.md`: replace the grade row, and the **Open** row (bold) if the
   report says Open. Use the date the swim was swum (`Oct 24, 2026`) and the meet name.
2. `data/class_records_history.json`: append one entry per **class** record, with
   `previous` set to the class record it replaced. An Open-only change needs no entry of its own
   (an Open record is always also a class record). Keep the file's format: `json.dumps(...,
   indent=2, ensure_ascii=False)`. A swimmer may lower the same class record twice in a season.
   The guard accepts that only when the newer entry's `previous` is exactly the older one.

For each RELAY line: insert the row into `records/relay-records-<gender>.md` at its rank and
renumber. Rows are not dropped off the bottom (the Arena import set this precedent).

**Identity:** names go through `data/swimmer_aliases.json` only. Never merge two swimmers
because their names look alike: siblings share surnames (Olsson, Radomsky, Alitiem, Caballero,
Lightcap). An unknown spelling is a question for Aaryn, recorded in the alias table once he
answers.

## 3. Rebuild

```bash
python3 scripts/import_meet.py "<path>.cl2" --meet "<Meet Name>" [--finals-date …]
```

The script re-imports (idempotent) and updates `results_so_far` in the season file. It then
re-harvests the season Top 10 (MaxPreps plus every meet file; MaxPreps copies of the same swims
are dropped), runs `apply_aliases.py`, the all-time rebuild and `build_season_summary.py`, and
finally `generate_website.py`, which runs the guards. A red guard stops the import. Fix the
cause; never override it.

Then check:

- `python3 scripts/validate_records.py`, `check_relay_split_attachment.py` and
  `check_class_records_history.py`. All must pass.
- The meet page `docs/meets/<date>-<slug>.html`: read its story and top swims as a family would.
  Every claim must be true.
- The home page teaser and the season phase line.

## 4. Publish

The steps follow `~/workspaces/tv-swim` RULE 1 and the coordination protocol:

1. BOARD line **before** the merge: what is changing, and the rollback sha (current `main`).
2. Commit with the records named in the message. Push, open a PR, merge.
3. **Published means seen on the live site.** A successful merge is not enough. Poll
   [tanqueverdeswim.org](https://tanqueverdeswim.org) until the new meet page and the new
   record times appear (GitHub Pages takes 1–3 minutes, sometimes much longer).
4. BOARD receipt **after** you have seen it live, naming the merge sha and the rollback sha.
