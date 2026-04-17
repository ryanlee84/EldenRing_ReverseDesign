# -*- coding: utf-8 -*-
"""레날라 문서·용어집·그래프를 ListUrl 폴더에 생성."""
import csv
import json
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

import matplotlib.pyplot as plt
import numpy as np

from atkparam_rows import filter_attack_rows, row_graph_coefs_all_zero

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "ListUrl"
OUT_DIR.mkdir(exist_ok=True)

SRC = BASE / "atkparam_npc.csv"
STEM = "rennala_294-318"
GLOSSARY_STEM = "glossary_WIKI"
OUT_HTML = OUT_DIR / f"{STEM}.html"
GLOSSARY_HTML = OUT_DIR / f"{GLOSSARY_STEM}.html"


def _load_boss_nav_extra():
    """`build_all_boss_docs.py` 가 쓰는 `boss_nav_extra.json` 과 병합. 없으면 빈 목록."""
    p = OUT_DIR / "boss_nav_extra.json"
    if not p.is_file():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return [(str(a), str(b)) for a, b in raw]
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return []


# 문서 제목·탭·사이드바: 영문 (공식 한글명) — NAV_PAGES 보다 먼저 정의
BOSS_NAME_EN = "Rennala, Queen of the Full Moon"
BOSS_NAME_KO_OFFICIAL = "만월의 여왕 레날라"
PAGE_TITLE_TEXT = f"{BOSS_NAME_EN} ({BOSS_NAME_KO_OFFICIAL})"

# 사이드바 전체는 boss_nav_extra.json(build_all_boss_docs 가 순서·접두어 포함해 기록). 없을 때만 레날라 한 줄.
def _nav_pages_fallback() -> list[tuple[str, str]]:
    extra = _load_boss_nav_extra()
    if extra:
        return extra
    return [("rennala_294-318.html", BOSS_NAME_KO_OFFICIAL)]


NAV_PAGES = _nav_pages_fallback()
OLD_GLOSSARY = OUT_DIR / f"{STEM}_glossary.html"
OLD_GLOSSARY_KO = OUT_DIR / "용어집 WIKI.html"
IMG_CHART = OUT_DIR / f"{STEM}_atkcoef.png"
# 보스 위키(Fextralife 원문)와 같은 주제의 위키아 일러스트(달 마법 아이콘 아님)
IMG_BOSS = OUT_DIR / f"{STEM}_boss_wiki.webp"

BOSS_WIKI_IMAGE_URL = (
    "https://static.wikia.nocookie.net/eldenring/images/f/f5/"
    "Queen_Rennala.webp/revision/latest/scale-to-width-down/400"
)
MAP_LINK = "https://eldenring.wiki.fextralife.com/Interactive+Map?id=793&code=mapA"
BOSS_WIKI_LINK = "https://eldenring.wiki.fextralife.com/Rennala,+Queen+of+the+Full+Moon"

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# CSV에만 있고 표에는 `hit_radius_slash` 한 열로 합쳐 표시
HIT_RADIUS_KEYS = ("hit0_radius", "hit1_radius", "hit2_radius", "hit3_radius")
# 그래프·행 필터·표 열 공통: 물리·마법·화염·벼락·스태미나 피해 계수
DMG_COEF_KEYS = ("atkphys", "atkmag", "atkfire", "atkthun", "atkstam")

DATA_COLS = [
    "knockbackdist",
    "hitstoptime",
    "atkphys",
    "atkmag",
    "atkfire",
    "atkthun",
    "atkstam",
    "dmglevel",
    "guardatkrate",
    "guardbreakrate",
    "hit_radius_slash",
]

DATA_COLS_KO = [
    "밀어내기 거리",
    "히트 스톱 시간",
    "물리 피해 계수",
    "마법 피해 계수",
    "화염 피해 계수",
    "벼락 피해 계수",
    "스태미나 피해 계수",
    "피해 단계",
    "가드 시 공격력 비율",
    "가드 붕괴율",
    "히트0~3 구 반경",
]


