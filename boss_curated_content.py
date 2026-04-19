# -*- coding: utf-8 -*-
"""큐레이션 보스: Fextralife 위키 기준 한글 개요 표·위키 URL·표제·Fandom 썸네일 제목."""
from __future__ import annotations

# CSV 키 → 메타(선택). page_title·h1_title 이 있으면 stem_nav_labels 에 사용.
# wiki_link·map_link 가 있으면 build_all 에서 기본 Fextralife 생성 링크를 덮어씀.
CURATED_BOSS_META: dict[str, dict] = {
    # Fandom 문서 제목이 "Azula Beastman" 이 아니라 Beastman of Farum Azula 쪽에 대표 이미지가 있다.
    "Azula Beastman": {
        "fandom_title": "Beastman_of_Farum_Azula",
    },
    "Burial Watchdog": {
        "wiki_link": "https://eldenring.wiki.fextralife.com/Erdtree+Burial+Watchdog",
        "fandom_title": "Erdtree_Burial_Watchdog",
        "page_title": "Erdtree Burial Watchdog (환수의 파수견)",
        "h1_title": "Erdtree Burial Watchdog (환수의 파수견)",
    },
    "Royal Rider": {
        "wiki_link": "https://eldenring.wiki.fextralife.com/Royal+Knight+Loretta",
        "map_link": "https://eldenring.wiki.fextralife.com/Interactive+Map?id=1540&code=mapA",
        "fandom_title": "Royal_Knight_Loretta",
        "page_title": "Royal Knight Loretta (친위기사 로레타)",
        "h1_title": "Royal Knight Loretta (친위기사 로레타)",
        "portraits_extra": [
            "https://static.wikia.nocookie.net/eldenring/images/4/48/ER_Royal_Knight_Loretta.png/revision/latest/scale-to-width-down/600",
        ],
    },
    "Commander": {
        "wiki_link": "https://eldenring.wiki.fextralife.com/Commander+Niall",
        "map_link": "https://eldenring.wiki.fextralife.com/Interactive+map?id=3807&lat=-58.929687&lng=158.27116&code=mapA",
        "fandom_title": "Commander_Niall",
        "page_title": "Commander Niall (노장 니아르)",
        "h1_title": "Commander Niall (노장 니아르)",
    },
    "Morgott": {
        "wiki_link": "https://eldenring.wiki.fextralife.com/Morgott+the+Omen+King",
    },
}

