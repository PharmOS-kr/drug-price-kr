#!/usr/bin/env python3
"""약가마스터에서 제품코드 → 표준코드 매핑 생성."""

import csv
from pathlib import Path


def load_mapping(master_path: Path | None = None) -> dict[str, str]:
    """제품코드(9자리) → 표준코드(13자리) 매핑 반환."""
    if master_path is None:
        repo_root = Path(__file__).resolve().parent.parent
        master_path = repo_root / "data" / "reference" / "drug-master-20251031.csv"

    mapping: dict[str, str] = {}
    with open(master_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            std_code = (row.get("표준코드") or "").strip()
            product_code = (row.get("제품코드(개정후)") or "").strip()
            if product_code and std_code:
                mapping[product_code] = std_code
    return mapping


if __name__ == "__main__":
    m = load_mapping()
    print(f"Loaded {len(m)} mappings")
    for k, v in list(m.items())[:5]:
        print(f"  {k} → {v}")