def csv_read_columns() -> set[str]:
    """합성 열 제외, CSV에 필요한 원본 열·rowid·rowname."""
    return (
        set(DATA_COLS)
        | {"rowid", "rowname"}
        | set(HIT_RADIUS_KEYS)
        | set(DMG_COEF_KEYS)
    ) - {"hit_radius_slash"}

# CSV 없을 때만 쓰는 내장 스냅샷(18열). knock 다음 히트 스톱(스냅샷은 0) 후 피해 계수·히트 반경 등.
_LEGACY_SNAPSHOT_COLS = [
    "knockbackdist",
    "hitstoptime",
    "atkphys",
    "atkmag",
    "atkfire",
    "atkthun",
    "atkstam",
    "dmglevel",
    "guardatkrate",
    "guardbreakrate",
    "hit0_radius",
    "hit1_radius",
    "hit2_radius",
    "hit3_radius",
    "maphittype",
    "friendlytarget",
    "spattribute",
    "atkattribute",
]


def _legacy_snapshot_dict(vals):
    d = {c: str(v) for c, v in zip(_LEGACY_SNAPSHOT_COLS, vals)}
    out = {}
    for c in DATA_COLS:
        if c == "hit_radius_slash":
            out[c] = "/".join(d.get(k, "0") for k in HIT_RADIUS_KEYS)
        else:
            out[c] = d.get(c, "0")
    for k in DMG_COEF_KEYS:
        out[k] = d.get(k, "0")
    return out

# 그래프용: 10pt 1줄, 띄어쓰기 없음 [1][2]
LABEL_CHART = [
    "[1]탄환.맵연동",
    "[1]탄환.기본",
    "[1]탄환.A",
    "[1]탄환.B",
    "[1]탄환.고위력마법",
    "[2]탄환.약한마법",
    "[2]탄환.중간.밀어냄큼",
    "[2]탄환.최고마법",
    "[2]탄환.중간",
    "[2]탄환.상위",
    "[2]탄환.계수없음",
    "[2]탄환.화염만",
    "[2]탄환.밀어냄약함",
    "[2]탄환.전행유사.피해단계상향",
    "[2]탄환.중간.피해단계중간",
    "[2]탄환.중간.피해단계약함",
    "[2]탄환.약함",
    "[2]근접.마법중간",
    "[2]근접.마법약함",
    "[2]근접.중간.피해단계중간",
    "[2]탄환.근접분류혼재",
    "[2]혼합.물리마법동일",
    "[2]혼합.마법약화",
    "[2]혼합.전행동일",
    "[2]광역.대형판정",
]

# 수치 표·툴팁용 (한 줄 표기는 label_table_oneline() 참고)
LABEL_TABLE = [
    "[1]탄환.맵연동",
    "[1]탄환.기본",
    "[1]탄환.A",
    "[1]탄환.B",
    "[1]탄환.고위력마법",
    "[2]탄환.약한마법",
    "[2]탄환.중간\n밀어냄큼",
    "[2]탄환.최고마법",
    "[2]탄환.중간",
    "[2]탄환.상위",
    "[2]탄환.계수없음",
    "[2]탄환.화염만",
    "[2]탄환.밀어냄약함",
    "[2]탄환.전행유사\n피해단계상향",
    "[2]탄환.중간\n피해단계중간",
    "[2]탄환.중간\n피해단계약함",
    "[2]탄환.약함",
    "[2]근접.마법중간",
    "[2]근접.마법약함",
    "[2]근접.중간\n피해단계중간",
    "[2]탄환.근접분류혼재",
    "[2]혼합.물리마법동일",
    "[2]혼합.마법약화",
    "[2]혼합.전행동일",
    "[2]광역.대형판정",
]


def label_table_oneline(s):
    return "·".join(part.strip() for part in (s or "").splitlines() if part.strip())