# 개요 표 tbody 안쪽 HTML만 (드롭 행 없음). 행 제목: 면역 = 상태·면역, 약점 = 받는 피해 유리 속성·전술.
BOSS_OVERVIEW_HTML: dict[str, str] = {
    "Azula Beastman": """
            <tr><th>개요</th><td>파름 아즈라에 서식하는 수인(짐승인) 계열의 적. 대검·내려찍기·점프 공격 등 근접 위주 패턴을 쓴다. 위키의 <em>Azula Beastman</em>·던전 배치 설명을 본다.</td></tr>
            <tr><th>위치</th><td>Crumbling Farum Azula 등 — 동일 이름이라도 구역·인카운터마다 체력·행동이 다를 수 있다.</td></tr>
            <tr><th>체력 (NG)</th><td>배치별로 상이함. 위키 해당 구역 페이지의 HP 표를 참고.</td></tr>
            <tr><th>면역</th><td>독·부패·출혈 등 상태 이상은 위키 <em>Resistance</em> 표. 완전 면역 여부는 인카운터별로 확인.</td></tr>
            <tr><th>약점</th><td>위키 <em>Negation</em>이 낮은 속성·물리 유형(표준·베기·타격·관통·마법·화염 등)이 유리하다. 아래 atkparam 표는 <strong>가하는 공격</strong> 수치만 담는다.</td></tr>
    """,
    "Burial Watchdog": """
            <tr><th>개요</th><td>별칭 <strong>Erdtree Burial Watchdog</strong>. 지하 묘지 곳곳의 선택 필드 보스로 등장하는 석상 개 형태의 수호자. 대검·지팡이·원소 숨결 등 변종이 있다. 패링 가능·태세 80 등 전투 정보는 위키 원문을 본다.</td></tr>
            <tr><th>위치</th><td>스톰풋 지하 묘지, 임펄러스 지하 묘지, 클리프바텀 지하 묘지, 마이너 황금수 지하 묘지(쌍두), 윈덤 지하 묘지 등 <strong>여러 지하 묘지</strong>에 각각 배치된다. 인카운터마다 HP·방어·보상이 다르다.</td></tr>
            <tr><th>체력 (NG)</th><td>위치별로 약 1,200 HP ~ 3,400 HP 이상 등 상이함. NG+ 표는 위키.</td></tr>
            <tr><th>면역</th><td>일반형 기준 독·부패·출혈·동상·수면·광기 <strong>면역</strong>(위키 Resistance).</td></tr>
            <tr><th>약점</th><td>물리·마법·화염·벼락·신성은 위키 <em>Negation</em> %에 따라 유리한 속성이 갈린다. 소형은 <em>Lesser Burial Watchdog</em> 일반 적으로 구분.</td></tr>
    """,
    "Crystalian": """
            <tr><th>개요</th><td>수정으로 덮인 인간형 미니보스. 창·낫 등 무기 변종이 있고 둘이 동시에 등장하는 경우도 있다. 크리스탈 외피가 깨지기 전에는 일부 피해가 잘 들어가지 않는다.</td></tr>
            <tr><th>위치</th><td>리에니에 동굴·감옥, 시프라 강 등 여러 동굴/감옥.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터별 상이. 위키 해당 던전 페이지 참고.</td></tr>
            <tr><th>면역</th><td>출혈</td></tr>
            <tr><th>약점</th><td>표준, 파열</td></tr>
    """,
    "Crucible Knight": """
            <tr><th>개요</th><td>용사 도가니 기사단 소속 기사. 꼬리·날개 등 용의 힘을 쓰는 패턴이 특징. 실드·대검 등 무기 변종이 있다.</td></tr>
            <tr><th>위치</th><td>스톰빌 성, 리에니에, 깊은 뿌리 깊이 등 여러 필드·던전.</td></tr>
            <tr><th>체력 (NG)</th><td>배치별 상이.</td></tr>
            <tr><th>면역</th><td>상태 이상 저항·면역은 위키 해당 인카운터 페이지.</td></tr>
            <tr><th>약점</th><td>위키 <em>Negation</em>이 낮은 물리 유형·속성이 유리하다.</td></tr>
    """,
    "Leonine Misbegotten": """
            <tr><th>개요</th><td>사자 머리를 한 혼종. 빠른 연속 공격·점프 찍기 등이 특징인 미니보스.</td></tr>
            <tr><th>위치</th><td>성 내부·해안 등 — 위키에서 해당 구역을 검색.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터별 상이.</td></tr>
            <tr><th>면역</th><td>위키 Resistance·면역 항목.</td></tr>
            <tr><th>약점</th><td>위키 Negation이 낮은 공격 유형. 아래는 atkparam 구간 샘플이다.</td></tr>
    """,
    "Royal Rider": """
            <tr><th>개요</th><td>정식 명칭 <strong>Royal Knight Loretta</strong>. 카리아 영지를 수호하는 기사의 영혼으로, 말을 탄 채 할버드와 휘석 마법(글린트블레이드·대궁 등)을 사용한다. 선택 보스이나 <strong>세 자매</strong>·별의 시대 루트를 위해 격파가 필요한 경우가 많다.</td></tr>
            <tr><th>위치</th><td>리에니에 호수 북부 <strong>Caria Manor</strong> 상층 — <strong>Royal Moongazing Grounds</strong>(달을 보는 정원) 원형 전장. 가장 가까운 은혜: <strong>Manor Upper Level</strong>.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 기준 NG HP 약 <strong>4,214</strong>, 방어력 107. NG+ 이후는 위키 표.</td></tr>
            <tr><th>면역</th><td>독·부패·출혈·동상·수면·광기 면역.</td></tr>
            <tr><th>약점</th><td>위키 <em>Negation</em>: 표준·베기·타격·관통 각 10, 마법·화염·신성 40, <strong>벼락 0</strong> → 번개 속성이 상대적으로 유리. 태세 80·패리 가능·치명타는 짧은 경직. HP 50% 이후 페이즈·로레타의 대궁 등은 위키 공략. 할리그의 <em>Loretta, Knight of the Haligtree</em>는 별개 보스.</td></tr>
    """,
    "Elemer of the Briar": """
            <tr><th>개요</th><td>가시(브라이어)와 저주를 연상시키는 장비의 기사. 흔히 <em>Bell Bearing Hunter</em>와 연계된 미니보스로 소개된다.</td></tr>
            <tr><th>위치</th><td>샤브리리 포도주, 도구 상자 등 퀘스트·야간 이벤트 — 위키 원문 확인.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터별 상이.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation이 낮은 속성·유형.</td></tr>
    """,
    "Dragonlord Placidusax": """
            <tr><th>개요</th><td>전설 보스. 과거의 용왕으로, Farum Azula 시대의 잔재로 등장한다. 다단 점프·벼락·소각 브레스 등 광역 패턴이 많다.</td></tr>
            <tr><th>위치</th><td>크룸블링 패름 아즈라 — <strong>Beside the Great Bridge</strong> 근처에서 아래로 내려가 도달하는 은밀 보스.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 보스 표 참고(다페이즈).</td></tr>
            <tr><th>면역</th><td>용족 보스 공통 저항·면역은 위키.</td></tr>
            <tr><th>약점</th><td>물리·속성 흡수율은 위키 Negation 표. 아래는 공격 데이터 발췌.</td></tr>
    """,
    "Commander": """
            <tr><th>개요</th><td>정식 명칭 <strong>Commander Niall</strong>. 거인 설원 <strong>Castle Sol</strong>의 노장으로, 개장의 발과 뇌전을 섞은 공격을 쓴다. 전투 초반 <strong>추방 기사 영혼</strong> 둘을 소환한다. 선택 보스이나 <strong>성스러운 적설지</strong> 진입 전 격파가 필요하다.</td></tr>
            <tr><th>위치</th><td>Mountaintops of the Giants — Castle Sol 동편 상층 안개 문. 가장 가까운 은혜: <strong>Church of the Eclipse</strong>. (지도 링크는 본문 인터랙티브 맵 참고.)</td></tr>
            <tr><th>체력 (NG)</th><td>니얼 본체·소환 기사 각각 위키 표 참고.</td></tr>
            <tr><th>면역</th><td>광기 면역 등 — 위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 <em>Negation</em>: 베기 35 등 유형별 상이. 얼음·번개 혼합 패턴 대응은 공략 참고. <em>Commander O'Neil</em>과는 소환·속성이 다르다.</td></tr>
    """,
    "Tree Sentinel": """
            <tr><th>개요</th><td>황금수 아래를 순찰하는 기사. 말 탄 필드 보스로 대형 할버드·방패·신성 광역이 특징.</td></tr>
            <tr><th>위치</th><td>리무그레이브 등 초반 필드 및 후반 변종(말레니아 문 앞 등) 여러 곳.</td></tr>
            <tr><th>체력 (NG)</th><td>배치별 상이.</td></tr>
            <tr><th>면역</th><td>위키 해당 인카운터 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation이 낮은 속성·유형.</td></tr>
    """,
    "Ancestor Spirit": """
            <tr><th>개요</th><td>영혼의 들판에서 맞이하는 거대 영혼체. 유연한 몸놀림과 마법 같은 광역이 특징.</td></tr>
            <tr><th>위치</th><td>소프라 강 지역 <strong>Siofra River</strong> — 횃불 이벤트 후 보스 전장.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 보스 표.</td></tr>
            <tr><th>면역</th><td>위키 면역·저항.</td></tr>
            <tr><th>약점</th><td>위키 Negation.</td></tr>
    """,
    "Godskin Apostle": """
            <tr><th>개요</th><td>신의 살갗과 연관된 사도. 흑염·연장·공중 패턴이 강한 미니보스·필드 보스.</td></tr>
            <tr><th>위치</th><td>바람 절벽, 봉마 소, 신의 피부 사도 교회 등 여러 곳.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터별 상이.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation이 낮은 속성.</td></tr>
    """,
    "Ancient Dragon": """
            <tr><th>개요</th><td>고대 용 필드 보스. 브레스·발톱·꼬리 등 대형 판정이 많다.</td></tr>
            <tr><th>위치</th><td>크룸블링 패름 아즈ula 등 — 위키 <em>Ancient Dragon</em> 해당 항목.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>용족에 맞는 상태 저항·면역.</td></tr>
            <tr><th>약점</th><td>머리·발 등 부위·속성 약점은 위키 Negation·공략.</td></tr>
    """,
    "Morgott": """
            <tr><th>개요</th><td>왕도 레이든델의 필수 보스 <strong>Morgott, the Omen King</strong> 및 초반 필드 <strong>Margit, the Fell Omen</strong> 등 동일 계열. 지팡이·성검 소환·꼬리 등 오멘 패턴.</td></tr>
            <tr><th>위치</th><td>스톰빌 성(멀기트), 레이든델(모르고트) 등 스토리 진행에 따라 다름.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터별 상이 — 위키 각 보스 섹션.</td></tr>
            <tr><th>면역</th><td>상태 이상 면역·저항은 위키.</td></tr>
            <tr><th>약점</th><td>위키 Negation. 아래 atkparam 은 데이터 구간 하나를 발췌한 것이다.</td></tr>
    """,
    "Godrick the Grafted": """
            <tr><th>개요</th><td>스톰빌 성의 주인인 샤드베어러. 접목된 다수 팔·바람·내려찍기 등 2페이즈 전투.</td></tr>
            <tr><th>위치</th><td>Stormveil Castle — 깊은 안개 문 너머. 은혜: <strong>Limgrave Tower Bridge</strong> 쪽 루트.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 보스 표.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation/Resistance 표에서 유리한 속성·유형.</td></tr>
    """,
    "Red Wolf of Radagon": """
            <tr><th>개요</th><td>라다곤과 연관된 붉은 늑대. 휘석 검·늑대 소환 등 마법 견제가 특징.</td></tr>
            <tr><th>위치</th><td>라이 카리아 마법학원 — <strong>Debate Parlor</strong> 이후 안개 문.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>위키 면역·저항.</td></tr>
            <tr><th>약점</th><td>위키 Negation.</td></tr>
    """,
    "Starscourge Radahn": """
            <tr><th>개요</th><td>레드마네 성에서 열리는 축제의 주인공. 중력·궁·쌍도 등 광역 필드 보스.</td></tr>
            <tr><th>위치</th><td>Caelid — Redmane Castle. NPC 소환·재도전 규칙은 위키.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 다페이즈 표.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation·머리·승마전 등 공략.</td></tr>
    """,
    "Fire Giant": """
            <tr><th>개요</th><td>거인족의 최후. 화염 냄비·발밟기·눈사태 등 대형 패턴.</td></tr>
            <tr><th>위치</th><td>Mountaintops — 화염 거인 봉화 이후 필드.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표(다페이즈/약점 발 등).</td></tr>
            <tr><th>면역</th><td>위키 상태 저항.</td></tr>
            <tr><th>약점</th><td>발·눈 등 부위·속성은 위키 Negation.</td></tr>
    """,
    "Beast Clergyman": """
            <tr><th>개요</th><td>1페이즈는 <strong>Beast Clergyman</strong>, HP 일정 이하에서 <strong>Maliketh, the Black Blade</strong>로 전환되는 필수 보스.</td></tr>
            <tr><th>위치</th><td>Crumbling Farum Azula — <strong>Beside the Great Bridge</strong> 근처.</td></tr>
            <tr><th>체력 (NG)</th><td>1페이즈·2페이즈 각각 위키 표.</td></tr>
            <tr><th>면역</th><td>수면·광기·죽음 면역 등 — 위키 Resistance(페이즈별).</td></tr>
            <tr><th>약점</th><td>위키 Absorption/Negation(페이즈별). 신성 모독 발톱 등은 위키 공략.</td></tr>
    """,
    "Hoarah Loux": """
            <tr><th>개요</th><td>초대 엘든 왕 고프리의 본모. 1페이즈 왕 모습, 2페이즈 전사 호라 루.</td></tr>
            <tr><th>위치</th><td>Leyndell — 최종 전장(스토리 후반).</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation·태세·잡기 대응.</td></tr>
    """,
    "Radagon": """
            <tr><th>개요</th><td>황금률의 반쪽. 망치·성역·번개 등 광역 공격. 이어서 엘든 비스트 전투로 이어진다.</td></tr>
            <tr><th>위치</th><td>Erdtree 최종 구역.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>위키 면역·저항.</td></tr>
            <tr><th>약점</th><td>위키 Negation.</td></tr>
    """,
    "Mohg": """
            <tr><th>개요</th><td>피의 왕조. 혈염·날개·지하 몽그윈 왕조로의 문 등 패턴.</td></tr>
            <tr><th>위치</th><td>Mohgwyn Dynasty — 지하 영역.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>위키 Resistance.</td></tr>
            <tr><th>약점</th><td>위키 Negation·출혈 대응.</td></tr>
    """,
    "Malenia": """
            <tr><th>개요</th><td>미켈라의 칼날. 물개와 검무·개화 등 2페이즈. 출혈·흡혈이 위협적이다.</td></tr>
            <tr><th>위치</th><td>Miquella's Haligtree 최심부.</td></tr>
            <tr><th>체력 (NG)</th><td>위키 표.</td></tr>
            <tr><th>면역</th><td>위키 면역(개화 등 패턴 제외 일부 상태).</td></tr>
            <tr><th>약점</th><td>위키 Negation·동상 등 공략.</td></tr>
    """,
}

