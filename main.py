#!/usr/bin/env python3
"""
python parse_canteen.py <pdf_path> --year 2026 --month 5 --output 2026-05.json
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import pdfplumber

def normalize(text: str) -> str:
    """半角記号に統一して空白を削除"""
    return unicodedata.normalize("NFKC", text).strip()


DAY_MAP = {
    "月": "mon", "火": "tue", "水": "wed",
    "木": "thu", "金": "fri", "土": "sat", "日": "sun",
}
WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri"]
DOW_INDEX = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

def expand_days(label: str):
    label = normalize(label).strip()
    if label == "平日":
        return WEEKDAY_KEYS[:]
    range_match = re.match(r"^(.)[~](.)$", label)
    if range_match:
        start, end = range_match.group(1), range_match.group(2)
        week = ["月", "火", "水", "木", "金", "土", "日"]
        si, ei = week.index(start), week.index(end)
        if si <= ei:
            return [DAY_MAP[w] for w in week[si:ei+1]]
        else:
            return [DAY_MAP[w] for w in week[si:] + week[:ei+1]]
    if label in DAY_MAP:
        return [DAY_MAP[label]]
    if re.match(r"^[月火水木金土日,]+$", label):
        return [DAY_MAP[c] for c in label if c in DAY_MAP]
    return []


def parse_time(t: str) -> str:
    return normalize(t).replace("：", ":")


def parse_hours(hours_note: str):
    result = []
    segments = re.split(r"\s*/\s*|\n", normalize(hours_note))
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        m = re.match(r"^(.+?)\s+(\d{1,2}[：:]\d{2})\s*[~]\s*(\d{1,2}[：:]\d{2})$", seg)
        if m:
            days = expand_days(m.group(1))
            if days:
                result.append({
                    "days": days,
                    "open_time":  parse_time(m.group(2)),
                    "close_time": parse_time(m.group(3)),
                })
    return result

def parse_cell(cell: Optional[str]) -> dict:
    if not cell or cell.strip() == "":
        return {"open": False}

    text = normalize(cell).strip()

    if text == "x" or text == "x":
        return {"open": False}

    if text == "×":
        return {"open": False}

    if "○" not in text and "x" not in text and "×" not in text:
        return {"open": True, "note": text.replace("\n", "")}

    time_match = re.search(r"(\d{1,2}:\d{2})\s*[|]\s*(\d{1,2}:\d{2})", text)
    if time_match:
        return {
            "open": True,
            "open_time":  time_match.group(1),
            "close_time": time_match.group(2),
        }

    if "○" in text:
        return {"open": True}

    return {"open": False}

def parse_table(table, year: int, month: int) -> dict:
    if len(table) < 3:
        raise ValueError("テーブルの行数が少なすぎます")

    header_row = table[0]
    data_rows  = table[2:]

    DATE_COL_START = 4

    days = []
    for col_idx in range(DATE_COL_START, len(header_row)):
        day_str = normalize(header_row[col_idx] or "")
        if day_str.isdigit():
            day = int(day_str)
            try:
                d = date(year, month, day)
                days.append({"col": col_idx, "date": d.isoformat()})
            except ValueError:
                pass

    stores = []
    for row in data_rows:
        if not row or not row[0] or not normalize(str(row[0])).isdigit():
            continue

        store_id   = int(normalize(str(row[0])))
        building   = normalize(str(row[1] or "")).replace("\n", " ")
        name       = normalize(str(row[2] or "")).replace("\n", " ")
        hours_note = str(row[3] or "")

        hours = parse_hours(hours_note)

        dow_to_times = {}
        for h in hours:
            for d in h["days"]:
                dow_to_times[d] = (h["open_time"], h["close_time"])

        schedule = {}
        for day_info in days:
            col = day_info["col"]
            cell_val = row[col] if col < len(row) else None
            entry = parse_cell(cell_val)

            if entry.get("open") and "open_time" not in entry and "note" not in entry:
                d = date.fromisoformat(day_info["date"])
                dow = DOW_INDEX[d.weekday()]
                if dow in dow_to_times:
                    entry["open_time"], entry["close_time"] = dow_to_times[dow]

            schedule[day_info["date"]] = entry

        stores.append({
            "id":       store_id,
            "name":     name,
            "building": building,
            "hours":    hours,
            "schedule": schedule,
        })

    return {
        "meta": {
            "year":      year,
            "month":     month,
            "parsed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "stores": stores,
    }

def main():
    ap = argparse.ArgumentParser(description="学食営業時間PDF→JSON変換くん")
    ap.add_argument("pdf",      help="入力 PDF ファイルパス")
    ap.add_argument("--year",   type=int, default=datetime.now().year)
    ap.add_argument("--month",  type=int, default=datetime.now().month)
    ap.add_argument("--output", default="-", help="出力先 (デフォルト: stdout)")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: {pdf_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    with pdfplumber.open(pdf_path) as pdf:
        tables = pdf.pages[0].extract_tables()

    if not tables:
        print("Error: PDFにテーブルが見つかりませんでした", file=sys.stderr)
        sys.exit(1)

    result = parse_table(tables[0], year=args.year, month=args.month)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(output_json)
    else:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"✓ {args.output} ({len(result['stores'])} 店舗)", file=sys.stderr)


if __name__ == "__main__":
    main()
