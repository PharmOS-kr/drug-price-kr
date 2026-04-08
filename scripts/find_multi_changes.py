#!/usr/bin/env python3
"""2회 이상 상한금액이 변동된 제품을 찾는 분석 스크립트."""

import csv
import io
import subprocess
from collections import defaultdict


def get_commits():
    """data/prices.csv를 변경한 커밋 목록 (오래된 순)."""
    result = subprocess.run(
        ["git", "log", "--oneline", "--reverse", "--", "data/prices.csv"],
        capture_output=True, text=True,
    )
    return result.stdout.strip().split("\n")


def load_snapshot(sha):
    """특정 커밋의 prices.csv를 {제품코드: 상한금액} 딕셔너리로 반환."""
    raw = subprocess.run(
        ["git", "show", f"{sha}:data/prices.csv"],
        capture_output=True, text=True,
    ).stdout
    prices = {}
    for row in csv.DictReader(io.StringIO(raw)):
        prices[row["제품코드"]] = row["상한금액"]
    return prices


def load_names():
    """최신 커밋에서 제품코드 → (제품명, 업체명) 매핑."""
    raw = subprocess.run(
        ["git", "show", "HEAD:data/prices.csv"],
        capture_output=True, text=True,
    ).stdout
    names = {}
    for row in csv.DictReader(io.StringIO(raw)):
        names[row["제품코드"]] = (row["제품명"], row["업체명"])
    return names


def main():
    commits = get_commits()

    # 커밋별 스냅샷
    snapshots = []
    for line in commits:
        sha = line.split()[0]
        month = line.split("data: ")[1].split()[0] if "data: " in line else sha
        snapshots.append((month, load_snapshot(sha)))

    # 연속 스냅샷 간 가격 변동 추적
    changes = defaultdict(list)
    for i in range(1, len(snapshots)):
        prev_month, prev_prices = snapshots[i - 1]
        curr_month, curr_prices = snapshots[i]
        for code in set(prev_prices) & set(curr_prices):
            if prev_prices[code] != curr_prices[code]:
                changes[code].append(
                    (prev_month, curr_month, prev_prices[code], curr_prices[code])
                )

    multi = {k: v for k, v in changes.items() if len(v) >= 2}
    names = load_names()

    print(f"전체 변동 제품: {len(changes)}건")
    print(f"2회 이상 변동: {len(multi)}건\n")

    for code in sorted(multi, key=lambda c: -len(multi[c])):
        name, company = names.get(code, ("?", "?"))
        print(f"━━━ {name} ({company}) [제품코드:{code}]")
        for prev_m, curr_m, old_p, new_p in multi[code]:
            try:
                diff = int(new_p) - int(old_p)
                pct = diff / int(old_p) * 100 if int(old_p) else 0
                arrow = "↑" if diff > 0 else "↓"
                print(f"  {prev_m} → {curr_m}: {old_p} → {new_p} ({arrow}{abs(pct):.1f}%)")
            except ValueError:
                print(f"  {prev_m} → {curr_m}: {old_p} → {new_p}")
        print()


if __name__ == "__main__":
    main()
