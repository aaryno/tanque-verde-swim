#!/bin/bash
# Rebuild data/state_history/*.json from the official State results PDFs, every
# year in one place so the set is reproducible. Inputs live in
# ~/workspaces/tv-swim/incoming/state-history/ (aia-<year>.pdf plus the text
# made from it; how each text was made is noted per year).
set -euo pipefail
cd "$(dirname "$0")/../.."
I=${STATE_PDFS:-$HOME/workspaces/tv-swim/incoming/state-history}
A=https://azpreps365.com/archives/swimming-boys
H="python3 scripts/harvest/state_history.py"
FIN="The official file lists only the finals of this division: a swimmer who swam prelims only is not in it."

# 2007-2009: pdftotext -layout -x 25 -y 0 -W 600 -H 792 (crop the clipped left margin); round headings
# are unreadable, so the round comes from the listing and the places (--lanes 8).
$H 2007 $I/aia-2007-crop.txt --meet "2007 AIA 1A/2A/3A State Championship" --date 2007-10-27 --source https://aiaonline.org/files/7844/x.pdf --source $A --pdf $I/aia-2007.pdf --lanes 8
$H 2008 $I/aia-2008-crop.txt --meet "2008 AIA 1A/2A/3A State Championship" --date 2008-10-18 --source https://aiaonline.org/files/9361/x.pdf --source $A --pdf $I/aia-2008.pdf --lanes 8
$H 2009 $I/aia-2009-crop.txt --meet "2009 AIA 1A/2A/3A State Championship" --date 2009-10-17 --source https://aiaonline.org/files/10504/x.pdf --source $A --pdf $I/aia-2009.pdf --lanes 8
# 2010-2017, 2021: pdftotext -layout
$H 2010 $I/aia-2010.txt --meet "2010 AIA Division II State Championship" --date 2010-11-06 --source https://aiaonline.org/files/11757/x.pdf --source $A --pdf $I/aia-2010.pdf
$H 2011 $I/aia-2011.txt --meet "2011 AIA Division II State Championship" --date 2011-11-05 --source https://aiaonline.org/files/12611/x.pdf --source $A --pdf $I/aia-2011.pdf
$H 2012 $I/aia-2012.txt --meet "2012 AIA Division II State Championship" --date 2012-11-03 --source https://aiaonline.org/files/13462/x.pdf --source $A --pdf $I/aia-2012.pdf
$H 2013 $I/aia-2013.txt --meet "2013 AIA Division II State Championship" --date 2013-11-09 --source https://aiaonline.org/files/14249/x.pdf --source $A --pdf $I/aia-2013.pdf
$H 2014 $I/aia-2014.txt --meet "2014 AIA Division II State Championship" --date 2014-11-08 --source https://aiaonline.org/files/14651/x.pdf --source $A --pdf $I/aia-2014.pdf
$H 2015 $I/aia-2015.txt --meet "2015 AIA Division II State Championship" --date 2015-11-07 --source https://aiaonline.org/files/15247/x.pdf --source $A --pdf $I/aia-2015.pdf
$H 2016 $I/aia-2016.txt --meet "2016 AIA Division III State Championship" --date 2016-11-05 --source https://aiaonline.org/files/15661/x.pdf --source $A --pdf $I/aia-2016.pdf
$H 2017 $I/aia-2017.txt --meet "2017 AIA Division III State Championship" --date 2017-11-04 --source https://aiaonline.org/files/16054/x.pdf --source $A --pdf $I/aia-2017.pdf
# 2018, 2019: pdftotext -layout -l 61 / -l 76 (leave out the Meet of Champions pages)
$H 2018 $I/aia-2018-nomoc.txt --meet "2018 AIA Division III State Championship" --date 2018-11-03 --source https://aiaonline.org/files/16553/x.pdf --source $A --pdf $I/aia-2018.pdf --relays-without-names --note "$FIN" --note "The official file gives no relay swimmers this year, so relays are not credited to anyone."
$H 2019 $I/aia-2019-nomoc.txt --meet "2019 AIA Division III State Championship" --date 2019-11-08 --source https://aiaonline.org/files/16845/x.pdf --source $A --pdf $I/aia-2019.pdf --note "$FIN"
# 2020: three columns per page, cut with -x 0/202/402 -W 202/200/210 (see state_history.py)
$H 2020 $I/aia-2020-cols.txt --meet "2020 AIA Division III State Championship" --date 2020-11-07 --source https://aiaonline.org/files/17252/x.pdf --source $A --pdf $I/aia-2020.pdf --note "Swum as a virtual meet (timed finals at each school) because of COVID-19; the file gives no grades."
$H 2021 $I/aia-2021.txt --meet "2021 AIA Division III State Championship" --date 2021-11-06 --source https://aiaonline.org/files/17672/x.pdf --source $A --pdf $I/aia-2021.pdf
# 2022: three columns (aia-2022-d3-cols.txt, Division 3 pages 40-57)
$H 2022 $I/aia-2022-d3-cols.txt --meet "2022 AIA Division 3 State Championship" --date 2022-11-05 --source https://aiaonline.org/files/17935/2022-swimming-and-diving-divisions-i-iii-state-championships-results.pdf --pdf $I/aia-2022.pdf
$H 2023 $I/aia-2023.txt --meet "2023 D-3 AIA State Championship" --date 2023-11-04 --source https://aiaonline.org/files/18187/2023-swimming-and-diving-divisions-i-iii-state-championships.pdf --pdf $I/aia-2023.pdf
# 2024 and 2025 came from SwimSwam-posted D3 files with their own options (two files; --team-scores); see their JSON source fields. They hold no DQ/SCR rows.
