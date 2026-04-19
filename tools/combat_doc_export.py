# -*- coding: utf-8 -*-
"""
보스 전투 문서화용 데이터 생성.

- AtkParam_Npc CSV에서 공격 행을 필터링해 JSON + Markdown을 쓴다.
- .anibnd/.chrbnd 등은 바이너리이므로 직접 파싱하지 않는다. 대신 --asset-dir 를 주면
  해당 폴더 아래 파일 목록(인벤토리)을 문서에 포함한다.
- TAE 이벤트 표는 별도 도구로 덤프한 JSON을 --merge-tae 로 넘기면 같은 산출물에 합친다.

예 (트리 가드, 깃에 넣기 좋은 상대 경로·자산 힌트):
  python tools/combat_doc_export.py --boss-key "[Tree Sentinel]" --exclude Draconic \\
    --asset-doc-lines data/tree_sentinel_asset_inventory.txt \\
    --out-json data/tree_sentinel_combat.json \\
    --out-md docs/tree_sentinel_combat.md

  TAE JSON 병합(형식은 임의 dict 가능, 권장 스키마는 data/tree_sentinel_tae.example.json):
  python tools/combat_doc_export.py --boss-key "[Tree Sentinel]" --exclude Draconic \\
    --asset-doc-lines data/tree_sentinel_asset_inventory.txt \\
    --merge-tae data/tree_sentinel_tae.example.json \\
    --out-json data/tree_sentinel_combat.json --out-md docs/tree_sentinel_combat.md

로컬 chr 폴더를 스캔해 실제 파일 경로를 넣으려면(절대 경로 가능):
  python tools/combat_doc_export.py ... --asset-dir "C:/.../Smithbox_Tree/chr" --chr-glob "c3251.*"
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

BASE = Path(__file__).resolve().parents[1]
DEFAULT_ATKPARAM = BASE / "atkparam_npc.csv"


def path_for_meta(path: Path, base: Path) -> str:
    """저장소 루트 아래면 posix 상대 경로, 아니면 절대 경로 문자열."""
    try:
        rel = Path(path).resolve().relative_to(base.resolve())
        return rel.as_posix()
    except ValueError:
        return str(Path(path).resolve())


def load_doc_asset_lines(path: Path | None) -> list[str]:
    """한 줄 하나. # 시작은 주석. 파일 없으면 []."""
    if path is None or not path.is_file():
        return []
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


# 문서·JSON에 넣을 열(존재하는 것만 출력)
DOC_COLUMNS = [
    "rowid",
    "rowname",
    "atkphys",
    "atkmag",
    "atkfire",
    "atkthun",
    "atkstam",
    "hit0_radius",
    "hit1_radius",
    "hit2_radius",
    "hit3_radius",
    "knockbackdist",
    "hitstoptime",
    "dmglevel",
    "guardatkrate",
    "guardbreakrate",
    "speffectid0",
    "speffectid1",
    "speffectid2",
    "speffectid3",
    "speffectid4",
    "atksuperarmor",
    "atkbehaviorid",
    "isarrowatk",
]


def load_rows(
    csv_path: Path,
    include: str,
    exclude: str | None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("rowname") or "").strip()
            if include not in name:
                continue
            if exclude and exclude in name:
                continue
            rows.append({k: (row.get(k) or "").strip() for k in row})
    rows.sort(key=lambda r: int(r.get("rowid") or 0))
    return rows


def slim_attack(row: dict[str, str]) -> dict[str, str]:
    return {k: row.get(k, "") for k in DOC_COLUMNS}