# 「스킬」 표 tbody — 레날라의 summary_rows 와 같이 수동 요약. 키가 없으면 generic_summary 사용.
BOSS_SKILL_SUMMARY_HTML: dict[str, str] = {
    "Azula Beastman": """
      <tr><td>근접·대검 계열</td><td>베기·내려찍기·연속 타격. 판정마다 atkparam 행이 나뉜다.</td></tr>
      <tr><td>점프·돌진</td><td>거리·히트박스가 다른 변형이 여러 행으로 잡힌다.</td></tr>
      <tr><td>발사체·원거리</td><td>이름에 발사체(데이터 표기 Bullet)가 붙은 행은 별도 판정일 수 있다.</td></tr>
    """,
    "Burial Watchdog": """
      <tr><td>대검·지팡이 변종</td><td>무기별 패턴이 다르고 동일 동작도 행이 쪼개질 수 있다.</td></tr>
      <tr><td>숨결·원소</td><td>화염 등 원소 숨결 변형은 위키·인카운터별로 상이.</td></tr>
      <tr><td>소형 Lesser</td><td>일반 적 분류는 본 표 구간과 다를 수 있다.</td></tr>
    """,
    "Crystalian": """
      <tr><td>창·낫 등 무기형</td><td>동일 던전에서 무기·행동 세트가 갈린다.</td></tr>
      <tr><td>외피 전·후</td><td>크리스탈 깨짐 전후로 체감·판정이 달라질 수 있다.</td></tr>
      <tr><td>듀오 전투</td><td>두 마리 동시 배치 시 행이 겹쳐 보일 수 있다.</td></tr>
    """,
    "Crucible Knight": """
      <tr><td>실드·대검 등 무기형</td><td>가드·찌르기·도가니 꼬리 등 패밀리 공통 패턴.</td></tr>
      <tr><td>용의 일격</td><td>꼬리·날개 연출 행이 atkparam 에 따로 잡힌다.</td></tr>
      <tr><td>변형·발사체</td><td>같은 보스명이라도 던전별로 행 구성이 다르다.</td></tr>
    """,
    "Leonine Misbegotten": """
      <tr><td>연속 베기·찍기</td><td>빠른 템포로 동작 변형 행이 많다.</td></tr>
      <tr><td>점프·낙하</td><td>판정 크기가 다른 변형이 나뉜다.</td></tr>
      <tr><td>잡기·특수</td><td>speffect·판정 ID 차이로 행이 분리될 수 있다.</td></tr>
    """,
    "Royal Rider": """
      <tr><td>할버드 근접</td><td>말 탄 채 베기·찌르기·내려찍기.</td></tr>
      <tr><td>휘석 마법</td><td>글린트블레이드·대궁 등 원거리. 발사체(Bullet) 행과 본체 행을 구분한다.</td></tr>
      <tr><td>페이즈 전환</td><td>HP 구간에 따라 패턴 추가 — 위키·공략과 대조.</td></tr>
    """,
    "Elemer of the Briar": """
      <tr><td>대검·가시 패턴</td><td>벨 베어링 헌터 계열과 유사한 연장 공격.</td></tr>
      <tr><td>돌진·광역</td><td>거리·판정이 다른 변형 행이 다수.</td></tr>
      <tr><td>인카운터별</td><td>야간 이벤트·위치에 따라 체력·행동이 다를 수 있다.</td></tr>
    """,
    "Dragonlord Placidusax": """
      <tr><td>브레스·번개</td><td>광역 속성 패턴. 단계·위치별로 행이 나뉜다.</td></tr>
      <tr><td>몸통·발톱·꼬리</td><td>부위·판정마다 별도 atkparam 행.</td></tr>
      <tr><td>다페이즈</td><td>페이즈마다 사용 행 집합이 바뀐다 — 위키 보스 페이지 참고.</td></tr>
    """,
    "Commander": """
      <tr><td>뇌장·얼음 계열</td><td>개장의 발 등 근접·속성 혼합.</td></tr>
      <tr><td>소환 기사</td><td>본체와 별개 NPC 판정 행이 섞일 수 있다.</td></tr>
      <tr><td>범위 광역</td><td>돌진·제압류는 히트박스별로 행이 쪼개진다.</td></tr>
    """,
    "Tree Sentinel": """
      <tr><td>할버드·방패</td><td>말 탄 필드 보스 공통 근접 패턴.</td></tr>
      <tr><td>신성·도탄</td><td>원거리·광역 신성 계열 — 발사체(Bullet) 행 확인.</td></tr>
      <tr><td>변종</td><td>초반·말레니아 문 앞 등 배치별로 스킬 구성이 다르다.</td></tr>
    """,
    "Ancestor Spirit": """
      <tr><td>점프·돌진</td><td>유연한 체형으로 궤적이 다른 행이 많다.</td></tr>
      <tr><td>마법형 광역</td><td>영혼체 연출에 맞는 판정이 별도 행으로 잡힌다.</td></tr>
      <tr><td>횃불 이벤트</td><td>전투 전 이벤트는 본 atkparam 구간과 무관할 수 있다.</td></tr>
    """,
    "Godskin Apostle": """
      <tr><td>흑염·연장</td><td>사도 공통 근접·속성 패턴.</td></tr>
      <tr><td>공중·회전</td><td>판정이 큰 기술은 행이 세분화된다.</td></tr>
      <tr><td>필드·던전</td><td>동일 이름·다른 맵 배치 시 행 수가 다를 수 있다.</td></tr>
    """,
    "Ancient Dragon": """
      <tr><td>브레스·입격</td><td>용족 필드 보스 공통 광역 패턴.</td></tr>
      <tr><td>발톱·꼬리</td><td>부위별 판정 행 분리.</td></tr>
      <tr><td>착지·이동</td><td>이동 중·착지 순간 히트가 별도 행일 수 있다.</td></tr>
    """,
    "Morgott": """
      <tr><td>멀기트(필드) 패턴</td><td>지팡이·성검 소환·꼬리 등 초반 보스 행.</td></tr>
      <tr><td>모르고트(왕도)</td><td>동일 CSV 키 구간 안에서 스토리 보스 패턴이 섞일 수 있다.</td></tr>
      <tr><td>오멘 계열</td><td>연장·발사체(Bullet) 변형은 위키 스킬명과 1:1이 아닐 수 있다.</td></tr>
    """,
    "Godrick the Grafted": """
      <tr><td>1페이즈</td><td>도끼·바람·내려찍기 등 접목 팔 패턴.</td></tr>
      <tr><td>2페이즈</td><td>용의 두 머리·광역 등 추가 패턴.</td></tr>
      <tr><td>잡기·특효</td><td>별도 speffect 행이 분리될 수 있다.</td></tr>
    """,
    "Red Wolf of Radagon": """
      <tr><td>휘석 검·물기</td><td>마법 견제 중심 원거리·근접.</td></tr>
      <tr><td>늑대 소환</td><td>소환물 판정이 본체와 다른 행일 수 있다.</td></tr>
      <tr><td>학원 보스</td><td>Debate Parlor 이후 단일 전투 구성.</td></tr>
    """,
    "Starscourge Radahn": """
      <tr><td>중력·궁·쌍도</td><td>필드 보스 광역 패턴. 거리·페이즈에 따라 행 집합이 달라진다.</td></tr>
      <tr><td>승마전</td><td>NPC 소환·재도전 규칙은 위키 — 데이터 행과 전투 단계를 대조.</td></tr>
      <tr><td>탄환·발사체</td><td>궁·중력탄 등 원거리는 발사체(Bullet) 접두 행이 많다.</td></tr>
    """,
    "Fire Giant": """
      <tr><td>화염 냄비·발밟기</td><td>대형 타겟·광역 위주.</td></tr>
      <tr><td>눈사태·구르기</td><td>2페이즈·약점 발 연출과 연계된 행 분리.</td></tr>
      <tr><td>다페이즈</td><td>위키 보스 표와 페이즈별 HP·패턴을 맞춰 본다.</td></tr>
    """,
    "Beast Clergyman": """
      <tr><td>1페이즈 야수 사제</td><td>수인 근접·연장. 말리케스 전 패턴.</td></tr>
      <tr><td>2페이즈 말리케스</td><td>흑검·신성 모독 등 — 위키 페이즈별 스킬명과 대조.</td></tr>
      <tr><td>데이터 구간</td><td>동일 키 구간에 두 페이즈 행이 함께 포함될 수 있다.</td></tr>
    """,
    "Hoarah Loux": """
      <tr><td>1페이즈 고프리</td><td>도끼·잡기·태세 붕괴 등 왕 패턴.</td></tr>
      <tr><td>2페이즈 호라 루</td><td>맨손·내전·체포 등 전사 패턴.</td></tr>
      <tr><td>페이즈 전환</td><td>컷신 후 행 집합이 바뀐다 — 위키와 대조.</td></tr>
    """,
    "Radagon": """
      <tr><td>망치·성역</td><td>황금률 기반 근접·광역. 벼락 속성 혼합.</td></tr>
      <tr><td>광역 판정</td><td>동일 스킬이라도 히트마다 행이 나뉠 수 있다.</td></tr>
      <tr><td>엘든 비스트 연계</td><td>격파 후 다음 보스는 별도 구간·문서.</td></tr>
    """,
    "Mohg": """
      <tr><td>혈염·창</td><td>피의 왕조 패턴. 출혈·혈연 연출.</td></tr>
      <tr><td>날개·비행</td><td>공중·광역 행이 별도 판정으로 잡힌다.</td></tr>
      <tr><td>왕조로의 문</td><td>특수 페이즈·컷신 연계는 위키 공략 참고.</td></tr>
    """,
    "Malenia": """
      <tr><td>1페이즈 검무</td><td>물개·연속 베기·돌진. 출혈·흡혈 주의.</td></tr>
      <tr><td>2페이즈 개화</td><td>범위·속도 변화 — 위키 페이즈별 스킬.</td></tr>
      <tr><td>물개·연장</td><td>동일 연출도 히트마다 atkparam 행이 분리된다.</td></tr>
    """,
}


def overview_for_key(key: str, start: int, end: int) -> str:
    """개요 표 HTML. 키별 정의가 없으면 짧은 기본 안내만."""
    body = BOSS_OVERVIEW_HTML.get(key)
    if body:
        return body
    return f"""
            <tr><th>개요</th><td>이 페이지는 atkparam_npc CSV <strong>{start}–{end}</strong>행을 한 구간으로 묶은 자동 문서입니다. 스토리·전투·맵은 Fextralife 위키 원문을 우선합니다.</td></tr>
            <tr><th>위치</th><td>위키에서 해당 보스·던전 페이지를 검색하십시오.</td></tr>
            <tr><th>체력 (NG)</th><td>인카운터·패치에 따라 다릅니다.</td></tr>
            <tr><th>면역</th><td>상태 이상 면역·저항은 위키 <em>Resistance</em> 표를 본다.</td></tr>
            <tr><th>약점</th><td>받는 피해는 위키 <em>Negation</em>이 낮은 속성·물리 유형이 유리하다. 아래 표는 <strong>공격</strong> 파라미터만 반영한다.</td></tr>
    """
