# 보스 페르소나 HTML 파이프라인

`atkparam_npc.csv`를 구간으로 잘라 **레날라 문서와 같은 레이아웃**의 보스별 HTML·그래프를 만드는 절차를 정리한다. 샘플 두 보스(반달의 블레이드, 흑도 가신)는 수동 요약이 들어가고, 나머지는 `build_all_boss_docs.py`로 일괄 생성한다.

## 데이터 소스

- **CSV**: 프로젝트 루트의 `atkparam_npc.csv` (헤더 1행, 데이터는 2행부터 1-based 행 번호로 지칭).
- **열**: `build_rennala_doc.py`의 `DATA_COLS`·`DATA_COLS_KO`·`rowid`·`rowname`을 쓴다. 공격별 표·해설의 첫 열(공격 이름)은 **보스명이 아니라 `rowid`만** 표시한다.

## 구간(보스) 잡는 규칙

1. `rowname` 문자열 안의 **`[ ... ]` 대괄호 안 텍스트**를 **보스(적) 키**로 본다. 정규식: `\[([^\]]+)\]`.
2. **빈 `rowname`**(또는 대괄호 패턴이 없는 행)은 **직전에 열린 키의 구간을 끝 행만 연장**한다. 즉 같은 보스 블록 안의 연속 행으로 취급한다.
3. 키에 **`Rennala`가 포함**되면 그 구간은 **자동 보스 문서에서 제외**한다. 레날라는 `build_rennala_doc.py`로 따로 수동 정밀 문서를 만들기 때문이다.
4. 행 수가 **4행 미만**인 구간은 노이즈로 보고 버린다(`min_rows=4`).

구간이 정해지면 `build_test_boss_docs.load_slice(start, end)`로 해당 1-based 행 범위를 읽어 각 행에 `label_chart` / `label_table` = `rowid`를 넣는다.

## HTML·스타일·용어

- **공통 레이아웃·CSS·사이드바**: `build_rennala_doc.py`의 `LAYOUT_CSS`, `render_sidebar`, `esc`, 표 헤더 한글 등을 **임포트해 재사용**한다.
- **보스 페이지 본문**: `build_test_boss_docs.write_boss_html(...)`이 생성한다. 상단은 위키 요약 형태의 `boss-overview` 표, 이어서 인터랙티브 맵 링크, 스킬 표, 그래프 두 장, 공격별 수치·해설 표이다.
- **스킬 표 vs atkparam 행 수**: `SKILL_NOTE_HTML`에 적힌 대로, 스킬은 위키·전투 기준 **손 요약**이고 공격별 표는 **판정마다 한 줄**이라 행이 많다는 점을 고정 안내한다.

## 그래프

- `build_test_boss_docs.charts_for` → `_save_mag_chart`, `_save_mix_chart`.
- **마법 계수(`atkmag`)가 전부 0**이어도 마법 그래프 자리에 **안내용 PNG**를 쓴다(안내 문구는 PNG 안에만; figure 밖 중복 문단은 넣지 않음). PNG 높이는 짧은 안내 전용으로 **낮게** 잡는다.
- Y축 라벨은 **`rowid`만** 사용하고, 막대/행 간격은 `row_h=0.4` 등으로 넓혀 가독성을 맞춘다.

## 초상(Fandom)

- Fandom `api.php`의 **`pageimages`**로 썸네일 URL을 가져온다. UA는 짧으면 403이 나는 경우가 있어 **브라우저에 가까운 User-Agent**를 쓴다.
- 저장 파일명은 URL에 `.jp`가 들어가면 **`.jpg`**, webp면 `.webp`, 그 외 `.png`로 구분한다(Wikia 경로 중간에 `.jpeg`가 끼는 경우를 고려).

## 네비게이션

- **레날라**는 항상 첫 항목: `("rennala_294-318.html", "레날라")`.
- 전체 보스 배치 후 **`ListUrl/boss_nav_extra.json`**에 `(href, 표시이름)` 배열을 쓴다(레날라 제외).
- `build_rennala_doc.py`는 기동 시 `boss_nav_extra.json`을 읽어 **`NAV_PAGES = [레날라] + extra`**로 병합한다.
- 각 보스 HTML 생성 시 `write_boss_html(..., nav_pages=full_nav)`로 **동일한 전체 목록**을 넘겨, 어느 페이지를 열어도 사이드바가 일치하게 한다.

## 파일명·특수 보스

- 일반 보스: `npc_{시작행}_{끝행}_{영문슬러그}.html` (슬러그는 키에서 ASCII만 남긴 것, 길이 제한).
- **반달 / 흑도**만 기존 샘플과 동일한 stem을 쓰도록 `build_all_boss_docs.py`의 `BOSS_DOC_SPECIAL`에 **stem·한글 제목·위키·맵·개요·스킬 요약·추가 초상 URL**을 넣어 둔다.

## 실행 순서

1. **전체 보스 재생성**(네비 JSON 포함, 마지막에 레날라 재빌드):
   - `python build_all_boss_docs.py`
2. **레날라만**(용어집·그래프·레날라 HTML; `boss_nav_extra.json`이 있으면 사이드바에 전 보스 반영):
   - `python build_rennala_doc.py`
3. **샘플 두 보스만** 손으로 다듬은 내용으로 다시 쓰기:
   - `python build_test_boss_docs.py`  
   - 이때 사이드바는 스크립트 안의 `NAV_SAMPLE_BOSSES`(레날라+반달+흑도)로 **고정**된다. 전체 목록과 맞추려면 이후 1번을 다시 돌리면 된다.

## 참고 문서

- 레날라 작업 맥락: `Main.md`
- CSV·열 의미는 게임 덤프 기준이며, 위치·드롭 등 **플레이 정보는 Fextralife 위키**와 대조하는 것이 전제다.