NOTE_TEXTS = [
    "맵·아군 설정이 다른 탄이며 계수는 비어 있음.",
    "기본 탄환이며 계수·피해 단계가 낮음.",
    "도구에 이름이 비어 있는 내부용 추정 행.",
    "바로 위 행과 같은 패턴.",
    "고위력 마법·스태미나와 높은 피해 단계.",
    "약한 마법과 작은 스태미나 계수.",
    "밀어냄과 마법이 함께 오르고 피해 단계는 중간.",
    "마법·스태미나가 높고 피해 단계는 최상급.",
    "중간 마법.",
    "상위 마법·스태미나.",
    "속성 계수가 모두 비어 있음.",
    "화염만 존재.",
    "밀어냄은 거의 없고 마법은 중간.",
    "전 행과 거의 같고 피해 단계만 약간 상향.",
    "중간 마법과 중간 피해 단계.",
    "중간 마법에 피해 단계는 약한 편.",
    "약한 마법·작은 스태미나.",
    "근접 분류이며 더미 폴리곤이 잡혀 있음.",
    "위 행보다 마법이 약간 낮음.",
    "중간 이상 마법.",
    "이름은 탄환이지만 분류는 근접에 가까움.",
    "물리·마법이 동시에 있고 스태미나도 있음.",
    "위 행보다 마법만 낮춘 변형.",
    "전 행과 수치가 동일함.",
    "판정이 크고 밀어냄도 크며 마법 계수는 매우 작음.",
]

