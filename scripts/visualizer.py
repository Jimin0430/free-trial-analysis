"""
visualizer.py
분석 결과 시각화 모듈 (4가지 분석)

1. 카드 등록 여부별 전환율 비교
2. 체험 기간별 전환율 비교
3. 산업군(B2B vs B2C)별 비교
4. 종합 비교 (카드 × 기간 × 산업)
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _set_korean_font():
    # macOS 한글 폰트를 파일 경로로 직접 등록
    import platform
    from matplotlib import font_manager

    if platform.system() == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        ]

        for font_path in font_paths:
            try:
                font_manager.fontManager.addfont(font_path)
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                plt.rcParams['font.family'] = font_name
                break
            except:
                continue

    plt.rcParams['axes.unicode_minus'] = False


sns.set_theme(style="whitegrid")
PALETTE = ["#5B8DB8", "#E07B54", "#6DBF82", "#C97EC4", "#F0C040"]


# ── 분석 1: 카드 등록 여부별 전환율 ───────────────────────────────────────
def plot_card_comparison(df: pd.DataFrame, save: bool = True):
    """카드 요구 vs 미요구 전환율 비교 (산업군별)"""
    _set_korean_font()  # 각 plot 함수에서 폰트 설정
    # 프리미엄/리버스트라이얼 제외, trial_days > 0만
    filt = df[df["trial_days"] > 0].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("카드 등록 여부별 전환율 비교", fontsize=14, fontweight="bold")

    for ax, metric, label in zip(
        axes,
        ["good_conversion_pct", "median_conversion_pct", "great_conversion_pct"],
        ["Good (하위)", "Median (중간)", "Great (상위)"]
    ):
        grouped = filt.groupby("card_label")[metric].mean()
        bars = ax.bar(grouped.index, grouped.values,
                      color=["#5B8DB8", "#E07B54"], edgecolor="white", width=0.5)
        ax.set_title(f"{label} 전환율", fontsize=11)
        ax.set_ylabel("전환율 (%)")
        for bar, val in zip(bars, grouped.values):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
        ax.set_ylim(0, grouped.values.max() * 1.3)

    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "01_card_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


# ── 분석 2: 체험 기간별 전환율 ────────────────────────────────────────────
def plot_trial_days_comparison(df: pd.DataFrame, save: bool = True):
    """7일 / 14일 / 30일 체험 기간별 전환율"""
    filt = df[df["industry"] == "General"].copy()
    filt = filt[filt["trial_days"] > 0]

    fig, ax = plt.subplots(figsize=(9, 5))

    x = np.arange(len(filt))
    width = 0.25

    ax.bar(x - width, filt["good_conversion_pct"], width, label="Good", color="#5B8DB8")
    ax.bar(x,         filt["median_conversion_pct"], width, label="Median", color="#E07B54")
    ax.bar(x + width, filt["great_conversion_pct"], width, label="Great", color="#6DBF82")

    ax.set_xticks(x)
    labels = filt.apply(lambda r: f"{int(r['trial_days'])}일\n({'카드' if r['card_required'] else '무카드'})", axis=1)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("전환율 (%)")
    ax.set_title("체험 기간 × 카드 등록 여부별 전환율 (General 기준)", fontsize=12)
    ax.legend()

    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "02_trial_days_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


# ── 분석 3: 산업군별 비교 (B2B vs B2C) ────────────────────────────────────
def plot_industry_comparison(df: pd.DataFrame, save: bool = True):
    """B2B vs B2C 산업군별 median 전환율 비교"""
    b2b_b2c = df[df["industry"].isin(["B2B_SaaS", "B2C_SaaS"])].copy()
    b2b_b2c = b2b_b2c[b2b_b2c["trial_days"] > 0]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("산업군별 전환율 비교 (B2B vs B2C)", fontsize=14, fontweight="bold")

    for ax, industry, color in zip(axes, ["B2B_SaaS", "B2C_SaaS"], ["#5B8DB8", "#E07B54"]):
        sub = b2b_b2c[b2b_b2c["industry"] == industry]
        grouped = sub.groupby("card_label")["median_conversion_pct"].mean()
        bars = ax.bar(grouped.index, grouped.values, color=color, alpha=0.85,
                      edgecolor="white", width=0.4)
        ax.set_title(industry.replace("_", " "), fontsize=12)
        ax.set_ylabel("Median 전환율 (%)")
        ax.set_ylim(0, grouped.values.max() * 1.35)
        for bar, val in zip(bars, grouped.values):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "03_industry_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


# ── 분석 4: 종합 히트맵 (카드 × 기간 × 산업) ─────────────────────────────
def plot_heatmap(df: pd.DataFrame, save: bool = True):
    """카드 등록 여부 × 산업군 median 전환율 히트맵"""
    filt = df[df["trial_days"] > 0].copy()
    pivot = filt.pivot_table(
        values="median_conversion_pct",
        index="industry",
        columns="card_label",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Blues",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Median 전환율 (%)"})
    ax.set_title("산업군 × 카드 등록 여부별 Median 전환율 히트맵", fontsize=12)
    ax.set_xlabel("")
    ax.set_ylabel("")

    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "04_heatmap.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


if __name__ == "__main__":
    from data_loader import load_benchmark
    df = load_benchmark()
    plot_card_comparison(df)
    plot_trial_days_comparison(df)
    plot_industry_comparison(df)
    plot_heatmap(df)
    print("모든 차트 생성 완료!")
