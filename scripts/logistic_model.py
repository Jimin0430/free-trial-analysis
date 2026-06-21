"""
logistic_model.py
로지스틱 회귀 분석 모듈

목적: 카드 등록 여부, 체험 기간, 산업군 조합이
     "높은 전환율 그룹"에 속할 확률을 예측

입력(X): card_required, trial_days, industry (범주형 → 인코딩)
출력(Y): high_conversion (median_conversion_pct > 전체 평균 → 1, 아니면 0)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import classification_report, ConfusionMatrixDisplay

OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _set_korean_font():
    # macOS 한글 폰트 우선순위로 시도
    import platform
    if platform.system() == 'Darwin':  # macOS
        fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'AppleMyungjo']
        for font in fonts:
            if font in [f.name for f in fm.fontManager.ttflist]:
                plt.rcParams['font.family'] = font
                break
    plt.rcParams['axes.unicode_minus'] = False

_set_korean_font()


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    피처 엔지니어링
    - 범주형 변수(industry) → 원-핫 인코딩
    - 타겟(Y): median_conversion_pct가 전체 평균보다 높으면 1, 낮으면 0
    """
    # 프리미엄(trial_days=0) 제외 — 체험 기간 비교 대상 아님
    filt = df[df["trial_days"] > 0].copy()

    # 타겟 변수 생성
    threshold = filt["median_conversion_pct"].mean()
    filt["high_conversion"] = (filt["median_conversion_pct"] > threshold).astype(int)

    print(f"전환율 기준 임계값(평균): {threshold:.1f}%")
    print(f"높은 전환율(1): {filt['high_conversion'].sum()}개 | 낮은 전환율(0): {(filt['high_conversion']==0).sum()}개\n")

    # 피처 선택 및 인코딩
    features = pd.get_dummies(
        filt[["card_required", "trial_days", "industry"]],
        columns=["industry"],
        drop_first=False
    )
    features["card_required"] = features["card_required"].astype(int)

    target = filt["high_conversion"]
    return features, target, threshold, filt


