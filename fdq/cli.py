"""python -m fdq.cli  -> writes output/facilities_leads.xlsx from the synthetic sample."""
from .clean import check
from .report import write_excel
from .sample import build


def main() -> None:
    clean, quarantined = check(build())
    write_excel(clean, quarantined, "output/facilities_leads.xlsx")
    print(f"{len(clean)} records used, {len(quarantined)} set aside with a reason")


if __name__ == "__main__":
    main()
