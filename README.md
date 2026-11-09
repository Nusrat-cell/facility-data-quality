# Facility Data Quality

I wanted to see what the first week of a data job at a wastewater technology company might feel like, so I made up a
messy list of 300 facilities and tried to turn it into something a customer could open in Excel and use.

The data is synthetic. `fdq/sample.py` invents the facilities and then deliberately breaks them the way public
regulatory data tends to be broken. No real plant is described anywhere.

## What the mess looks like

- capacity written in three units (m3/day, megalitres a day, gallons a day)
- the same country spelled up to three ways (Denmark, DK, Danmark)
- the same facility twice, sometimes with a different capital letter or a trailing space
- missing capacities, latitudes of 999, permit dates that say "not available"
- a few gallon figures typed into rows that say m3/day

## What it does

It cleans the names and countries, converts every capacity to m3/day, and checks each row. A row that fails does not
get deleted. It goes to a log sheet with the reason next to it, so whoever opens the file can see what was left out and why.
The rows that pass get a simple lead score (60 points for plant size, 40 for how soon the permit runs out) and the top
50 go into `output/facilities_leads.xlsx`, next to a summary sheet and the log.

Run it:

```
pip install pandas openpyxl pytest
python -m fdq.cli
python -m pytest
```

## What worked

Keeping every rejected row with a reason. On the sample, 36 of 310 rows are set aside: 13 for missing capacity, 10 exact
duplicates, 6 impossible coordinates, 5 unreadable permit dates and 3 capacities that look like the wrong unit (some rows
fail for two reasons, so the reasons add up to more than 36). A test checks that clean rows plus rejected rows always
add up to the raw rows, so nothing disappears quietly.

Cleaning the name before looking for duplicates. "FACILITY 007 " and "Facility 007" only count as the same record once the
name is trimmed and title-cased, so the check runs after that step, not before.

## What did not work, or only half worked

- **My first version missed the wrong-unit rows.** A gallon figure typed into an m3/day row is a perfectly normal
  looking number, so nothing complained and the plant came out thousands of times too big. I added a size check
  (anything above 150,000 m3/day goes to the log with "check the unit"). It is a blunt rule: a real city plant that
  large would be flagged too, so a person has to look at those rows.
- **Duplicates are exact matches only.** "Facility 007" and "Facilty 007" are treated as two plants. Fuzzy matching
  would catch it but also merge plants that really are different, so I left it out rather than guess.
- **When it finds a duplicate it keeps the first row, not the most complete one.** On real data I would keep the row
  with the fewest gaps.
- **Coordinates are only checked for being possible, not for being right.** A latitude of 55 is accepted even if the
  facility says it is in Sweden and the point is in the sea.
- **The lead score is my guess.** 60/40 is not based on anything a customer told me. It is explainable, which was the
  point, but a real team would set the weights from what their salespeople actually close.

## Next

A check of coordinates against the country, fuzzy duplicate suggestions that a person approves, and the real
regulatory sources in place of the invented list.