# atkparam_npc.csv 가 없을 때(294~318행) 동일 수치로 문서만 생성
_SNAPSHOT_INT = [
    (1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 2, 1, 0, 3),
    (1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 1, 0, 3),
    (1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 1, 0, 3),
    (1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 1, 0, 3),
    (1, 0, 0, 280, 0, 0, 80, 7, 100, 0, 0, 0, 0, 0, 0, 0, 0, 3),
    (0, 0, 0, 100, 0, 0, 10, 0, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (2, 0, 0, 290, 0, 0, 60, 3, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (3, 0, 0, 350, 0, 0, 120, 7, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (1, 0, 0, 200, 0, 0, 60, 3, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (3, 0, 0, 250, 0, 0, 120, 7, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (1, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 11, 3),
    (1, 0, 0, 0, 120, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 11, 3),
    (0, 0, 0, 100, 0, 0, 60, 0, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (0, 0, 0, 100, 0, 0, 60, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (1, 0, 0, 160, 0, 0, 60, 3, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (1, 0, 0, 100, 0, 0, 60, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (0, 0, 0, 100, 0, 0, 10, 0, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (1, 0, 0, 140, 0, 0, 20, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 0),
    (1, 0, 0, 130, 0, 0, 20, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 0),
    (1, 0, 0, 200, 0, 0, 60, 3, 100, 0, 0, 0, 0, 0, 0, 0, 10, 0),
    (1, 0, 0, 100, 0, 0, 10, 0, 100, 0, 0, 0, 0, 0, 0, 0, 10, 3),
    (0, 0, 100, 100, 0, 0, 40, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 1),
    (0, 0, 100, 55, 0, 0, 40, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 1),
    (0, 0, 100, 55, 0, 0, 40, 1, 100, 0, 0, 0, 0, 0, 0, 0, 10, 1),
    (4, 0, 0, 1, 0, 0, 0, 7, 100, 0, 4, 0, 0, 0, 0, 0, 10, 3),
]
def load_rows():
    if SRC.exists():
        with open(SRC, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        h = rows[0]
        need = csv_read_columns()
        idx = {c: h.index(c) for c in need}
        data = []
        for i, L in enumerate(range(294, 319)):
            r = rows[L - 1]
            row = {
                "label_chart": LABEL_CHART[i],
                "label_table": LABEL_TABLE[i],
                "rowname": r[idx["rowname"]],
            }
            for c in DATA_COLS:
                if c == "hit_radius_slash":
                    continue
                row[c] = r[idx[c]]
            for k in DMG_COEF_KEYS:
                row[k] = r[idx[k]]
            row["hit_radius_slash"] = "/".join(
                (r[idx[k]].strip() or "0") for k in HIT_RADIUS_KEYS
            )
            data.append(row)
        return data

    data = []
    for i, vals in enumerate(_SNAPSHOT_INT):
        row = {
            "label_chart": LABEL_CHART[i],
            "label_table": LABEL_TABLE[i],
            "rowname": "",
        }
        row.update(_legacy_snapshot_dict(vals))
        data.append(row)
    return data


def download_boss_wiki_image():
    req = urllib.request.Request(
        BOSS_WIKI_IMAGE_URL,
        headers={"User-Agent": "Mozilla/5.0 (documentation build)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        IMG_BOSS.write_bytes(resp.read())


def esc(s):
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def esc_br(s):
    return "<br>".join(esc(line) for line in (s or "").split("\n"))


def esc_attr(s):
    """HTML title 속성용 (따옴표·개행 처리)."""
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", " ")
    )


def _cell_numeric_nonzero(s: str) -> bool:
    try:
        return int(float((s or "").strip() or 0)) != 0
    except (TypeError, ValueError):
        t = (s or "").strip()
        return t not in ("", "0")


def format_attack_table_cell(col_key: str, raw) -> str:
    """공격별 수치 표: 피해 계수 열은 0이 아닌 값만 굵게·빨간색. 히트 반경 슬롯·히트 스톱·가드 붕괴율은 기존 볼드 규칙."""
    s = raw if isinstance(raw, str) else str(raw or "")
    if col_key in DMG_COEF_KEYS:
        et = esc(s)
        return f'<strong class="dmg-coef-nz">{et}</strong>' if _cell_numeric_nonzero(s) else et
    if col_key == "hit_radius_slash":
        bits = []
        for p in s.split("/"):
            t = (p or "").strip() or "0"
            et = esc(t)
            bits.append(f"<strong>{et}</strong>" if _cell_numeric_nonzero(t) else et)
        return "/".join(bits)
    if col_key in ("hitstoptime", "guardbreakrate"):
        et = esc(s)
        return f"<strong>{et}</strong>" if _cell_numeric_nonzero(s) else et
    return esc(s)


def render_sidebar(active_href: str, pages: list | None = None) -> str:
    """좌측 목록. active_href 는 현재 페이지 파일명(예: rennala_294-318.html). pages 가 없으면 NAV_PAGES."""
    pages = pages or NAV_PAGES
    parts = [
        '<aside class="sidebar" aria-label="Boss page list">',
        '<p class="sidebar-title">Boss pages</p>',
        "<nav>",
    ]
    active_used = False
    for href, label in pages:
        is_here = href == active_href and not active_used
        if is_here:
            active_used = True
        active = " active" if is_here else ""
        parts.append(
            f'  <a href="{href}" class="nav-item{active}">{esc(label)}</a>'
        )
    parts.extend(["</nav>", "</aside>"])
    return "\n".join(parts)


LAYOUT_CSS = """
  .layout { display: flex; min-height: 100vh; align-items: flex-start; }
  .sidebar {
    flex: 0 0 min(320px, 38vw);
    min-width: 260px;
    background: var(--card);
    border-right: 1px solid var(--border);
    padding: 20px 16px;
    position: sticky;
    top: 0;
    align-self: flex-start;
    max-height: 100vh;
    overflow-y: auto;
  }
  .sidebar-title {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin: 0 0 14px;
  }
  .sidebar nav { display: flex; flex-direction: column; gap: 4px; }
  .nav-item {
    display: block;
    padding: 10px 12px;
    border-radius: 8px;
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    border: 1px solid transparent;
  }
  .nav-item:hover { background: #eef2ff; border-color: var(--border); }
  .nav-item.active { background: #e0e7ff; color: var(--accent); border-color: #c7d2fe; }
  .content-main { flex: 1; min-width: 0; width: 100%; }
"""

# 좌측 목록 스크롤 위치 유지. file:// 에서는 sessionStorage 가 페이지마다 분리되므로
# 이동 URL에 ?navsb=픽셀 을 붙여 전달하고, 로드 후 주소에서 지운다.
SIDEBAR_SCROLL_SCRIPT = """
<script>
(function () {
  var KEY = "elden-boss-nav-sidebar-scroll";
  var aside = document.querySelector(".sidebar");
  if (!aside) return;

  function hrefWithNavsb(href, sb) {
    var hashIdx = href.indexOf("#");
    var hash = hashIdx >= 0 ? href.slice(hashIdx) : "";
    var base = hashIdx >= 0 ? href.slice(0, hashIdx) : href;
    var sep = base.indexOf("?") >= 0 ? "&" : "?";
    return base + sep + "navsb=" + String(sb) + hash;
  }

  aside.addEventListener("click", function (e) {
    var a = e.target.closest("a.nav-item");
    if (!a || a.getAttribute("target") === "_blank") return;
    if (e.button !== 0) return;
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var href = a.getAttribute("href");
    if (!href) return;
    e.preventDefault();
    var sb = aside.scrollTop;
    try {
      sessionStorage.setItem(KEY, String(sb));
    } catch (err) {}
    location.href = hrefWithNavsb(href, sb);
  });

  function restore() {
    var n = null;
    try {
      var u = new URL(window.location.href);
      var p = u.searchParams.get("navsb");
      if (p !== null) {
        n = parseInt(p, 10) || 0;
        u.searchParams.delete("navsb");
        history.replaceState(null, "", u.toString());
      }
    } catch (err) {}
    if (n === null) {
      try {
        var y = sessionStorage.getItem(KEY);
        if (y != null) n = parseInt(y, 10) || 0;
      } catch (err2) {}
    }
    if (n === null) return;
    aside.scrollTop = n;
    requestAnimationFrame(function () {
      aside.scrollTop = n;
      requestAnimationFrame(function () {
        aside.scrollTop = n;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", restore);
  } else {
    restore();
  }
  window.addEventListener("pageshow", function (ev) {
    if (ev.persisted) restore();
  });
})();
</script>
"""


def charts(data):
    """build_test_boss_docs.charts_for 와 동일: 물리·마법·화염·벼락·스태미나 통합 PNG."""
    from build_test_boss_docs import charts_for

    return charts_for(data, IMG_CHART, STEM)


def write_glossary():
    rows = [
        ("밀어내기 거리", "맞았을 때 밀려나는 정도에 가닿는 값으로 읽는 경우가 많습니다."),
        ("히트 스톱 시간", "타격 순간 짧게 멈추는 연출과 연관될 수 있습니다."),
        ("물리 피해 계수", "물리 속성에 대한 피해 계수입니다."),
        ("마법 피해 계수", "마법(마력) 속성에 대한 피해 계수입니다."),
        ("화염 피해 계수", "화염 속성에 대한 피해 계수입니다."),
        ("벼락 피해 계수", "벼락(번개) 속성에 대한 피해 계수입니다."),
        ("스태미나 피해 계수", "스태미나 피해(가드 스태미나 소모 등)에 가닿는 계수로 읽는 경우가 많습니다."),
        ("피해 단계", "히트 반응의 단계를 나누는 값으로 쓰이는 경우가 많습니다. 이 자료 구간에는 0, 1, 3, 7만 등장합니다."),
        ("가드 시 공격력 비율", "가드에 막혔을 때 공격 쪽 비율에 가닿는 값입니다."),
        ("가드 붕괴율", "가드가 깨지기 쉬운지와 연관된 계열입니다."),
        (
            "히트0~3 구 반경",
            "멀티히트 슬롯 0~3마다 구(구체) 하나의 판정 반경을 두고, 히트0→1→2→3 순으로 한 칸에 슬래시로 적습니다(예: 30/0/0/0). "
            "0은 그 슬롯에 판정이 없다는 뜻에 가깝고, 0이 아닌 숫자(1 포함)는 그 슬롯에 판정이 있으며 값이 반경 크기입니다. "
            "1은 특수 코드가 아니라 반경이 1인 아주 작은 구로 읽으면 됩니다(30·40 등과 같은 눈금·단위). "
            "실제 거리 환산은 엔진·도구마다 다를 수 있어, 여기서는 상대 비교용 숫자로 보는 것이 안전합니다.",
        ),
    ]
    body = "".join(
        f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>\n" for a, b in rows
    )
    main_name = OUT_HTML.name
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>용어집 WIKI</title>
<style>
  body {{ font-family: "Malgun Gothic", sans-serif; max-width: 800px; margin: 24px auto; padding: 0 16px; line-height: 1.65; color: #1a1a1a; }}
  h1 {{ font-size: 1.35rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 0.95rem; }}
  th, td {{ border: 1px solid #e1e4e8; padding: 10px 12px; vertical-align: top; text-align: left; }}
  th {{ background: #f0f4ff; width: 28%; }}
  p.back {{ margin-top: 24px; }}
  a {{ color: #2563eb; }}
</style>
</head>
<body>
  <h1>용어집 WIKI</h1>
  <p class="back"><a href="{main_name}">← {esc(PAGE_TITLE_TEXT)}</a></p>
  <table>
    <tbody>
{body}
    </tbody>
  </table>
</body>
</html>
"""
    GLOSSARY_HTML.write_text(html, encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SRC.exists():
        print("atkparam_npc.csv 없음: 294~318행 내장 스냅샷으로 생성합니다.")
    data_full = load_rows()
    data = filter_attack_rows(data_full)
    note_list = [
        NOTE_TEXTS[i]
        for i, d in enumerate(data_full)
        if not row_graph_coefs_all_zero(d)
    ]
    try:
        download_boss_wiki_image()
    except Exception as e:
        print("Boss wiki image download skipped:", e)

    show_chart = charts(data)
    write_glossary()

    gloss_name = GLOSSARY_HTML.name
    img_boss_rel = IMG_BOSS.name if IMG_BOSS.exists() else ""

    # 스킬: 한 줄 (마침표 없으면 줄바꿈 없이 한 줄로 표현)
    summary_rows = """
      <tr><td>1페이즈(이하[1])탄환스킬</td><td>대부분 약하거나 비어 있고 한 종류만 고위력 마법·스태미나·피해 단계가 크며 맵·아군 설정이 다른 한 종류가 있음.</td></tr>
      <tr><td>2페이즈(이하[2])탄환스킬</td><td>마법·밀어냄·피해 단계로 위력 구간을 나누며 화염만 있는 변형과 계수가 전부 비어 있는 변형이 있음.</td></tr>
      <tr><td>2페이즈(이하[2])근접스킬</td><td>이름과 분류가 어긋난 항목이 있어 애니메이션·불릿과 대조가 필요함.</td></tr>
      <tr><td>2페이즈(이하[2])혼합·광역스킬</td><td>물리·마법이 동시에 오르는 근접형과 판정이 큰 광역이 있음.</td></tr>
    """

    rows_html = []
    for d, note in zip(data, note_list):
        name_1 = esc(label_table_oneline(d["label_table"]))
        tip = esc_attr(note)
        cells = f'<th title="{tip}">{name_1}</th>'
        cells += "".join(
            f"<td>{format_attack_table_cell(c, d.get(c, ''))}</td>" for c in DATA_COLS
        )
        rows_html.append(f"<tr>{cells}</tr>")
    rows_html = "\n".join(rows_html)

    header_row = "<th>공격 이름</th>" + "".join(
        f"<th>{esc(ko)}</th>" for ko in DATA_COLS_KO
    )

    boss_img_block = ""
    if IMG_BOSS.exists():
        boss_img_block = (
            f'<img src="{img_boss_rel}" width="200" alt="{esc(PAGE_TITLE_TEXT)}" />'
        )

    graph_bits = []
    if show_chart:
        graph_bits.append(
            f'  <figure class="chart">\n    <img src="{esc(IMG_CHART.name)}" alt="물리·마법·화염·벼락·스태미나 피해 계수" />\n  </figure>'
        )
    if graph_bits:
        graph_section_html = "  <h2>그래프</h2>\n" + "\n".join(graph_bits) + "\n"
    elif data_full and not data:
        graph_section_html = """  <h2>그래프</h2>
  <p class="chart-note">이 구간은 물리·마법·화염·벼락·스태미나 계수가 모두 0인 행만 있어 그래프를 생략했습니다.</p>
"""
    else:
        graph_section_html = ""

    # 개요·위치·체력·면역·약점: Fextralife 「Rennala, Queen of the Full Moon」 NG 전투 정보와 맞춤
    boss_block = f"""
  <section class="boss">
    <div class="boss-grid">
      <div class="boss-img">{boss_img_block}</div>
      <div class="boss-body">
        <table class="data boss-overview">
          <tbody>
            <tr><th>개요</th><td>전설 보스·샤드베어러(반신은 아님). 카리아 왕가 수장이자 라이 카리아 마법학원 옛 학원장. 선택 보스이나 <strong>별의 시대</strong> 엔딩·<strong>재탄생(재분배)</strong>을 위해 격파가 필요하다. 1페이즈는 황금 기운이 든 유년 학자를 맞춰 기포를 깨는 패턴, 2페이즈는 본체 전투다.</td></tr>
            <tr><th>위치</th><td><strong>Academy of Raya Lucaria</strong> (라이 카리아 마법학원) — 대도서관(Grand Library) 상층 전당, 엘리베이터·지역 진행 후 도달. 가장 가까운 은혜: <strong>Debate Parlor</strong> (변론의 방). (Farum Azula 등 다른 지역 보스와 위치가 다름.)</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 NG: <strong>1페이즈 HP 3,493</strong> · <strong>2페이즈 HP 4,097</strong> (방어력 109 공통). NG+ 이후·패치에 따라 변동할 수 있음 — 상세는 위키 표 참고.</td></tr>
            <tr><th>면역</th><td>
              <strong>2페이즈</strong>: 수면·광기 면역. 독·부패 등 저항은 위키 <em>Resistance</em> 표.
            </td></tr>
            <tr><th>약점</th><td>
              <strong>1페이즈</strong> — 표준 −10, 베기 −10, 타격 0, 관통 −10 · 마법 80, 화염 20, 벼락 20, 신성 20 (위키 <em>negation</em> %, 클수록 해당 속성 피해가 덜 들어감).<br />
              <strong>2페이즈</strong> — 물리 계열 동일. 마법 80, <strong>화염·벼락·신성 각 40</strong>(1페이즈보다 화염 등이 덜 막힘). 태세(Stance) 80, 패리 불가, 태세 붕괴 후 치명타. 주로 <strong>마법</strong> 속성으로 공격. 저항 수치는 페이즈·NG마다 위키와 다를 수 있음 — 아래 「공격별 수치」는 atkparam_npc 공격 행만 다룸.
            </td></tr>
          </tbody>
        </table>
        <p class="wiki-src"><a href="{BOSS_WIKI_LINK}" target="_blank" rel="noopener">Fextralife 위키 원문</a> 전투·맵·면역/약점 수치를 우선으로 하여 정리함.</p>
      </div>
    </div>
  </section>
"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(PAGE_TITLE_TEXT)}</title>
<style>
  :root {{
    --bg: #f7f8fa;
    --card: #ffffff;
    --text: #1a1a1a;
    --muted: #5c6570;
    --border: #e1e4e8;
    --accent: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    font-size: 15px;
  }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 28px 20px 80px; }}
  h1 {{ font-size: 1.85rem; margin: 0 0 0.75rem; }}
  h2 {{ font-size: 1.15rem; margin: 2rem 0 0.65rem; border-bottom: 2px solid var(--border); padding-bottom: 0.35rem; }}
  p {{ margin: 0.55rem 0; }}
  .boss {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; margin-bottom: 22px; }}
  .boss h2 {{ margin-top: 0; border: none; }}
  .boss-en {{ font-size: 0.92rem; font-weight: 500; color: var(--muted); }}
  .boss-grid {{ display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start; }}
  .boss-img {{ flex: 0 0 auto; }}
  .boss-img img {{ max-width: 200px; height: auto; border-radius: 8px; }}
  .boss-body {{ flex: 1 1 320px; min-width: 0; }}
  table.boss-overview {{ margin-top: 0; font-size: 0.9rem; }}
  table.boss-overview th {{
    width: 9.5rem;
    white-space: nowrap;
    vertical-align: top;
  }}
  .wiki-src {{ font-size: 0.85rem; color: var(--muted); margin-top: 12px; }}
  h2.with-gloss {{
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px 16px;
  }}
  h2.with-gloss .gloss-inline {{ margin: 0; font-size: 0.9rem; font-weight: 500; }}
  h2.with-gloss .gloss-inline a {{ color: var(--accent); }}
  table.data {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }}
  table.data th, table.data td {{
    border-bottom: 1px solid var(--border);
    padding: 7px 8px;
    text-align: left;
    vertical-align: top;
  }}
  table.data th {{
    background: #f0f4ff;
    font-weight: 600;
  }}
  table.data tr:last-child td, table.data tr:last-child th {{ border-bottom: none; }}
  table.atk-params {{ font-size: 0.7rem; }}
  table.atk-params th:first-child {{ white-space: nowrap; min-width: 13.5rem; max-width: 36rem; padding-left: 10px; padding-right: 12px; }}
  strong.dmg-coef-nz {{ color: #c62828; font-weight: 700; }}
  figure.chart {{
    margin: 1rem 0;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
  }}
  figure.chart img {{ max-width: 100%; height: auto; display: block; margin: 0 auto; }}
  p.chart-note {{ font-size: 0.88rem; color: var(--muted); margin: 0.35rem 0 0; max-width: 52rem; }}
  .map-link {{ margin: 6px 0 0; }}
  .map-link a {{ color: var(--accent); }}
{LAYOUT_CSS}
</style>
</head>
<body>
<div class="layout">
{render_sidebar(OUT_HTML.name)}
  <div class="content-main">
<main>
  <h1>{esc(PAGE_TITLE_TEXT)}</h1>

{boss_block}

  <p class="map-link"><a href="{MAP_LINK}" target="_blank" rel="noopener">인터랙티브 맵</a></p>

  <h2>스킬</h2>
  <table class="data">
    <thead><tr><th>이름</th><th>내용</th></tr></thead>
    <tbody>
{summary_rows}
    </tbody>
  </table>

  <h2 class="with-gloss">공격별 수치 <span class="gloss-inline"><a href="{gloss_name}">용어집 WIKI</a></span></h2>
  <div style="overflow-x:auto">
  <table class="data atk-params">
    <thead><tr>{header_row}</tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  </div>

{graph_section_html}
</main>
  </div>
</div>
{SIDEBAR_SCROLL_SCRIPT}
</body>
</html>
"""

    OUT_HTML.write_text(html, encoding="utf-8")

    old_spell_img = OUT_DIR / f"{STEM}_spell_moon.webp"
    for p in (OLD_GLOSSARY, OLD_GLOSSARY_KO, old_spell_img):
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass

    root_redirect = BASE / f"{STEM}.html"
    if root_redirect.exists():
        try:
            root_redirect.unlink()
        except OSError:
            pass

    print("Wrote", OUT_HTML)
    print("Wrote", GLOSSARY_HTML)


if __name__ == "__main__":
    main()
