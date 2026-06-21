"""
simulator.py
데이터 락인(Lock-in) 효과 및 지연 전환(Delayed Conversion) 시뮬레이션

가설 2 검증:
  도구형 서비스는 기간이 길어질수록 전환율이 우상향한다.
"""

import numpy as np
import pandas as pd


# ── 상수 (Recurly / Zhang & Duan 2025 참조) ───────────────────────────────
LOCKIN_DAILY_RATE = 0.008   # 하루당 락인 효과 증가율 (도구형)
BASE_CONVERSION   = 0.12    # 체험 1일차 기본 즉시 전환율


def lockin_curve(days: int, daily_rate: float = LOCKIN_DAILY_RATE) -> float:
    """
    데이터 락인 누적 효과 모델 (지수 포화 함수).

    Parameters
    ----------
    days        : 체험 기간 (일)
    daily_rate  : 하루당 락인 증가율

    Returns
    -------
    lock_in_bonus : 락인으로 인한 추가 전환율 (0~1)
    """
    return 1 - np.exp(-daily_rate * days)


def simulate_conversion(
    trial_days_list: list[int],
    service_type: str = "기록도구형",
    card_required: bool = False,
) -> pd.DataFrame:
    """
    체험 기간별 전환율 시뮬레이션.

    Parameters
    ----------
    trial_days_list : 비교할 체험 기간 목록
    service_type    : "기록도구형" or "콘텐츠창의형"
    card_required   : 카드 선등록 여부

    Returns
    -------
    DataFrame : 기간별 채택률·즉시전환율·지연전환율·총전환율
    """
    records = []
    for days in trial_days_list:
        # 채택률: 기간↑ → 채택률 소폭 증가, 카드 요구 시 대폭 감소
        adoption = 0.74 - (0.04 if card_required else 0) + days * 0.0003
        adoption = min(adoption, 0.95)

        # 락인 효과 (도구형에만 적용)
        lockin = lockin_curve(days) if service_type == "기록도구형" else 0.0

        # 즉시 전환율: 기간 길수록 감소 (피로도), 카드 요구 시 증가
        immediate = BASE_CONVERSION * (1 - 0.002 * days) + (0.10 if card_required else 0)
        immediate = max(immediate, 0.05)

        # 지연 전환율: 락인 효과에 비례
        delayed = 0.05 + lockin * 0.18

        records.append({
            "trial_days": days,
            "service_type": service_type,
            "card_required": card_required,
            "adoption_rate": round(adoption, 4),
            "immediate_conversion_rate": round(immediate, 4),
            "delayed_conversion_rate": round(delayed, 4),
            "total_conversion_rate": round(immediate + delayed, 4),
            "lockin_effect": round(lockin, 4),
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    days = [7, 14, 21, 30, 60]

    print("=== 기록 도구형 (카드 미요구) ===")
    print(simulate_conversion(days, "기록도구형", False).to_string(index=False))

    print("\n=== 기록 도구형 (카드 요구) ===")
    print(simulate_conversion(days, "기록도구형", True).to_string(index=False))

    print("\n=== 콘텐츠 창의형 (카드 미요구) ===")
    print(simulate_conversion(days, "콘텐츠창의형", False).to_string(index=False))
