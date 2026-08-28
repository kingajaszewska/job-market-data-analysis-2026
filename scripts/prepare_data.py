"""Prepare the job-offer research spreadsheet for portfolio analysis.

The script keeps all 100 collected records, standardizes analytical fields,
adds data-quality flags, and creates a normalized offer-to-tool table.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "job_offers_source.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def normalize_seniority(value: str) -> str:
    text = value.casefold().strip()
    if text in {"mid", "mid/senior"}:
        return "Mid+"
    if any(token in text for token in ("mid", "specjalista", "koordynator")):
        return "Junior–Mid"
    return "Junior / entry"


def normalize_work_mode(value: str) -> str:
    text = value.casefold().replace(" ", "")
    if "brak" in text:
        return "Unknown"
    if "hybryd" in text:
        return "Hybrid"
    if text == "zdalna":
        return "Remote"
    if text == "stacjonarna":
        return "On-site"
    return "Mixed / flexible"


def normalize_employment(value: str) -> str:
    text = value.casefold().strip()
    if "brak" in text:
        return "Unknown"
    if text in {"różna", "umowa o pracę / b2b", "b2b / uop", "umowa zlecenie / b2b", "umowa o pracę / zlecenie"}:
        return "Multiple options"
    if "staż" in text or "praktyka" in text:
        return "Internship / placement"
    if "b2b" in text or "kontrakt" in text:
        return "B2B"
    if "zlecenie" in text:
        return "Civil-law contract"
    if "umowa o pracę" in text or "zastępstwo" in text:
        return "Employment contract"
    return "Other"


def normalize_category(value: str) -> str:
    text = value.casefold().strip()
    if any(token in text for token in ("data governance", "data quality", "master data", "jakość danych")):
        return "Data governance & quality"
    if any(token in text for token in ("dokument", "knowledge management", "informacja", "research")):
        return "Information & documentation"
    if any(token in text for token in ("biznes", "analiza systemowa", "analiza it", "pmo", "crm", "consulting")):
        return "Business & systems analysis"
    if re.search(r"\bbi\b", text) or any(token in text for token in ("raport", "data warehouse", "data engineering")):
        return "Reporting & BI"
    if any(token in text for token in ("administrac", "support", "wprowadzanie danych", "operations", "obsługa klienta")):
        return "Operations & data support"
    return "Data analysis"


def classify_record_quality(value: str) -> str:
    text = value.casefold().strip()
    if text.startswith("zweryfikowana") and "wynikach wyszukiwania" not in text:
        return "Verified"
    if text.startswith("archiwalna") and "do weryfikacji" not in text:
        return "Archived direct record"
    return "Needs verification"


TOOL_PATTERNS: list[tuple[str, str]] = [
    ("Excel", r"\bexcel\b"),
    ("MS Office", r"ms\s*office"),
    ("Power BI", r"power\s*bi"),
    ("SQL", r"\bsql\b"),
    ("Python", r"\bpython\b"),
    ("R", r"(?:^|[/,\s])r(?:$|[/,\s])"),
    ("BI tools", r"(?<!power )\bbi\b|narzędzia\s+bi"),
    ("Azure", r"\bazure\b"),
    ("SAP", r"\bsap\b"),
    ("Jira", r"\bjira\b"),
    ("Confluence", r"\bconfluence\b"),
    ("BPMN", r"\bbpmn\b"),
    ("UML", r"\buml\b"),
    ("GitLab", r"\bgitlab\b"),
    ("Postman", r"\bpostman\b"),
    ("Qlik", r"\bqlik\b"),
    ("SharePoint", r"\bsharepoint\b"),
    ("CRM", r"\bcrm\b"),
    ("PowerPoint", r"\bpowerpoint\b"),
    ("Data warehouse", r"data\s*warehouse"),
]


def extract_tools(value: str) -> list[str]:
    text = value.casefold().strip()
    if text in {"brak informacji", "brak danych", ""}:
        return []
    found = []
    for tool, pattern in TOOL_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(tool)
    return found


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_excel(SOURCE_FILE, sheet_name="Baza ofert")
    raw.columns = [str(column).strip() for column in raw.columns]

    cleaned = pd.DataFrame(
        {
            "offer_id": raw["Nr"].astype(int),
            "portal": raw["Portal"].astype(str).str.strip(),
            "job_title": raw["Stanowisko"].astype(str).str.strip(),
            "company": raw["Firma"].astype(str).str.strip(),
            "location": raw["Lokalizacja"].astype(str).str.strip(),
            "seniority_raw": raw["Poziom"].astype(str).str.strip(),
            "seniority_group": raw["Poziom"].astype(str).map(normalize_seniority),
            "work_mode_raw": raw["Tryb pracy"].astype(str).str.strip(),
            "work_mode_group": raw["Tryb pracy"].astype(str).map(normalize_work_mode),
            "employment_raw": raw["Forma zatrudnienia"].astype(str).str.strip(),
            "employment_group": raw["Forma zatrudnienia"].astype(str).map(normalize_employment),
            "category_raw": raw["Kategoria"].astype(str).str.strip(),
            "category_group": raw["Kategoria"].astype(str).map(normalize_category),
            "tools_raw": raw["Narzędzia"].astype(str).str.strip(),
            "salary_raw": raw["Wynagrodzenie"].astype(str).str.strip(),
            "salary_disclosed": raw["Wynagrodzenie"].astype(str).str.contains(r"\d", regex=True).map({True: "Yes", False: "No"}),
            "record_quality": raw["Status / uwagi"].astype(str).map(classify_record_quality),
            "source_url": raw["Link / źródło"].astype(str).str.strip(),
            "access_date": pd.to_datetime(raw["Data dostępu"], errors="coerce").dt.strftime("%Y-%m-%d"),
            "tasks_competencies": raw["Zakres/kompetencje z oferty"].astype(str).str.strip(),
            "requirements": raw["Wymagania"].astype(str).str.strip(),
            "fit_notes": raw["Dlaczego pasuje do pracy"].astype(str).str.strip(),
            "status_raw": raw["Status / uwagi"].astype(str).str.strip(),
        }
    )

    cleaned["duplicate_source_url"] = cleaned["source_url"].duplicated(keep=False).map({True: "Yes", False: "No"})
    cleaned["duplicate_title_company"] = cleaned.duplicated(["job_title", "company"], keep=False).map({True: "Yes", False: "No"})

    tool_rows: list[dict[str, object]] = []
    for offer_id, tools_raw in zip(cleaned["offer_id"], cleaned["tools_raw"]):
        for tool in extract_tools(tools_raw):
            tool_rows.append({"offer_id": int(offer_id), "tool": tool})
    offer_tools = pd.DataFrame(tool_rows, columns=["offer_id", "tool"])

    cleaned.to_csv(OUTPUT_DIR / "job_offers_clean.csv", index=False)
    offer_tools.to_csv(OUTPUT_DIR / "offer_tools.csv", index=False)

    dictionary = pd.DataFrame(
        [
            ("offer_id", "Unique record identifier", "source"),
            ("portal", "Recruitment portal", "source"),
            ("job_title", "Job title", "source"),
            ("company", "Employer name", "source"),
            ("location", "Location text from the listing", "source"),
            ("seniority_raw", "Original seniority label", "source"),
            ("seniority_group", "Standardized seniority group", "derived"),
            ("work_mode_raw", "Original work-mode label", "source"),
            ("work_mode_group", "Standardized work mode", "derived"),
            ("employment_raw", "Original contract information", "source"),
            ("employment_group", "Standardized employment group", "derived"),
            ("category_raw", "Original research category", "source"),
            ("category_group", "Standardized analytical category", "derived"),
            ("tools_raw", "Tools listed in the research sheet", "source"),
            ("salary_raw", "Salary information as collected", "source"),
            ("salary_disclosed", "Yes when salary text contains a numeric amount", "derived"),
            ("record_quality", "Verified, archived direct record, or needs verification", "derived"),
            ("source_url", "Listing or search-result URL", "source"),
            ("access_date", "Date on which the source was accessed", "source"),
            ("tasks_competencies", "Condensed tasks and competencies", "source"),
            ("requirements", "Condensed requirements", "source"),
            ("fit_notes", "Research note explaining relevance", "source"),
            ("status_raw", "Original verification/status note", "source"),
            ("duplicate_source_url", "Flags repeated URLs", "derived"),
            ("duplicate_title_company", "Flags repeated title-company combinations", "derived"),
        ],
        columns=["field", "description", "field_type"],
    )
    dictionary.to_csv(OUTPUT_DIR / "data_dictionary.csv", index=False)

    summary = {
        "records": int(len(cleaned)),
        "verified": int((cleaned["record_quality"] == "Verified").sum()),
        "archived_direct": int((cleaned["record_quality"] == "Archived direct record").sum()),
        "needs_verification": int((cleaned["record_quality"] == "Needs verification").sum()),
        "salary_disclosed": int((cleaned["salary_disclosed"] == "Yes").sum()),
        "duplicate_source_url_records": int((cleaned["duplicate_source_url"] == "Yes").sum()),
        "duplicate_title_company_records": int((cleaned["duplicate_title_company"] == "Yes").sum()),
        "tool_mentions": int(len(offer_tools)),
    }
    (OUTPUT_DIR / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
