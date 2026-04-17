# -*- coding: utf-8 -*-
"""atkparam_npc.csv 에서 큐레이션된 보스 구간만 HTML·차트·boss_nav_extra.json 생성, ListUrl 나머지 파일 제거."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

import build_test_boss_docs as bt

from boss_curated_content import (
    BOSS_SKILL_SUMMARY_HTML,
    CURATED_BOSS_META,
    overview_for_key,
)

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "ListUrl"
SRC = BASE / "atkparam_npc.csv"
NAV_JSON = OUT_DIR / "boss_nav_extra.json"

# prune_listurl 에서 삭제하지 않음 (GitHub Pages 루트·목차).
LISTURL_PRUNE_SKIP_NAMES = frozenset(
    {"boss_nav_extra.json", "index.html", ".nojekyll"}
)

BRACKET = re.compile(r"\[([^\]]+)\]")

# 수동 정밀 문서와 동일 파일명·한글 네비를 유지(샘플 스크립트와 공유).
BOSS_DOC_SPECIAL: dict[str, dict] = {
    "Blaidd the Half-Wolf": {
        "stem": "blaidd_251-293",
        "nav": "Blaidd the Half-Wolf",
        "page_title": "Blaidd the Half-Wolf",
        "h1_title": "Blaidd the Half-Wolf",
        "fandom_title": "Blaidd_the_Half-Wolf",
        "wiki_link": "https://eldenring.wiki.fextralife.com/Blaidd+the+Half-Wolf",
        "map_link": "https://eldenring.wiki.fextralife.com/Interactive+Map?id=4452&code=mapA",
        "portraits_extra": [
            "https://static.wikia.nocookie.net/eldenring/images/7/7f/ER_NPC_Closeup_Blaidd.png/revision/latest/scale-to-width-down/600"
        ],
        "overview": """
            <tr><th>개요</th><td>라니의 그림자로 두 손가락이 만든 반달 거인. 미스트우드에서 이리 데릴 투기와 연계되고, 레드마네 축제 등에서 NPC로 조력한다. 라니 루트 후반에는 적대 NPC로 등장할 수 있다.</td></tr>
            <tr><th>위치</th><td>첫 조우는 미스트우드(이리 데릴). 이후 레드마네·왕도 폐허 인근 등 퀘스트 진행에 따라 이동·전투가 이어진다.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 단일 페이즈 약 4,500 전후(출처·패치에 따라 변동 가능).</td></tr>
            <tr><th>면역</th><td>냉기·출혈 등 상태이상과 태세는 위키 원문과 대조. 수치 표는 atkparam_npc 의 공격 파라미터만 반영한다.</td></tr>
            <tr><th>약점</th><td>NPC 조력 시에는 아군 판정 행이 섞일 수 있다. 위키 Negation이 낮은 속성·유형이 유리. 위키의 인물 설명·퀘스트 분기는 원문을 본다.</td></tr>
    """,
        "summary": """
      <tr><td>대검 베기·내려찍기</td><td>왕실 대검을 휘두르는 기본 근접. 물리 계수·밀어냄·피해 단계가 함께 잡힌 행이 다수이며, speffect만 다른 변형 짝이 섞인다.</td></tr>
      <tr><td>점프 공격</td><td>공중에서 찍는 타격. 위력·판정 크기가 다른 변형이 나뉘어 있다.</td></tr>
      <tr><td>발톱·구르기</td><td>늑대형 근접. 짧은 판정과 연계 행이 atkparam에 따로 잡힌다.</td></tr>
      <tr><td>원거리(발사체)</td><td>이름에 발사체(데이터 표기 Bullet)가 붙은 행. 별도 히트 판정이다.</td></tr>
    """,
    },
    "Black Knife Assassin": {
        "stem": "black_knife_333-361",
        "nav": "Black Knife Assassin",
        "page_title": "Black Knife Assassin",
        "h1_title": "Black Knife Assassin",
        "fandom_title": "Black_Knife_Assassin",
        "wiki_link": "https://eldenring.wiki.fextralife.com/Black+Knife+Assassin",
        "map_link": "https://eldenring.wiki.fextralife.com/Interactive+Map?id=5844&code=mapA",
        "portraits_extra": [
            "https://static.wikia.nocookie.net/eldenring/images/3/36/ER_Black_Knife_Assassin_Leyndell.jpeg/revision/latest/scale-to-width-down/600"
        ],
        "overview": """
            <tr><th>개요</th><td>흑도 음모와 연결된 암살자. 지하 묘지·성문 앞 차지 던전 등에 미니보스로 복수 배치된다.</td></tr>
            <tr><th>위치</th><td>리무그레이브 흑도 지하 묘지, 스톰빌 성문 앞 호스 차지 던전, 리에니에 흑도 감옥 등.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터마다 체력이 다름. 위키의 해당 던전 페이지를 참고.</td></tr>
            <tr><th>면역</th><td>인간형 미니보스에 가까운 저항·면역. 정확한 수치는 위키 원문 확인.</td></tr>
            <tr><th>약점</th><td>은신·돌진 패턴 대응. 위키 Negation이 낮은 유형이 유리. 공격 수치 표는 atkparam_npc 의 공격 파라미터만 반영한다.</td></tr>
    """,
        "summary": """
      <tr><td>단검 연속 찌르기</td><td>기본 단검 콤보. 물리 계수 위주이고 이 구간 atkparam 의 atkmag 는 대부분 0이다.</td></tr>
      <tr><td>은신 암습</td><td>기습·급습류. 거리 등 수치 차이로 변형 행이 나뉜다.</td></tr>
      <tr><td>흑염·신성 계열</td><td>검은 불꽃 등 패턴으로 추정되는 행이 섞인다(이름은 도구 기준).</td></tr>
      <tr><td>원거리(발사체)</td><td>발사체(Bullet) 표기 행. 단검 본체와 별도 판정.</td></tr>
    """,
    },
    "Beast Clergyman": {
        "stem": "npc_362_423_Beast_Clergyman",
        "nav": "Beast Clergyman",
        "page_title": "Beast Clergyman (흑검 말리케스)",
        "h1_title": "Beast Clergyman (흑검 말리케스)",
        "fandom_title": "Maliketh,_the_Black_Blade",
        "portraits_extra": [
            "https://static.wikia.nocookie.net/eldenring/images/f/fd/"
            "ER_Beast_Clergyman.png/revision/latest/scale-to-width-down/400"
        ],
        "wiki_link": "https://eldenring.wiki.fextralife.com/Beast+Clergyman",
        "map_link": (
            "https://eldenring.wiki.fextralife.com/Interactive+Map?"
            "id=4660&lat=-125.085937&lng=221.027742&code=mapA"
        ),
        "overview": """
            <tr><th>개요</th><td>구랭(Gurranq)과 동일 존재로 강하게 암시되는 <strong>전설 보스</strong>. 이 전투 패배는 세계의 구랭 NPC에게 죽음 플래그를 주지 않는다. <strong>필수 보스</strong>(엔드게임·잿빛 왕도 등 진행). HP를 약 <strong>50~55%</strong>까지 깎으면 컷신 후 <strong>Maliketh, the Black Blade</strong> 2페이즈로 이어진다.</td></tr>
            <tr><th>위치</th><td><strong>Crumbling Farum Azula</strong> 후반. 가장 가까운 은혜: <strong>Beside the Great Bridge</strong> (큰 다리 옆).</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 <strong>NG HP 10,620</strong> (Beast Clergyman 1페이즈 구간). NG+·패치에 따라 변동 가능.</td></tr>
            <tr><th>면역</th><td>독·부패·출혈·동상 저항, 수면·광기·죽음 면역 등 — 위키 <em>Resistance</em>.</td></tr>
            <tr><th>약점</th><td>위키 <em>Negation</em>: 표준·타격·베기·관통·마법·화염·벼락·신성(숫자가 클수록 해당 속성이 더 막힘). 태세(Stance) 80, 태세 붕괴 시 치명타. 정령 봉환 가능. 2페이즈 말리케스 대비 <strong>Blasphemous Claw</strong> 등은 위키 공략 참고. 아래 atkparam 표는 <strong>가하는 공격</strong>만 반영한다.</td></tr>
    """,
        "summary": """
      <tr><td>근접·연장 판정</td><td>Beast Clergyman 의 atkparam 행 다수는 동작 변형·히트박스·speffect 차이로 나뉩니다.</td></tr>
      <tr><td>원거리·발사체</td><td>발사체(Bullet) 등 접두가 붙은 행은 본체와 별도 판정일 수 있습니다.</td></tr>
      <tr><td>기타</td><td>스킬 표는 위키 요약이 아니라 데이터 기반 일반 안내입니다. 정밀한 패턴 설명은 위키를 본다.</td></tr>
    """,
    },
}

# CSV rowname 의 `[키]` 와 문자열이 정확히 같아야 함.
# 아래는 사용자 제공 공식 한글명 목록과만 연결(임의 번역 없음). 목록에 없는 키는 영문만 표시.
OFFICIAL_KO: dict[str, str] = {
    "Azula Beastman": "파름 아즈라의 수인",
    "Burial Watchdog": "환수의 파수견",
    "Crystalian": "아인 두목 형제",
    "Crucible Knight": "도가니의 기사",
    "Leonine Misbegotten": "사자 혼종",
    "Royal Rider": "친위기사 로레타",
    "Elemer of the Briar": "철가시 엘레메르",
    "Dragonlord Placidusax": "용왕 플라키두삭스",
    "Commander": "노장 니아르",
    "Tree Sentinel": "트리 가드",
    "Ancestor Spirit": "선조령",
    "Godskin Apostle": "신의 살갗의 사도",
    "Ancient Dragon": "사룡 포르삭스",
    "Morgott": "엘데의 왕 모르고트",
    "Godrick the Grafted": "접목의 고드릭",
    "Red Wolf of Radagon": "라다곤의 붉은 늑대",
    "Starscourge Radahn": "별 부수는 라단",
    "Fire Giant": "불의 거인",
    "Malenia": "미켈라의 칼날 말레니아",
    "Mohg": "피의 군주 모그",
    "Radagon": "황금률 라다곤",
    "Hoarah Loux": "전사 호라 루",
}

# 사이드바 전체 순서. __RENNALA__·__RYKARD__ 는 CSV 키가 아님(레날라는 수동 문서, 라이커드는 CSV 구간 없음).
# 모르고트는 동일 HTML(npc_505_670)에 멀기트·왕 두 줄.
NAV_RENNALA = "__RENNALA__"
NAV_RYKARD = "__RYKARD__"

CURATED_NAV_ORDER: list[tuple[str, str]] = [
    ("Azula Beastman", "파름 아즈라의 수인"),
    ("Burial Watchdog", "환수의 파수견"),
    ("Crystalian", "아인 두목 형제"),
    ("Crucible Knight", "도가니의 기사"),
    ("Leonine Misbegotten", "사자 혼종"),
    ("Royal Rider", "친위기사 로레타"),
    ("Elemer of the Briar", "철가시 엘레메르"),
    ("Dragonlord Placidusax", "용왕 플라키두삭스"),
    ("Commander", "노장 니아르"),
    ("Tree Sentinel", "트리 가드"),
    ("Ancestor Spirit", "선조령"),
    ("Godskin Apostle", "신의 살갗의 사도"),
    ("Ancient Dragon", "사룡 포르삭스"),
    ("Morgott", "끔찍한 흉조 멀기트"),
    ("Godrick the Grafted", "접목의 고드릭"),
    ("Red Wolf of Radagon", "라다곤의 붉은 늑대"),
    (NAV_RENNALA, "만월의 여왕 레날라"),
    ("Starscourge Radahn", "별 부수는 라단"),
    ("Fire Giant", "불의 거인"),
    ("Beast Clergyman", "흑검 말리케스"),
    ("Hoarah Loux", "전사 호라 루"),
    ("Radagon", "황금률 라다곤"),
    (NAV_RYKARD, "모독의 군주 라이커드"),
    ("Morgott", "엘데의 왕 모르고트"),
    ("Mohg", "피의 군주 모그"),
    ("Malenia", "미켈라의 칼날 말레니아"),
]

CURATED_KEYS_UNIQUE: list[str] = []
for _k, _ in CURATED_NAV_ORDER:
    if _k in (NAV_RENNALA, NAV_RYKARD):
        continue
    if _k not in CURATED_KEYS_UNIQUE:
        CURATED_KEYS_UNIQUE.append(_k)
CURATED_KEYS = frozenset(CURATED_KEYS_UNIQUE)


def display_title(en_key: str) -> str:
    ko = OFFICIAL_KO.get(en_key)
    return f"{en_key} ({ko})" if ko else en_key


def bracket_inner(rowname: str) -> str | None:
    if not rowname:
        return None
    m = BRACKET.search(rowname)
    return m.group(1).strip() if m else None


def safe_slug(key: str, maxlen: int = 44) -> str:
    nfd = unicodedata.normalize("NFKD", key)
    ascii_only = "".join(c for c in nfd if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", "_", ascii_only).strip("_")
    return (s[:maxlen] or "x")


def discover_groups(rows: list[list[str]], idx_rowname: int, min_rows: int = 4):
    """rowname 안의 [키]로 구간을 열고, 빈 rowname 은 직전 키 구간을 연장한다. Rennala 는 수동 레날라 문서와 겹치므로 제외."""
    groups: list[dict] = []
    cur: dict | None = None

    for line_no in range(2, len(rows) + 1):
        row = rows[line_no - 1]
        rn = row[idx_rowname] if idx_rowname < len(row) else ""
        inner = bracket_inner(rn)

        if inner is None:
            if cur is not None:
                cur["end"] = line_no
            continue

        if "Rennala" in inner:
            if cur is not None:
                groups.append(cur)
                cur = None
            continue

        if cur is None or inner != cur["key"]:
            if cur is not None:
                groups.append(cur)
            cur = {"key": inner, "start": line_no, "end": line_no}
        else:
            cur["end"] = line_no

    if cur is not None:
        groups.append(cur)

    return [g for g in groups if g["end"] - g["start"] + 1 >= min_rows]


def fextralife_wiki_link(key: str) -> str:
    # Fextralife 경로: 공백을 + 로 두는 경우가 많음. 쉼표 등은 브라우저가 인코딩한다.
    return "https://eldenring.wiki.fextralife.com/" + key.replace(" ", "+")


# CSV [키]와 달리 Fandom 에서 보스 일러스트가 붙은 문서 제목이 다른 경우.
# pageimages API 는 짧은 이름(예: Radagon)에는 thumbnail 이 없고,
# 긴 제목(Radagon of the Golden Order)에만 있는 경우가 많다.
FANDOM_PORTRAIT_ALIASES: dict[str, list[str]] = {
    "Radagon": ["Radagon_of_the_Golden_Order"],
    "Malenia": ["Malenia,_Blade_of_Miquella"],
    "Morgott": ["Morgott,_the_Omen_King"],
    "Godfrey": ["Godfrey,_First_Elden_Lord"],
    "Mohg": ["Mohg,_Lord_of_Blood"],
    "Hoarah Loux": ["Hoarah_Loux,_Warrior"],
}


def fandom_title_candidates(key: str, spec: dict | None) -> list[str]:
    if spec and spec.get("fandom_title"):
        return [str(spec["fandom_title"])]
    k = key.strip()
    out: list[str] = []
    for cand in (
        k.replace(" ", "_"),
        k.replace(" ", "_").replace(",", "%2C"),
        re.sub(r"[,']", "", k).replace(" ", "_"),
    ):
        if cand and cand not in out:
            out.append(cand)
    for alias in FANDOM_PORTRAIT_ALIASES.get(k, []):
        if alias and alias not in out:
            out.append(alias)
    return out


def portrait_urls_for_key(key: str) -> list[str | None]:
    spec = BOSS_DOC_SPECIAL.get(key)
    meta = CURATED_BOSS_META.get(key, {})
    extras: list = list(meta.get("portraits_extra") or [])
    extras.extend((spec or {}).get("portraits_extra") or [])
    titles: list[str] = []
    if meta.get("fandom_title"):
        titles.append(str(meta["fandom_title"]))
    titles.extend(fandom_title_candidates(key, spec))
    seen: set[str] = set()
    ordered: list[str] = []
    for t in titles:
        if t and t not in seen:
            seen.add(t)
            ordered.append(t)
    urls: list[str | None] = []
    for t in ordered:
        u = bt.fandom_thumbnail_url(t)
        if u:
            urls.append(u)
            break
    urls.extend(extras)
    return urls


def generic_summary(key: str) -> str:
    return f"""
      <tr><td>근접·연장 판정</td><td>{key} 의 atkparam 행 다수는 동작 변형·히트박스·speffect 차이로 나뉩니다.</td></tr>
      <tr><td>원거리·발사체</td><td>발사체(Bullet) 등 접두가 붙은 행은 본체와 별도 판정일 수 있습니다.</td></tr>
      <tr><td>기타</td><td>스킬 표는 위키 요약이 아니라 데이터 기반 일반 안내입니다. 정밀한 패턴 설명은 위키를 본다.</td></tr>
    """


def stem_nav_labels(group: dict) -> tuple[str, str, str, str]:
    """stem, sidebar_nav_label, page_title, h1_title"""
    key = group["key"]
    a, b = group["start"], group["end"]
    spec = BOSS_DOC_SPECIAL.get(key)
    if spec:
        return (
            str(spec["stem"]),
            str(spec["nav"]),
            str(spec["page_title"]),
            str(spec["h1_title"]),
        )
    stem = f"npc_{a}_{b}_{safe_slug(key)}"
    short = key if len(key) <= 28 else key[:25] + "…"
    meta = CURATED_BOSS_META.get(key, {})
    if meta.get("page_title") and meta.get("h1_title"):
        return stem, short, str(meta["page_title"]), str(meta["h1_title"])
    full = display_title(key)
    return stem, short, full, full


def build_curated_nav_tail(groups: list[dict]) -> list[tuple[str, str]]:
    """boss_nav_extra.json 및 사이드바 전체(레날라·라이커드 플레이스홀더 포함)."""
    by_key = {g["key"]: g for g in groups}
    out: list[tuple[str, str]] = []
    for key, label in CURATED_NAV_ORDER:
        if key == NAV_RENNALA:
            out.append(("rennala_294-318.html", label))
        elif key == NAV_RYKARD:
            out.append(("rykard_placeholder.html", label))
        else:
            g = by_key[key]
            stem, _, _, _ = stem_nav_labels(g)
            out.append((f"{stem}.html", label))
    return out


def full_nav_for_sidebar(groups: list[dict]) -> list[tuple[str, str]]:
    return build_curated_nav_tail(groups)


def write_rykard_placeholder(nav_pages: list[tuple[str, str]]) -> None:
    """atkparam_npc 에 Rykard [키] 구간이 없어 자동 표를 만들 수 없을 때 안내 전용 페이지."""
    import build_rennala_doc as br

    p = OUT_DIR / "rykard_placeholder.html"
    title = "Rykard, Lord of Blasphemy (모독의 군주 라이커드)"
    wiki = "https://eldenring.wiki.fextralife.com/Rykard,+Lord+of+Blasphemy"
    map_url = "https://eldenring.wiki.fextralife.com/Interactive+Map?id=4104&code=mapA"
    stem_img = "rykard_placeholder"
    img_rel = ""
    thumb = bt.fandom_thumbnail_url("Rykard,_Lord_of_Blasphemy")
    if thumb:
        dest = bt.boss_portrait_dest(stem_img, thumb)
        if bt.download_image(thumb, dest):
            img_rel = dest.name

    boss_img_block = ""
    if img_rel:
        boss_img_block = (
            f'<img src="{br.esc(img_rel)}" width="200" alt="{br.esc(title)}" />'
        )

    overview_rows = f"""
            <tr><th>개요</th><td><strong>신을 삼키는 거신(God-Devouring Serpent)</strong>과 본체 <strong>모독의 군주 라이커드</strong>로 이어지는 <strong>2페이즈</strong> 데미갓 보스. 겔미르의 <strong>화산관(Volcano Manor)</strong> 최심부, 관객석이 있는 전장에서 조우한다. 거신과 합일을 택한 라이커드의 설정·대룬은 위키 로어를 본다. <strong>선택 보스</strong>이나 샤드베어러(대룬) 보스로 카운트되며, 레이든델 진입에 필요한 샤드베어러 두 명 중 한 명으로 잡을 수 있다(진행 방식에 따라 타니스 루트 등과 상호작용).</td></tr>
            <tr><th>위치</th><td><strong>Mt. Gelmir</strong> — 화산관 끝 웨이게이트 또는 타니스 계약·대화 분기 후 <strong>Audience Pathway</strong>(관객의 통로) 은혜로 이동. 안개 문 너머 전장. 입장 직후 왼쪽에서 <strong>뱀사냥꾼(Serpent-Hunter)</strong> 무기를 집어 전투에 쓴다.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 <strong>1페이즈(거신) HP 30,493</strong>, <strong>2페이즈(라이커드) HP 59,174</strong>, 방어력 115. NG+ 이후·패치는 위키 표 참고.</td></tr>
            <tr><th>면역</th><td><strong>광기(Madness) 면역</strong>. 독·부패·출혈·동상·수면 등은 위키 <em>Resistance</em> 수치.</td></tr>
            <tr><th>약점</th><td>두 페이즈 <em>Negation</em> 동일(위키): 표준·베기·관통 10, 타격 35, 마법·신성 40, <strong>화염 80</strong>, 벼락 20 등 — 숫자가 클수록 해당 속성이 더 막힘. 약점 부위는 <strong>머리</strong>. 태세 120, 패리 불가·치명타는 제한적. 상세 패턴·세팅은 위키 공략.</td></tr>
    """

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{br.esc(title)}</title>
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
  p {{ margin: 0.55rem 0; }}
  .boss {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; margin-bottom: 22px; }}
  .boss a {{ color: var(--accent); }}
  .boss-grid {{ display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start; }}
  .boss-img {{ flex: 0 0 auto; }}
  .boss-img img {{ max-width: 200px; height: auto; border-radius: 8px; }}
  .boss-body {{ flex: 1 1 320px; min-width: 0; }}
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
  table.boss-overview {{ margin-top: 0; font-size: 0.9rem; }}
  table.boss-overview th {{
    width: 9.5rem;
    white-space: nowrap;
    vertical-align: top;
  }}
  .wiki-src {{ font-size: 0.85rem; color: var(--muted); margin-top: 12px; }}
  p.skill-note {{ font-size: 0.88rem; color: var(--muted); margin: 0.75rem 0 0; line-height: 1.55; max-width: 52rem; }}
  .map-link {{ margin: 6px 0 0; }}
  .map-link a {{ color: var(--accent); }}
{br.LAYOUT_CSS}
</style>
</head>
<body>
<div class="layout">
{br.render_sidebar("rykard_placeholder.html", nav_pages)}
  <div class="content-main">
<main>
  <h1>{br.esc(title)}</h1>

  <section class="boss">
    <div class="boss-grid">
      <div class="boss-img">{boss_img_block}</div>
      <div class="boss-body">
        <table class="data boss-overview">
          <tbody>
{overview_rows}
          </tbody>
        </table>
        <p class="wiki-src"><a href="{wiki}" target="_blank" rel="noopener">Fextralife 위키 원문</a> 전투·맵·면역/약점 수치를 우선으로 하여 요약함.</p>
        <p class="skill-note"><code>atkparam_npc.csv</code>에 Rykard 전용 <code>[…]</code> 구간이 없어 다른 보스 페이지와 같은 방식의 「공격별 수치」표는 자동 생성하지 않습니다.</p>
      </div>
    </div>
  </section>

  <p class="map-link"><a href="{map_url}" target="_blank" rel="noopener">인터랙티브 맵</a></p>
</main>
  </div>
</div>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print("Wrote", p)


def prune_listurl(allowed_stems: set[str]) -> None:
    """큐레이션에 쓰이지 않는 ListUrl 파일 삭제 (boss_nav_extra.json 유지)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in list(OUT_DIR.iterdir()):
        if not p.is_file():
            continue
        if p.name in LISTURL_PRUNE_SKIP_NAMES:
            continue
        base = p.name.rsplit(".", 1)[0]
        ok = any(base == s or base.startswith(s + "_") for s in allowed_stems)
        if not ok:
            try:
                p.unlink()
                print("Removed:", p.name)
            except OSError as e:
                print("Remove failed:", p, e)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SRC.is_file():
        raise FileNotFoundError(str(SRC))

    with open(SRC, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        raise ValueError("CSV 가 비었습니다.")
    header = rows[0]
    if "rowname" not in header:
        raise KeyError("rowname 열이 필요합니다.")
    idx_rowname = header.index("rowname")

    groups = discover_groups(rows, idx_rowname, min_rows=4)
    by_key = {g["key"]: g for g in groups}
    missing = [k for k in CURATED_KEYS if k not in by_key]
    if missing:
        raise KeyError(f"큐레이션 키가 CSV 구간에 없음: {missing}")

    nav_tail = build_curated_nav_tail(groups)
    NAV_JSON.write_text(
        json.dumps(nav_tail, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Wrote", NAV_JSON, "entries:", len(nav_tail))

    full_nav = full_nav_for_sidebar(groups)
    write_rykard_placeholder(full_nav)

    default_map = (
        "https://eldenring.wiki.fextralife.com/Interactive+Map?id=0&code=mapA"
    )

    for key in CURATED_KEYS_UNIQUE:
        g = by_key[key]
        a, b = g["start"], g["end"]
        stem, _, page_title, h1_title = stem_nav_labels(g)
        spec = BOSS_DOC_SPECIAL.get(key)
        meta = CURATED_BOSS_META.get(key, {})
        overview = (spec or {}).get("overview") or overview_for_key(key, a, b)
        summary = (
            (spec or {}).get("summary")
            or BOSS_SKILL_SUMMARY_HTML.get(key)
            or generic_summary(key)
        )
        wiki = (spec or {}).get("wiki_link") or meta.get("wiki_link") or fextralife_wiki_link(key)
        mmap = (spec or {}).get("map_link") or meta.get("map_link") or default_map
        portraits = portrait_urls_for_key(key)

        data = bt.load_slice(a, b, label_mode="listurl_curated")
        img_chart = OUT_DIR / f"{stem}_atkcoef.png"

        print("Boss", key, a, b, "->", stem)
        bt.write_boss_html(
            stem=stem,
            page_title=page_title,
            h1_title=h1_title,
            active_href=f"{stem}.html",
            data=data,
            img_chart=img_chart,
            portrait_urls=portraits,
            wiki_link=wiki,
            map_link=mmap,
            overview_rows_html=overview,
            summary_rows_html=summary,
            skill_note_html=bt.SKILL_NOTE_HTML,
            nav_pages=full_nav,
        )

    # 레날라 HTML 을 다시 써서 사이드바·내부 링크가 최신 JSON 과 맞도록 함.
    rc = subprocess.run(
        [sys.executable, str(BASE / "build_rennala_doc.py")],
        cwd=str(BASE),
    )
    if rc.returncode != 0:
        sys.exit(rc.returncode)

    allowed_stems: set[str] = {"rennala_294-318", "glossary_WIKI", "rykard_placeholder"}
    for key in CURATED_KEYS_UNIQUE:
        st, _, _, _ = stem_nav_labels(by_key[key])
        allowed_stems.add(st)
    prune_listurl(allowed_stems)

    print("Done. Curated boss docs + Rennala; ListUrl pruned.")


if __name__ == "__main__":
    main()
