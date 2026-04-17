# -*- coding: utf-8 -*-
"""테스트: Blaidd / Black Knife Assassin — 레날라 문서와 동일 레이아웃·표·그래프."""
import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Fandom·Wikia는 짧은 UA에서 403을 주는 경우가 있어, 레날라 스크립트보다 브라우저에 가깝게 둔다.
WIKI_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

import build_rennala_doc as br

from atkparam_rows import filter_attack_rows

import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "ListUrl"
OUT_DIR.mkdir(exist_ok=True)
SRC = BASE / "atkparam_npc.csv"

# rowname 예: "[Blaidd the Half-Wolf] Bullet" → 접미사만 표시(표시 시 영문 Bullet 은 발사체 로 치환).
_ROWNAME_STRIP_LEADING_BRACKET = re.compile(r"^\[[^\]]+\]\s*", re.DOTALL)
_BRACKET_KEY_HEAD = re.compile(r"^\[([^\]]+)\]")
_BULLET_WORD = re.compile(r"(?i)\bbullet\b")


def _ko_bullet_label(text: str) -> str:
    """데이터 원문의 영문 Bullet 을 사용자 표기 발사체 로 통일."""
    if not text:
        return text
    return _BULLET_WORD.sub("발사체", text)


def _bracket_key_first(rowname: str) -> str:
    """rowname 맨 앞 `[보스 키]` 안의 문자열. 없으면 빈 문자열."""
    s = (rowname or "").strip()
    m = _BRACKET_KEY_HEAD.match(s)
    return m.group(1).strip() if m else ""


def _chart_label_text(suffix: str, key: str) -> str:
    """그래프 Y축: 접미사 또는 보스 키만 (구분은 표·그래프의 # 열)."""
    suf = (suffix or "").replace("\n", " ").strip()
    if suf:
        out = suf if len(suf) <= 40 else suf[:38] + "…"
        return _ko_bullet_label(out)
    if key:
        return key
    return "—"


plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def _rowname_suffix(rowname: str) -> str:
    """선행 `[보스 키]` 한 덩어리를 제거한 뒤 남는 문자열(접미사). 없으면 빈 문자열."""
    s = (rowname or "").strip()
    if not s:
        return ""
    rest = _ROWNAME_STRIP_LEADING_BRACKET.sub("", s, count=1).strip()
    return rest


def _attack_labels(rowname: str, _rowid: str) -> tuple[str, str]:
    """(표 첫 열용 label_table, 그래프용 label_chart).

    접미사·보스 키만 쓰고 내부 rowid 는 붙이지 않는다(행 번호는 별도 # 열).
    """
    suffix = _rowname_suffix(rowname)
    key = _bracket_key_first(rowname)
    if suffix:
        one = suffix.replace("\n", " ").strip()
        if len(one) > 160:
            one = one[:159] + "…"
        table = _ko_bullet_label(one)
    else:
        table = key if key else "—"
    chart = _chart_label_text(suffix, key)
    return table, chart


def _safe_int_cell(x) -> int:
    try:
        if x is None or x == "":
            return 0
        return int(float(x))
    except (TypeError, ValueError):
        return 0


_DOM_FULL = {"물": "물리", "마": "마법", "화": "화염", "뇌": "벼락", "스태": "스태미나"}


def _tier_attack_label(dom_tag: str, tier_key: str) -> str:
    """약·중·강 구간을 약공·중공·강공 등으로. 화염+중만 '중간' (화염/중간)."""
    if tier_key == "약":
        return "약공"
    if tier_key == "강":
        return "강공"
    if tier_key == "중":
        return "중간" if dom_tag == "화" else "중공"
    return tier_key


