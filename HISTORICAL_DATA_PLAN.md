# Historical State Championship Data Import Plan

## Data Sources on AZPreps365

### 1. Championship Results PDFs (2001-2025)
Full meet results with all swimmers from state meets.
- URL pattern: `https://aiaonline.org/files/[meet_id]/[filename].pdf`
- Contains: All finishers, prelim/final times, school names, grades

### 2. State Record Books (NOT useful for TV)
- Boys: `https://www.aiaonline.org/files/10102/boys-swimming-diving-records.pdf`
- Girls: `https://www.aiaonline.org/files/16643/girls-swimming-diving-records.pdf`
- Contains: Top 20 all-time performances in Arizona (state-wide)
- **Note**: Tanque Verde is NOT on these lists - dominated by D-I powerhouses

## Data Availability

### Current Data
- **Season files**: 2012-13 through 2024-25 (invitational meets from MaxPreps)
- **Earliest recorded swim**: October 2012

### Available Historical Data (AZPreps365 State Championships)

The AZPreps365 archives contain state championship results from **2001 to 2025**:

| Year | Meet ID | Meet Name |
|------|---------|-----------|
| 2001 | 7171 | 2001 Swimming and Diving 4A-5A State Championships |
| 2002 | 7268 | 2002 Swimming and Diving 5A State Championships |
| 2003 | 3826 | 2003 Swimming and Diving 5A State Championships |
| 2004 | 722 | 2004 Swimming and Diving 4A-5A State Championships |
| 2005 | 4023 | 2005 Swimming and Diving 4A-5A State Championships |
| 2006 | 6039 | 2006 Swimming and Diving 4A-5A State Championships |
| 2007 | 7844 | 2007 Swimming and Diving 1A-5A State Championships |
| 2008 | 9361 | 2008 Swimming and Diving 1A-5A State Championships |
| 2009 | 10504 | 2009 Swimming and Diving 1A-5A State Championships |
| 2010 | 11757 | 2010 Swimming and Diving Divisions I-II State Championships |
| 2011 | 12611 | 2011 Swimming and Diving Divisions I-II State Championships |
| 2012 | 13462 | 2012 Swimming and Diving Divisions I-II State Championships |
| 2013 | 14249 | 2013 Swimming and Diving Divisions I-II State Championships |
| 2014 | 14651 | 2014 Swimming and Diving Divisions I-II State Championships |
| 2015 | 15247 | 2015 Swimming and Diving Divisions I-II State Championships |
| 2016 | 15661 | 2016 Swimming and Diving Divisions I-III State Championships |
| 2017 | 16054 | 2017 Swimming and Diving Divisions I-III State Championships |
| 2018 | 16553 | 2018 Swimming and Diving Divisions I-III State Championships & Meet of Champions |
| 2019 | 16845 | 2019 Swimming and Diving Divisions I-III State Championships & Meet of Champions |
| 2020 | 17252 | 2020 Swimming and Diving Divisions I-III State Championships |
| 2021 | 17672 | 2021 Swimming and Diving Divisions I-III State Championships |
| 2022 | 17935 | 2022 Swimming and Diving Divisions I-III State Championships |
| 2023 | 18187 | 2023 Swimming and Diving Divisions I-III State Championships |
| 2024 | 18411 | 2024 Swimming and Diving Divisions I-III State Championships |
| 2025 | 18602 | 2025 Swimming and Diving Divisions I-III State Championships |

**Note:** Girls archives available at: https://azpreps365.com/archives/swimming-girls

## Tanque Verde Participation (Verified)

PDFs downloaded and analyzed for Tanque Verde mentions:

