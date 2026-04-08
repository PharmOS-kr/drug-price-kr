#!/usr/bin/env python3
"""HIRA 약제급여목록표 다운로드 → 표준코드 매핑 → data/prices.csv 저장."""

import csv
import sys
import tempfile
from pathlib import Path

import openpyxl
import requests

from build_mapping import load_mapping

HIRA_DOWNLOAD_URL = (
    "https://www.hira.or.kr/bbs/bbsCDownLoad.do"
    "?apndNo=1&apndBrdBltNo={blt_id}&apndBrdTyNo=1&apndBltNo=59"
)
LATEST_BLT_ID = 1703

CSV_HEADER = [
    "표준코드", "제품코드", "제품명", "규격", "단위",
    "상한금액", "업체명", "주성분코드", "주성분명", "투여", "분류",
]


def download_excel(blt_id: int) -> Path:
    url = HIRA_DOWNLOAD_URL.format(blt_id=blt_id)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.write(resp.content)
    tmp.close()
    print(f"Downloaded {len(resp.content):,} bytes → {tmp.name}", file=sys.stderr)
    return Path(tmp.name)


def parse_excel(xlsx_path: Path) -> list[dict]:
    """엑셀 파일 파싱. 헤더에서 컬럼 위치를 자동 감지."""
    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header = [str(h or "").replace("\n", "").strip() for h in rows[0]]
    ncols = len(header)
    print(f"Sheet: {ws.title}, {len(rows)-1} data rows, {ncols} cols", file=sys.stderr)

    # 헤더에서 컬럼 인덱스 찾기
    col_map = {}
    for i, h in enumerate(header):
        if "제품코드" in h and "제품코드" not in col_map:
            col_map["제품코드"] = i
        elif "제품명" in h:
            col_map["제품명"] = i
        elif "업체명" in h:
            col_map["업체명"] = i
        elif h == "규격":
            col_map["규격"] = i
        elif h == "단위":
            col_map["단위"] = i
        elif "상한금액" in h:
            col_map["상한금액"] = i
        elif h == "주성분코드":
            col_map["주성분코드"] = i
        elif "주성분명" in h:
            col_map["주성분명"] = i
        elif h == "투여":
            col_map["투여"] = i
        elif h == "분류":
            col_map["분류"] = i

    # 12컬럼 구 포맷: 주성분명 행이 분리되어 있음
    is_old_format = ncols <= 12

    items = []
    current_ingredient = ""
    for row in rows[1:]:
        if is_old_format and row[5] is None:
            current_ingredient = str(row[4] or "")
            continue

        item = {}
        for field, idx in col_map.items():
            item[field] = str(row[idx] or "") if idx < len(row) else ""
        if is_old_format:
            item["주성분명"] = current_ingredient
        items.append(item)

    return items


def write_csv(items: list[dict], mapping: dict[str, str], output_path: Path) -> None:
    for item in items:
        item["표준코드"] = mapping.get(item["제품코드"], "")
    items.sort(key=lambda x: (x["표준코드"] or "z", x["제품코드"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(items)
    mapped = sum(1 for i in items if i["표준코드"])
    print(f"Saved {len(items)} rows ({mapped} mapped) → {output_path}", file=sys.stderr)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="HIRA 약제급여목록표 수집")
    parser.add_argument("--blt-id", type=int, default=LATEST_BLT_ID,
                        help="HIRA 게시물 ID (default: %(default)s)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    mapping = load_mapping()
    xlsx_path = download_excel(args.blt_id)
    items = parse_excel(xlsx_path)
    write_csv(items, mapping, repo_root / "data" / "prices.csv")
    xlsx_path.unlink()


if __name__ == "__main__":
    main()