def train_model(X: pd.DataFrame, y: pd.Series):
    """로지스틱 회귀 학습 (표준화 포함)"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_scaled, y)

    return model, scaler, X_scaled


def evaluate_model(model, X_scaled, y, X):
    """
    모델 평가
    - 데이터가 적으므로 LOO(Leave-One-Out) 교차검증 사용
    - LOO: 한 개씩 빼고 나머지로 학습 → 빠진 하나를 예측 → 반복
    """
    loo = LeaveOneOut()
    loo_scores = cross_val_score(model, X_scaled, y, cv=loo, scoring="accuracy")

    print("=== 모델 평가 ===")
    print(f"LOO 교차검증 정확도: {loo_scores.mean():.1%} (±{loo_scores.std():.1%})")
    print(f"※ 데이터 28행으로 적으므로 LOO 교차검증 사용\n")

    y_pred = model.predict(X_scaled)
    print("=== 분류 리포트 ===")
    print(classification_report(y, y_pred, target_names=["낮은 전환율(0)", "높은 전환율(1)"]))

    return y_pred, loo_scores


def plot_coefficients(model, feature_names: list, save: bool = True):
    """계수(Coefficient) 시각화 — 어떤 변수가 전환율에 가장 영향을 주는가"""
    coefs = pd.Series(model.coef_[0], index=feature_names).sort_values()

    # 변수명 한글화
    rename_map = {
        "card_required": "카드 선등록(요구)",
        "trial_days": "체험 기간(일수)",
        "industry_B2B_SaaS": "산업: B2B SaaS",
        "industry_B2C_SaaS": "산업: B2C SaaS",
        "industry_Developer_Tools": "산업: 개발자 도구",
        "industry_AI_SaaS": "산업: AI SaaS",
        "industry_General": "산업: General",
        "industry_Subscription_Apps": "산업: 구독 앱",
    }
    coefs.index = [rename_map.get(i, i) for i in coefs.index]

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#E07B54" if v > 0 else "#5B8DB8" for v in coefs.values]
    bars = ax.barh(coefs.index, coefs.values, color=colors, edgecolor="white")

    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("계수(Coefficient) — 양수: 전환율 ↑, 음수: 전환율 ↓", fontsize=10)
    ax.set_title("로지스틱 회귀 계수\n어떤 변수가 높은 전환율에 영향을 주는가?", fontsize=12)

    for bar, val in zip(bars, coefs.values):
        ax.text(val + (0.03 if val >= 0 else -0.03), bar.get_y() + bar.get_height()/2,
                f"{val:+.2f}", va="center", ha="left" if val >= 0 else "right", fontsize=9)

    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "05_logistic_coefficients.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


def plot_confusion_matrix(model, X_scaled, y, save: bool = True):
    """혼동 행렬(Confusion Matrix) 시각화"""
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_estimator(
        model, X_scaled, y,
        display_labels=["낮은 전환율(0)", "높은 전환율(1)"],
        colorbar=False, ax=ax, cmap="Blues"
    )
    ax.set_title("혼동 행렬 (Confusion Matrix)", fontsize=12)
    plt.tight_layout()
    if save:
        path = OUTPUT_DIR / "06_confusion_matrix.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved → {path}")
    return fig


def predict_scenario(model, scaler, feature_names: list):
    """
    직접 만든 서비스 시나리오 예측
    기록 관리 앱 B2C 기준으로 주요 조건 조합 비교
    """
    scenarios = {
        "B2C 7일 카드 미요구":  {"card_required": 0, "trial_days": 7,  "industry": "B2C_SaaS"},
        "B2C 7일 카드 요구":    {"card_required": 1, "trial_days": 7,  "industry": "B2C_SaaS"},
        "B2C 14일 카드 미요구": {"card_required": 0, "trial_days": 14, "industry": "B2C_SaaS"},
        "B2C 14일 카드 요구":   {"card_required": 1, "trial_days": 14, "industry": "B2C_SaaS"},
        "B2C 30일 카드 미요구": {"card_required": 0, "trial_days": 30, "industry": "B2C_SaaS"},
        "B2C 30일 카드 요구":   {"card_required": 1, "trial_days": 30, "industry": "B2C_SaaS"},
        "B2B 7일 카드 미요구":  {"card_required": 0, "trial_days": 7,  "industry": "B2B_SaaS"},
        "B2B 7일 카드 요구":    {"card_required": 1, "trial_days": 7,  "industry": "B2B_SaaS"},
        "B2B 14일 카드 미요구": {"card_required": 0, "trial_days": 14, "industry": "B2B_SaaS"},
        "B2B 14일 카드 요구":   {"card_required": 1, "trial_days": 14, "industry": "B2B_SaaS"},
        "B2B 30일 카드 미요구": {"card_required": 0, "trial_days": 30, "industry": "B2B_SaaS"},
        "B2B 30일 카드 요구":   {"card_required": 1, "trial_days": 30, "industry": "B2B_SaaS"},
    }

    records = []
    for name, cond in scenarios.items():
        row = {f: 0 for f in feature_names}
        row["card_required"] = cond["card_required"]
        row["trial_days"] = cond["trial_days"]
        ind_col = f"industry_{cond['industry']}"
        if ind_col in row:
            row[ind_col] = 1
        X_input = scaler.transform(pd.DataFrame([row]))
        prob = model.predict_proba(X_input)[0][1]
        records.append({"시나리오": name, "높은 전환율 확률": f"{prob:.1%}"})

    result = pd.DataFrame(records)
    print("\n=== 기록 관리 앱 시나리오별 예측 ===")
    print(result.to_string(index=False))
    return result


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent))
    from data_loader import load_benchmark

    df = load_benchmark()
    X, y, threshold, filt = prepare_features(df)
    model, scaler, X_scaled = train_model(X, y)
    y_pred, loo_scores = evaluate_model(model, X_scaled, y, X)
    plot_coefficients(model, X.columns.tolist())
    plot_confusion_matrix(model, X_scaled, y)
    predict_scenario(model, scaler, X.columns.tolist())