def _listurl_curated_labels(row: dict) -> tuple[str, str]:
    """ListUrl 큐레이션 보스: 물리/중공D1, 발사체·화염/강공D0 형태. rowid 없음."""
    rname = (row.get("rowname") or "").strip()
    lower = rname.lower()
    suf = _rowname_suffix(rname).replace("\n", " ").strip()

    ap = _safe_int_cell(row.get("atkphys"))
    am = _safe_int_cell(row.get("atkmag"))
    af = _safe_int_cell(row.get("atkfire"))
    ath = _safe_int_cell(row.get("atkthun"))
    ast = _safe_int_cell(row.get("atkstam"))
    dl = _safe_int_cell(row.get("dmglevel"))

    pairs = [("물", ap), ("마", am), ("화", af), ("뇌", ath), ("스태", ast)]
    mxv = max(v for _, v in pairs)
    dom = ""
    if mxv > 0:
        for tag, v in pairs:
            if v == mxv:
                dom = tag
                break

    if mxv <= 0:
        tier_key = "무계수"
    elif mxv < 100:
        tier_key = "약"
    elif mxv < 250:
        tier_key = "중"
    else:
        tier_key = "강"

    if mxv <= 0:
        core = f"무계수D{dl}"
    else:
        tw = _tier_attack_label(dom, tier_key)
        core = f"{_DOM_FULL[dom]}/{tw}D{dl}"

    if suf:
        s_short = suf if len(suf) <= 18 else suf[:17] + "…"
        display = f"{_ko_bullet_label(s_short)}·{core}"
    elif "bullet" in lower:
        display = f"발사체·{core}"
    else:
        display = core

    if len(display) > 58:
        display = display[:55] + "…"
    return display, display


def load_slice(line_start: int, line_end: int, *, label_mode: str = "default"):
    """CSV 1-based 행 번호(헤더=1이면 데이터는 2부터). 레날라 스크립트와 동일하게 헤더가 1행.

    label_mode:
      - ``default``: 공격별 첫 열·그래프는 `_attack_labels` (접미사/보스키·rowid).
      - ``listurl_curated``: `build_all_boss_docs` 의 ListUrl 보스만 — 수치 기반 분류 라벨 (`_listurl_curated_labels`).

    공격별 수치·그래프: ``write_boss_html`` 에서 행마다 ``#``(1부터)과 짝지음. ``listurl_curated`` 는 예: ``물리/중공D1``.
    """
    if not SRC.exists():
        raise FileNotFoundError("atkparam_npc.csv 가 필요합니다.")
    if label_mode not in ("default", "listurl_curated"):
        raise ValueError(f"unknown label_mode: {label_mode!r}")
    with open(SRC, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    h = rows[0]
    need = br.csv_read_columns()
    idx = {c: h.index(c) for c in need}
    data = []
    for L in range(line_start, line_end + 1):
        r = rows[L - 1]
        rid = r[idx["rowid"]]
        rname = r[idx["rowname"]] if idx["rowname"] < len(r) else ""
        row = {
            "rowid": rid,
            "rowname": rname,
            "line": L,
        }
        for c in br.DATA_COLS:
            if c == "hit_radius_slash":
                continue
            row[c] = r[idx[c]]
        for k in br.DMG_COEF_KEYS:
            row[k] = r[idx[k]]
        row["hit_radius_slash"] = "/".join(
            (r[idx[k]].strip() or "0") for k in br.HIT_RADIUS_KEYS
        )
        if label_mode == "listurl_curated":
            label_table, label_chart = _listurl_curated_labels(row)
        else:
            label_table, label_chart = _attack_labels(rname, rid)
        row["label_table"] = label_table
        row["label_chart"] = label_chart
        data.append(row)
    return data


def note_for_row(d: dict) -> str:
    bits = []
    if d.get("rowname"):
        bits.append(f"rowname: {_ko_bullet_label(d['rowname'])}")
    bits.append(f"내부 식별 rowid {d['rowid']}")
    ap, am = d.get("atkphys", "0"), d.get("atkmag", "0")
    if ap != "0" and am != "0":
        bits.append("물리·마법 동시.")
    elif am != "0":
        bits.append("마법 계수 중심.")
    elif ap != "0":
        bits.append("물리 계수 중심.")
    hrs = (d.get("hit_radius_slash") or "0/0/0/0").strip()
    if any((p.strip() or "0") != "0" for p in hrs.split("/")):
        bits.append("히트0~3 구 반경 중 비0 있음.")
    return " ".join(bits)


def fandom_thumbnail_url(article_title: str, thumbsize: int = 600) -> str | None:
    """Fandom `pageimages` = 위키 인포박스와 같은 대표 썸네일(레날라의 Queen_Rennala.webp와 동일 출처 계열)."""
    qs = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": article_title,
            "prop": "pageimages",
            "format": "json",
            "pithumbsize": str(thumbsize),
        }
    )
    api = "https://eldenring.fandom.com/api.php?" + qs
    try:
        req = urllib.request.Request(api, headers={"User-Agent": WIKI_UA})
        with urllib.request.urlopen(req, timeout=22) as resp:
            j = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("Fandom API skip:", article_title, e)
        return None
    for pid, page in j.get("query", {}).get("pages", {}).items():
        if int(pid) < 0:
            continue
        th = page.get("thumbnail") or {}
        src = th.get("source")
        if src:
            return src
    return None


