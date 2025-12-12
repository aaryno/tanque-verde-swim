# Annual Page Redesign - December 12, 2025

## Goal
Redesign annual summary pages to match the styling and structure of `index.html` (splash page).

## Current Structure (to be replaced)
- Season Overview (plain text stats)
- Meet Schedule (table)
- Records Broken (bullet lists)
- Season Best Times (table)
- Active Swimmers (bullet lists)

## New Structure (matching index.html)

### 1. Season Overview Card
- Total swims, swimmers, meets
- Records broken count
- State meet placement (if applicable)
- Note for years with incomplete data

```html
<div class="container my-5" id="season-overview">
    <div class="section-header">
        <h2 class="mb-0">📊 2025-26 Season Overview</h2>
    </div>
    <div class="section-content">
        <div class="row g-4 mt-3">
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h3 class="display-4 text-primary">269</h3>
                        <p class="mb-0">Total Swims</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h3 class="display-4 text-primary">30</h3>
                        <p class="mb-0">Swimmers</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h3 class="display-4 text-primary">5</h3>
                        <p class="mb-0">Meets</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h3 class="display-4 text-success">4</h3>
                        <p class="mb-0">Records Broken</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- State placement if applicable -->
        <div class="row g-4 mt-2">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body text-center">
                        <p class="mb-1"><strong>Boys State: 4th Place</strong></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body text-center">
                        <p class="mb-1"><strong>Girls State: 7th Place</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2. Seniors Section (collapsible)
Same format as index.html `senior-card` styling:
- Card with name, stats
- School/class records if any
- Events with times and progression badges

### 3. State Highlights (collapsible)
Same format as index.html state highlights:
- Top finishers with place badges
- Event, time, and record badges

### 4. Records Broken (collapsible)
- Overall School Records (relay + individual)
- Use card-based format like index.html
- Show NEW vs PREVIOUS with improvement

### 5. Class Records Broken (collapsible)
- Grouped by class (FR/SO/JR/SR)
- Show event, swimmer, time
- Badge styling

## Data Requirements

For each season, we need:
1. **Stats**: Total swims, swimmers, meets, records count
2. **State placement**: Boys and Girls team places (if state meet occurred)
3. **Seniors**: List of seniors with their events and times
4. **State results**: Top 10 finishers at state meet
5. **Records broken**: Overall records broken that season
6. **Class records**: Class records set that season

## Generation Strategy

1. Generate pages from **oldest to newest** (2007-08 → 2025-26)
2. Track class records as we go - detect new records per season
3. Flag years with incomplete data (before ~2012)

## Incomplete Data Note

For seasons before 2012-13 (or where invitationals are missing):

```html
<div class="alert alert-info">
    <small>⚠️ Note: Complete meet results may not be available for this season. 
    Records shown are based on available data from state meets and select invitationals.</small>
</div>
```

## Files to Modify

1. `generate_enhanced_annual.py` - Complete rewrite to match new format
2. `docs/css/style.css` - May need additional styles for stats cards

## Next Steps

1. Create prototype HTML for 2025-26 page manually
2. Review with user
3. Iterate on design
4. Convert to Python generator
5. Generate all pages oldest→newest
