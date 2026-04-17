# -*- coding: utf-8 -*-
"""atkparam 행에서 그래프·표에 쓸 계수 열만 보는 필터."""

from __future__ import annotations

# 그래프에 쓰는 피해 계수(물리·마법·화염·스태미나). 네 가지가 모두 0이면 표·그래프에서 행을 제외한다.
# 벼락(atkthun)만 있는 행도 그래프에 수치가 없으므로 동일하게 제외한다.
COEF_KEYS_FOR_ROW_VISIBILITY = ("atkphys", "atkmag", "atkfire", "atkstam")


def row_graph_coefs_all_zero(d: dict) -> bool:
    for k in COEF_KEYS_FOR_ROW_VISIBILITY:
        try:
            v = int(str(d.get(k, "0") or "0").strip() or 0)
        except (TypeError, ValueError):
            v = 0
        if v != 0:
            return False
    return True


def filter_attack_rows(data: list) -> list:
    """물리·마법·화염·스태미나 피해 계수가 모두 0인 행은 제외."""
    return [d for d in data if not row_graph_coefs_all_zero(d)]
