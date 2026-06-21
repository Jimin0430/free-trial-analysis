"""
data_loader.py
벤치마크 데이터 로딩 및 전처리 모듈

데이터 출처:
- ChartMogul SaaS Benchmarks 2026
- RevenueCat Subscription App Benchmarks 2026
- Relate Free Trial Survey 2021 (n=600 SaaS)
- reopt 2026 Trial Conversion Benchmarks
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "benchmark_data.csv"


def load_benchmark() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # 결측치 처리: great_conversion_pct 일부 누락 → median으로 대체
    df["great_conversion_pct"] = df["great_conversion_pct"].fillna(df["median_conversion_pct"])

    # 파생 변수
    df["card_label"] = df["card_required"].map({True: "카드 요구", False: "카드 미요구"})
    df["trial_label"] = df["trial_days"].apply(
        lambda d: "프리미엄(무기한)" if d == 0 else f"{int(d)}일"
    )

    return df


if __name__ == "__main__":
    df = load_benchmark()
    print(df[["trial_model","industry","card_label","trial_days","median_conversion_pct"]].to_string())