def boss_portrait_dest(stem: str, image_url: str) -> Path:
    """Wikia URL 은 …/파일.jpeg/revision/… 형태라 split 후 endswith 만으로는 확장자를 못 잡는다."""
    u = (image_url or "").lower()
    if ".jp" in u:
        return OUT_DIR / f"{stem}_boss_wiki.jpg"
    if ".webp" in u:
        return OUT_DIR / f"{stem}_boss_wiki.webp"
    return OUT_DIR / f"{stem}_boss_wiki.png"


def clear_boss_portraits(stem: str) -> None:
    for p in OUT_DIR.glob(f"{stem}_boss_wiki.*"):
        try:
            p.unlink()
        except OSError:
            pass


def download_portrait(stem: str, urls: list[str | None]) -> Path:
    """첫 성공 URL만 저장. 실패 시 존재하지 않을 수 있는 기본 경로(.png) 반환."""
    clear_boss_portraits(stem)
    for u in urls:
        if not u:
            continue
        dest = boss_portrait_dest(stem, u)
        if download_image(u, dest):
            return dest
    return OUT_DIR / f"{stem}_boss_wiki.png"


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": WIKI_UA})
        with urllib.request.urlopen(req, timeout=25) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print("Image skip:", dest.name, e)
        return False


def _save_combined_atkcoef_chart(data, dest: Path) -> None:
    """물리·마법·화염·벼락·스태미나 계수를 한 그래프에 가로 막대로 표시."""
    labels = [
        f"{d.get('attack_ix', i)}. {d['label_chart']}"
        for i, d in enumerate(data, start=1)
    ]
    n = len(labels)
    y = np.arange(n, dtype=float)
    phys = [int(d["atkphys"]) for d in data]
    mag = [int(d["atkmag"]) for d in data]
    fire = [int(d["atkfire"]) for d in data]
    thun = [int(d["atkthun"]) for d in data]
    stam = [int(d["atkstam"]) for d in data]
    fs = 9
    row_h = 0.62
    fig_h = max(7.5, n * row_h + 2.4)
    bw = 0.11
    gap = 0.028
    step = bw + gap
    offs = np.array([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=float) * step
    _sep_color = (0.72, 0.72, 0.74, 0.55)

    all_flat = [v for row in zip(phys, mag, fire, thun, stam) for v in row]
    if not all_flat or max(all_flat) == 0:
        fig, ax = plt.subplots(figsize=(11, max(1.2, min(2.4, n * 0.25 + 0.8))))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("물리·마법·화염·벼락·스태미나 피해 계수", fontsize=12, pad=12)
        ax.text(
            0.5,
            0.5,
            "물리·마법·화염·벼락·스태미나 계수가 모두 0입니다.",
            ha="center",
            va="center",
            fontsize=12,
            transform=ax.transAxes,
        )
        fig.tight_layout()
        fig.savefig(dest, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return

    fig, ax = plt.subplots(figsize=(11, fig_h))
    # 행 사이 흐린 구분선(막대·라벨보다 뒤)
    for k in range(1, n):
        ax.axhline(k - 0.5, color=_sep_color, linewidth=0.75, zorder=0)
    ax.barh(y + offs[0], phys, height=bw, label="물리", color="#59a14f", zorder=2)
    ax.barh(y + offs[1], mag, height=bw, label="마법", color="#4e79a7", zorder=2)
    ax.barh(y + offs[2], fire, height=bw, label="화염", color="#e15759", zorder=2)
    ax.barh(y + offs[3], thun, height=bw, label="벼락", color="#edc948", zorder=2)
    ax.barh(y + offs[4], stam, height=bw, label="스태미나", color="#b07aa1", zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=fs)
    ax.invert_yaxis()
    ax.set_xlabel("계수", fontsize=11)
    ax.set_title("물리·마법·화염·벼락·스태미나 피해 계수", fontsize=12, pad=8)
    _handles, _labels = ax.get_legend_handles_labels()
    _leg_lo = ax.legend(_handles, _labels, fontsize=9, loc="lower right")
    ax.add_artist(_leg_lo)
    ax.legend(_handles, _labels, fontsize=9, loc="upper right")
    ax.grid(axis="x", alpha=0.3)
    xmax = max(max(phys), max(mag), max(fire), max(thun), max(stam), 1)
    ax.set_xlim(0, xmax * 1.15 + 5)
    for yi, p, m, f, t, s in zip(y, phys, mag, fire, thun, stam):
        offx = xmax * 0.012
        if p:
            ax.text(p + offx, yi + offs[0], str(p), va="center", fontsize=7)
        if m:
            ax.text(m + offx, yi + offs[1], str(m), va="center", fontsize=7)
        if f:
            ax.text(f + offx, yi + offs[2], str(f), va="center", fontsize=7)
        if t:
            ax.text(t + offx, yi + offs[3], str(t), va="center", fontsize=7)
        if s:
            ax.text(s + offx, yi + offs[4], str(s), va="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(dest, dpi=150, bbox_inches="tight")
    plt.close(fig)


def charts_for(data, img_chart: Path, stem: str) -> bool:
    """단일 PNG: 물리·마법·화염·벼락·스태미나 통합. 예전 파일명(atkmag/element_mix)은 삭제."""
    out_dir = img_chart.parent
    for name in (f"{stem}_atkcoef.png", f"{stem}_atkmag.png", f"{stem}_element_mix.png"):
        try:
            (out_dir / name).unlink()
        except OSError:
            pass
    if not data:
        return False
    _save_combined_atkcoef_chart(data, img_chart)
    return True


def write_boss_html(
    *,
    stem: str,
    page_title: str,
    h1_title: str,
    active_href: str,
    data: list,
    img_chart: Path,
    portrait_urls: list[str | None],
    wiki_link: str,
    map_link: str,
    overview_rows_html: str,
    summary_rows_html: str,
    skill_note_html: str,
    nav_pages: list[tuple[str, str]] | None = None,
):
    data_vis = filter_attack_rows(data)
    for i, d in enumerate(data_vis, start=1):
        d["attack_ix"] = i
    show_chart = charts_for(data_vis, img_chart, stem)
    img_boss = download_portrait(stem, portrait_urls)

    graph_html = (
        f'  <figure class="chart">\n    <img src="{img_chart.name}" alt="물리·마법·화염·벼락·스태미나 피해 계수" />\n  </figure>\n'
        if show_chart
        else ""
    )
    graph_section_html = ""
    if graph_html:
        graph_section_html = "  <h2>그래프</h2>\n" + graph_html
    elif data and not data_vis:
        graph_section_html = """  <h2>그래프</h2>
  <p class="chart-note">이 구간은 물리·마법·화염·벼락·스태미나 계수가 모두 0인 행만 있어 그래프를 생략했습니다.</p>
"""

    gloss_name = "glossary_WIKI.html"
    rows_html = []
    for d in data_vis:
        note = note_for_row(d)
        name_1 = br.esc(br.label_table_oneline(d["label_table"]))
        tip = br.esc_attr(note)
        ix = int(d["attack_ix"])
        cells = f'<td class="atk-ix">{ix}</td><th class="atk-name" title="{tip}">{name_1}</th>'
        cells += "".join(
            f"<td>{br.format_attack_table_cell(c, d.get(c, ''))}</td>"
            for c in br.DATA_COLS
        )
        rows_html.append(f"<tr>{cells}</tr>")
    rows_html = "\n".join(rows_html)
    header_row = '<th class="atk-ix">#</th><th class="atk-name-h">공격 이름</th>' + "".join(
        f"<th>{br.esc(ko)}</th>" for ko in br.DATA_COLS_KO
    )

    img_boss_rel = img_boss.name if img_boss.exists() else ""
    boss_img_block = ""
    if img_boss_rel:
        boss_img_block = (
            f'<img src="{img_boss_rel}" width="200" alt="{br.esc(h1_title)}" />'
        )

    boss_block = f"""
  <section class="boss">
    <div class="boss-grid">
      <div class="boss-img">{boss_img_block}</div>
      <div class="boss-body">
        <table class="data boss-overview">
          <tbody>
{overview_rows_html}
          </tbody>
        </table>
        <p class="wiki-src"><a href="{wiki_link}" target="_blank" rel="noopener">Fextralife 위키 원문</a>을 바탕으로 번역·요약함. 아래 「공격별 수치」는 atkparam_npc 테이블 발췌.</p>
      </div>
    </div>
  </section>
"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{br.esc(page_title)}</title>
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
  td.atk-ix {{
    text-align: right;
    width: 2.75rem;
    font-variant-numeric: tabular-nums;
    background: #f3f5f9;
    color: var(--muted);
    font-weight: 600;
  }}
  table.atk-params th.atk-name,
  table.atk-params th.atk-name-h {{
    white-space: nowrap;
    min-width: 13.5rem;
    max-width: 36rem;
    padding-left: 10px;
    padding-right: 12px;
  }}
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
  p.skill-note {{ font-size: 0.88rem; color: var(--muted); margin: 0.75rem 0 0; line-height: 1.55; max-width: 52rem; }}
  .map-link {{ margin: 6px 0 0; }}
  .map-link a {{ color: var(--accent); }}
{br.LAYOUT_CSS}
</style>
</head>
<body>
<div class="layout">
{br.render_sidebar(active_href, nav_pages)}
  <div class="content-main">
<main>
  <h1>{br.esc(h1_title)}</h1>

{boss_block}

  <p class="map-link"><a href="{map_link}" target="_blank" rel="noopener">인터랙티브 맵</a></p>

  <h2>스킬</h2>
  <table class="data">
    <thead><tr><th>이름</th><th>내용</th></tr></thead>
    <tbody>
{summary_rows_html}
    </tbody>
  </table>
{skill_note_html}
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
{br.SIDEBAR_SCROLL_SCRIPT}
</body>
</html>
"""
    out_path = OUT_DIR / f"{stem}.html"
    out_path.write_text(html, encoding="utf-8")
    print("Wrote", out_path)


SKILL_NOTE_HTML = """<p class="skill-note">「스킬」 표는 <strong>위키·전투 흐름을 기준으로 정리한 요약</strong>입니다(보스별 수동 입력). 아래 「공격별 수치」는 <strong>atkparam_npc에 등록된 공격 행마다 한 줄</strong>이라 위키 기술 이름과 1:1로 맞지 않고, 히트·변형·특효 ID 차이 등으로 <strong>같은 동작도 여러 행</strong>으로 쪼개져 행 수가 많습니다.</p>"""

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Blaidd (CSV 251–293) ---
    blaidd_data = load_slice(251, 293)
    blaidd_stem = "blaidd_251-293"
    blaidd_chart = OUT_DIR / f"{blaidd_stem}_atkcoef.png"
    blaidd_thumb = fandom_thumbnail_url("Blaidd_the_Half-Wolf")
    blaidd_portrait_urls: list[str | None] = []
    if blaidd_thumb:
        blaidd_portrait_urls.append(blaidd_thumb)
    blaidd_portrait_urls.append(
        "https://static.wikia.nocookie.net/eldenring/images/7/7f/ER_NPC_Closeup_Blaidd.png/revision/latest/scale-to-width-down/600"
    )
    blaidd_overview = """
            <tr><th>개요</th><td>라니의 그림자로 두 손가락이 만든 반달 거인. 미스트우드에서 이리 데릴 투기와 연계되고, 레드마네 축제 등에서 NPC로 조력한다. 라니 루트 후반에는 적대 NPC로 등장할 수 있다.</td></tr>
            <tr><th>위치</th><td>첫 조우는 미스트우드(이리 데릴). 이후 레드마네·왕도 폐허 인근 등 퀘스트 진행에 따라 이동·전투가 이어진다.</td></tr>
            <tr><th>드롭</th><td>적대 전투 시 왕실 대검, 반달의 세트 일부, 룬 등(조건·패치에 따라 상이).</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 단일 페이즈 약 4,500 전후(출처·패치에 따라 변동 가능).</td></tr>
            <tr><th>흡수·내성</th><td>냉기·출혈 등 상태이상과 태세는 위키 원문과 대조. 수치 표는 atkparam_npc 의 공격 파라미터만 반영한다.</td></tr>
            <tr><th>부가</th><td>NPC 조력 시에는 아군 판정 행이 섞일 수 있다. 위키의 인물 설명·퀘스트 분기는 원문을 본다.</td></tr>
    """
    blaidd_summary = """
      <tr><td>대검 베기·내려찍기</td><td>왕실 대검을 휘두르는 기본 근접. 물리 계수·밀어냄·피해 단계가 함께 잡힌 행이 다수이며, speffect만 다른 변형 짝이 섞인다.</td></tr>
      <tr><td>점프 공격</td><td>공중에서 찍는 타격. 위력·판정 크기가 다른 변형이 나뉘어 있다.</td></tr>
      <tr><td>발톱·구르기</td><td>늑대형 근접. 짧은 판정과 연계 행이 atkparam에 따로 잡힌다.</td></tr>
      <tr><td>원거리(발사체)</td><td>이름에 발사체(데이터 표기 Bullet)가 붙은 행. 별도 히트 판정이다.</td></tr>
    """
    write_boss_html(
        stem=blaidd_stem,
        page_title="Blaidd the Half-Wolf",
        h1_title="Blaidd the Half-Wolf",
        active_href=f"{blaidd_stem}.html",
        data=blaidd_data,
        img_chart=blaidd_chart,
        portrait_urls=blaidd_portrait_urls,
        wiki_link="https://eldenring.wiki.fextralife.com/Blaidd+the+Half-Wolf",
        map_link="https://eldenring.wiki.fextralife.com/Interactive+Map?id=4452&code=mapA",
        overview_rows_html=blaidd_overview,
        summary_rows_html=blaidd_summary,
        skill_note_html=SKILL_NOTE_HTML,
        nav_pages=br.NAV_PAGES,
    )

    # --- Black Knife Assassin (CSV 333–361) ---
    bka_data = load_slice(333, 361)
    bka_stem = "black_knife_333-361"
    bka_chart = OUT_DIR / f"{bka_stem}_atkcoef.png"
    bka_thumb = fandom_thumbnail_url("Black_Knife_Assassin")
    bka_portrait_urls: list[str | None] = []
    if bka_thumb:
        bka_portrait_urls.append(bka_thumb)
    bka_portrait_urls.append(
        "https://static.wikia.nocookie.net/eldenring/images/3/36/ER_Black_Knife_Assassin_Leyndell.jpeg/revision/latest/scale-to-width-down/600"
    )
    bka_overview = """
            <tr><th>개요</th><td>흑도 음모와 연결된 암살자. 지하 묘지·성문 앞 차지 던전 등에 미니보스로 복수 배치된다.</td></tr>
            <tr><th>위치</th><td>리무그레이브 흑도 지하 묘지, 스톰빌 성문 앞 호스 차지 던전, 리에니에 흑도 감옥 등.</td></tr>
            <tr><th>드롭</th><td>흑도(단검), 룬 등. 맵·진행도에 따라 드롭 구성이 달라질 수 있다.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터마다 체력이 다름. 위키의 해당 던전 페이지를 참고.</td></tr>
            <tr><th>흡수·내성</th><td>인간형 미니보스에 가까운 내성. 정확한 흡수율은 위키 원문 확인.</td></tr>
            <tr><th>부가</th><td>은신·돌진 패턴이 특징. 공격 수치 표는 atkparam_npc 의 공격 파라미터만 반영한다.</td></tr>
    """
    bka_summary = """
      <tr><td>단검 연속 찌르기</td><td>기본 단검 콤보. 물리 계수 위주이고 이 구간 atkparam 의 atkmag 는 대부분 0이다.</td></tr>
      <tr><td>은신 암습</td><td>기습·급습류. 거리 등 수치 차이로 변형 행이 나뉜다.</td></tr>
      <tr><td>흑염·신성 계열</td><td>검은 불꽃 등 패턴으로 추정되는 행이 섞인다(이름은 도구 기준).</td></tr>
      <tr><td>원거리(발사체)</td><td>발사체(Bullet) 표기 행. 단검 본체와 별도 판정.</td></tr>
    """
    write_boss_html(
        stem=bka_stem,
        page_title="Black Knife Assassin",
        h1_title="Black Knife Assassin",
        active_href=f"{bka_stem}.html",
        data=bka_data,
        img_chart=bka_chart,
        portrait_urls=bka_portrait_urls,
        wiki_link="https://eldenring.wiki.fextralife.com/Black+Knife+Assassin",
        map_link="https://eldenring.wiki.fextralife.com/Interactive+Map?id=5844&code=mapA",
        overview_rows_html=bka_overview,
        summary_rows_html=bka_summary,
        skill_note_html=SKILL_NOTE_HTML,
        nav_pages=br.NAV_PAGES,
    )


if __name__ == "__main__":
    main()