| Year | PDF Downloaded | TV Mentions | Notes |
|------|----------------|-------------|-------|
| 2001 | ✓ | 0 | TV not competing at state level |
| 2002 | ✓ | 0 | TV not competing at state level |
| 2003 | ✓ | 0 | TV not competing at state level |
| 2004 | ✓ | 0 | TV not competing at state level |
| 2005 | ✓ | 0 | TV not competing at state level |
| 2006 | ✓ | 0 | TV not competing at state level |
| **2007** | ✓ | **50** | **First year at state!** Swimmers: Kappler, Grabe, Montijo, Matsunaga, Chang |
| 2008 | ✓ | 52 | Good data! |
| 2009 | ✓ | 74 | Peak participation |
| 2010 | ✓ | 8 | Some swimmers |
| 2011 | ✓ | 14 | Some swimmers |
| 2012+ | In MaxPreps | N/A | Already have this data |

**Conclusion**: Tanque Verde started competing at the state championship level in **2007**.

## Data Gaps

### What we have:
- **State Championships**: 2007-2025 (from AZPreps365 PDFs + MaxPreps)
- **Invitational Meets**: 2012-2025 (from MaxPreps)

### What we're missing:
- **State Championships pre-2007**: TV did not compete at state level
- **Invitational Meets 2007-2011**: Not available online - would need paper records

## Import Plan

### Phase 1: Harvest Historical State Championships (2001-2011)

1. **Create harvester script** for AZPreps365 archive pages
   - URL pattern: `https://azpreps365.com/results/swimming/[meet_id]` (need to verify)
   - Extract: Swimmer name, school, event, time, place, year

2. **Filter for Tanque Verde swimmers**
   - Match by school name variations: "Tanque Verde", "TANQUE VERDE", etc.

3. **Parse and normalize data**
   - Convert times to standard format (MM:SS.ss)
   - Extract year/grade from swimmer info if available
   - Normalize swimmer names using aliases

4. **Create season files**
   - `top10-boys-2001-02.md` through `top10-boys-2011-12.md`
   - `top10-girls-2001-02.md` through `top10-girls-2011-12.md`
   - Note: These will only contain STATE MEET results, not full season data

### Phase 2: Rebuild All-Time Top 10

1. Run `build_alltime_top10.py` to incorporate historical data
2. Apply swimmer aliases for name normalization
3. Generate updated all-time lists

### Phase 3: Documentation

1. Add notes to generated files indicating data sources:
   - "State meet results only" for 2001-2011 seasons
   - "Full season data" for 2012-2025 seasons

## Technical Notes

### AZPreps365 URL Patterns:
- Archive index (Boys): `https://azpreps365.com/archives/swimming-boys`
- Archive index (Girls): `https://azpreps365.com/archives/swimming-girls`
- **Results are PDFs**: `https://aiaonline.org/files/[meet_id]/[year]-swimming-and-diving-[divisions]-state-championships.pdf`

Example:
- 2010: `https://aiaonline.org/files/11757/2010-swimming-and-diving-divisions-i-ii-state-championships.pdf`

### Data Format (PDFs)
The PDFs are multi-column race result sheets with:
- Event headers: "Event 208 Girls 50 Yard Freestyle"
- Swimmer names: "Collura, Taryn" (Last, First format)
- School/Year: "JR Tanque Verde High School"
- Times: "24.45" (prelim), "23.84 C" (finals with cut indicator)

**Verified Tanque Verde participation in 2010 state meet** ✓

### Extraction Approach
1. Use `pdftotext` to extract text
2. Parse by event sections (look for "Event XXX")
3. Match "Tanque Verde" entries
4. Extract swimmer name, year, time from surrounding lines

### Challenges:
1. **PDF multi-column layout**: Text extraction may not preserve column order
2. Tanque Verde may have been in different divisions historically (D-I/II vs D-III)
3. Swimmer name format is "Last, First" (needs normalization)
4. Split times included in parentheses need to be filtered

## Next Steps

1. [ ] Manually explore one AZPreps365 archive page to understand the structure
2. [ ] Create a test harvester for 2011 state meet
3. [ ] Verify Tanque Verde participation in historical meets
4. [ ] Build full harvester for all years 2001-2011
5. [ ] Process and import data
6. [ ] Rebuild all-time top 10 lists

