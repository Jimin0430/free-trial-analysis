# 기록 관리 앱 무료 체험 최적 설계 분석
**경제학과 12222571 최지민 | 기말고사 대체 보고서**

## 프로젝트 개요
기록 관리 앱의 수익 극대화를 위한 최적 무료 체험(Free Trial) 설계를 데이터 기반으로 분석합니다.

## 폴더 구조
```
free_trial_analysis/
├── data/
│   └── benchmark_data.csv       # 외부 리포트/논문 기반 벤치마크 데이터
├── notebooks/
│   └── analysis.ipynb           # 메인 분석 노트북
├── scripts/
│   ├── data_loader.py           # 데이터 로딩 및 전처리
│   ├── simulator.py             # 시나리오 시뮬레이션
│   └── visualizer.py            # 시각화
├── outputs/
│   └── figures/                 # 생성된 차트 저장
├── requirements.txt
└── README.md
```

## 분석 변수
| 구분 | 변수 | 옵션 |
|------|------|------|
| 독립변수 (IV) | 무료 체험 기간 | 7일 / 14일 / 30일 / 60일 |
| 독립변수 (IV) | 카드 선등록 여부 | Opt-in / Opt-out |
| 독립변수 (IV) | 서비스 유형 | 기록 도구형 / 콘텐츠 창의형 |
| 종속변수 (DV) | 채택률 / 즉시전환율 / 지연전환율 / LTV | - |

## 비교 그룹
- **Group A**: 기록 도구형 × 14일 × 미요구 → 표준 모델
- **Group B**: 기록 도구형 × 60일 × 미요구 → 락인 검증
- **Group C**: 기록 도구형 × 7일 × 요구 → 고관여 필터
- **Group D**: 콘텐츠 창의형 × 14일 × 미요구 → 대조 모델

## 핵심 가설
1. 카드 미등록 체험이 초기 채택률은 높으나, 최종 유료 전환율은 선등록 모델이 더 높다.
2. 도구형 서비스는 기간이 길어질수록 데이터 락인 효과로 전환율이 우상향한다.

## 실행 방법
```bash
pip install -r requirements.txt
jupyter notebook notebooks/analysis.ipynb
```

## 참고 자료
- Zhang, L., & Duan, J. (2025). Longer or shorter? A field experiment on free trial duration. *Frontiers in Psychology.*
- Recurly / Adapty / Shno 산업 리포트