def write_json(
    path: Path,
    meta: dict,
    attacks: list[dict[str, str]],
    tae_extra: dict | None,
) -> None:
    payload = build_json_payload(meta, attacks, tae_extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def render_markdown(
    meta: dict,
    attacks: list[dict[str, str]],
    inventory: list[str],
    tae_extra: dict | None,
) -> str:
    lines: list[str] = []
    lines.append(f"# 전투 문서 데이터 — {meta.get('title', 'Boss')}")
    lines.append("")
    lines.append(f"- 생성: `{meta.get('generated', '')}`")
    lines.append(f"- 소스 CSV: `{meta.get('csv_path', '')}`")
    inc = (meta.get("include_key") or "").strip()
    exc = (meta.get("exclude_substr") or "").strip()
    if inc or exc:
        lines.append(f"- 필터: 포함 `{inc}`")
        if exc:
            lines.append(f"- 제외: `{exc}`")
    else:
        lines.append("- 추출: CSV의 모든 데이터 행 (필터 없음)")
    lines.append("")

    if inventory:
        lines.append("## 자산 폴더 인벤토리")
        lines.append("")
        lines.append("*(바이너리는 이 툴이 해석하지 않음. 파일 경로만 기록.)*")
        lines.append("")
        for p in inventory:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("## 공격 행 (AtkParam_Npc)")
    lines.append("")
    if not attacks:
        lines.append("*(해당 조건의 행이 없습니다.)*")
    else:
        cols = [c for c in DOC_COLUMNS if any(c in r for r in attacks)]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for r in attacks:
            lines.append(
                "| "
                + " | ".join((r.get(c, "") or "").replace("|", "\\|") for c in cols)
                + " |"
            )
    lines.append("")

    if tae_extra is not None:
        lines.append("## TAE (외부 JSON 병합)")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(tae_extra, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def build_json_payload(
    meta: dict,
    attacks: list[dict[str, str]],
    tae_extra: dict | None,
) -> dict:
    payload: dict = {
        "meta": meta,
        "attacks": [slim_attack(r) for r in attacks],
    }
    if tae_extra is not None:
        payload["tae"] = tae_extra
    return payload


def write_md(
    path: Path,
    meta: dict,
    attacks: list[dict[str, str]],
    inventory: list[str],
    tae_extra: dict | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_markdown(meta, attacks, inventory, tae_extra),
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="보스 공격 CSV → 문서용 JSON/Markdown")
    ap.add_argument("--atkparam", type=Path, default=DEFAULT_ATKPARAM)
    ap.add_argument("--boss-key", default="[Tree Sentinel]", help="rowname 부분 문자열")
    ap.add_argument("--exclude", default="Draconic", help="rowname 에 포함되면 제외")
    ap.add_argument("--title", default="Tree Sentinel")
    ap.add_argument(
        "--asset-dir",
        type=Path,
        default=None,
        help="chr 등 추출 폴더 — 파일 목록만 문서에 포함",
    )
    ap.add_argument(
        "--chr-glob",
        default=r"c3251.*",
        help="asset-dir 안에서 이 패턴(정규식)에 맞는 파일만 목록",
    )
    ap.add_argument(
        "--asset-doc-lines",
        type=Path,
        default=None,
        help="문서용 자산 경로 텍스트(# 주석 가능). 스캔 없이 meta·MD에만 반영",
    )
    ap.add_argument("--merge-tae", type=Path, default=None, help="TAE 덤프 JSON 경로")
    ap.add_argument(
        "--out-json",
        type=Path,
        default=BASE / "data" / "tree_sentinel_combat.json",
    )
    ap.add_argument(
        "--out-md",
        type=Path,
        default=BASE / "docs" / "tree_sentinel_combat.md",
    )
    args = ap.parse_args()

    if not args.atkparam.is_file():
        print("CSV 없음:", args.atkparam, file=sys.stderr)
        sys.exit(1)

    ex = args.exclude.strip() if args.exclude else None
    attacks = load_rows(args.atkparam, args.boss_key, ex)

    tae_extra: dict | None = None
    if args.merge_tae and args.merge_tae.is_file():
        tae_extra = json.loads(args.merge_tae.read_text(encoding="utf-8"))

    inv: list[str] = []
    if args.asset_dir:
        pat = re.compile(args.chr_glob, re.I)
        if args.asset_dir.is_dir():
            inv = [
                path_for_meta(p, BASE)
                for p in sorted(args.asset_dir.iterdir())
                if pat.match(p.name)
            ]
    doc_hints = load_doc_asset_lines(args.asset_doc_lines)
    for hint in doc_hints:
        if hint not in inv:
            inv.append(hint)

    meta = {
        "title": args.title,
        "generated": datetime.now(timezone.utc).isoformat(),
        "csv_path": path_for_meta(args.atkparam, BASE),
        "include_key": args.boss_key,
        "exclude_substr": ex or "",
        "asset_inventory": inv,
    }

    write_json(args.out_json, meta, attacks, tae_extra)
    write_md(args.out_md, meta, attacks, inv, tae_extra)
    print("Wrote:", args.out_json)
    print("Wrote:", args.out_md)
    print("Rows:", len(attacks))


if __name__ == "__main__":
    main()
