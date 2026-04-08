# drug-price-kr

건강보험 의약품 약가(상한금액) 변동 이력을 Git으로 추적합니다.

## 왜?

- 의약품 약가는 건강보험심사평가원 고시로 수시 변동
- 변동 이력이 체계적으로 공개되지 않음
- **git diff로 언제, 어떤 약이, 얼마나 바뀌었는지** 즉시 확인

## 데이터 구조

```
data/
├── prices.csv              # 매월 덮어쓰기 → git diff로 변동 추적
└── reference/
    └── drug-master-*.csv   # 약가마스터 (표준코드 매핑 원본)
```

### prices.csv 스키마

| 컬럼 | 설명 | 예시 |
|------|------|------|
| 표준코드 | KD코드 13자리 | 8806717050118 |
| 제품코드 | HIRA 9자리 | 645302132 |
| 제품명 | 약품명 | 포크랄시럽(포수클로랄) |
| 규격 | 용량 | 95(1) |
| 단위 | 단위 | mL/병 |
| 상한금액 | 보험 상한가 (원) | 129 |
| 업체명 | 제조사 | 한림제약(주) |
| 주성분코드 | 성분코드 | 130830ASY |
| 주성분명 | 성분명 | chloral hydrate 9.5g |
| 투여 | 내복/주사/외용 | 내복 |
| 분류 | 약효분류코드 | 112 |

## 활용 예시

```bash
# 최근 약가 변동 확인
git log --oneline -- data/prices.csv

# 두 시점 간 가격 변동
git diff HEAD~1 -- data/prices.csv

# 특정 약품 가격 히스토리
git log -p -S "타이레놀" -- data/prices.csv

# 삭제된 품목 확인
git diff HEAD~1 -- data/prices.csv | grep "^-" | grep -v "^---"
```

## 데이터 현황

| 월 | 건수 | 매핑률 |
|---|---|---|
| 2025-11 | 21,702 | 94% |
| 2025-12 | 21,757 | 94% |
| 2026-01 | 21,770 | 94% |
| 2026-02 | 21,790 | 94% |
| 2026-03 | 21,819 | 94% |
| 2026-04 | 21,888 | 93% |

## 자동 수집

GitHub Actions로 매월 1일, 15일 자동 수집됩니다.

수동 실행: Actions 탭 → "Collect Drug Prices" → "Run workflow"

## 로컬 실행

```bash
pip install -r scripts/requirements.txt
cd scripts && python collect.py
```

## 데이터 출처

- [건강보험심사평가원 약제급여목록표](https://www.hira.or.kr/bbsDummy.do?pgmid=HIRAA030014050000)
- [공공데이터포털 약가마스터](https://www.data.go.kr/data/15067462/fileData.do) (표준코드 매핑)

## 라이선스

데이터: [CC BY 4.0](LICENSE) | 코드: MIT
