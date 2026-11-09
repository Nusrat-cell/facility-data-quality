# Facility Data Quality

A small practice project: take a messy list of industrial and municipal facilities, clean it, set aside what cannot be
trusted with a reason, and produce a client-ready Excel file that ranks the best sales leads.

It is built around the kind of work a data-savvy student analyst does for a company that sells wastewater technology:
find the facilities that need a solution, keep the data trustworthy, and explain the result in a spreadsheet a
customer can open.

**The data is synthetic.** `fdq/sample.py` invents 300 facilities with the mess real public data has: capacity given
in three different units, country written five ways, duplicate records, missing capacities, impossible coordinates and
unreadable permit dates. No real facility is described.

## What it does

1. **Normalise:** unify country names, tidy names, convert capacity from m3/day, megalitres a day (MLD) and gallons
   a day to one unit.
2. **Check:** duplicates, missing capacity, coordinates out of range and permit dates that cannot be read. A row that
   fails is moved to the data quality log with its reason. Nothing is dropped silently.
3. **Score:** a simple, explainable lead score: 60 points for plant size and 40 for how soon the permit expires.
4. **Report:** `output/facilities_leads.xlsx` with three sheets: Summary, Top 50 leads, Data quality log. Header row,
   frozen panes and sensible column widths so it is ready to send.

## Run it

```
pip install pandas openpyxl pytest
python -m fdq.cli
python -m pytest
```

## Limits

- The score is a starting point, not a forecast. A real version would use the customer's own criteria.
- Unit conversion assumes the unit column is correct. A wrong unit would be caught only by a plausibility check,
  which is the next thing I would add.
