# Main — 레날라 문서 작업 맥락

이 파일은 **같은 프로젝트를 이어서 작업할 때** 사용자 선호·누적 요청·현재 구현 상태를 빠르게 맞추기 위한 메모입니다.  
핵심 빌드 스크립트: `build_rennala_doc.py` → 산출물은 **`ListUrl/`** (루트 리다이렉트 HTML 없음).

---

## 1. 문서 목적·범위

- **대상 데이터**: `atkparam_npc.csv`의 **294~318행** (레날라 구간).
- **출력 형식**: **HTML 중심**, 한글 위주. MD는 보조·맥락용으로만 사용해도 됨.
- **저장 위치**: `ListUrl/rennala_294-318.html` 및 동폴더 차트·용어집.
- **파일명 규칙**: 본문 `rennala_294-318.*`, 용어집 **`glossary_WIKI.html`** (디스크 파일명은 영어, 페이지 안 표기는 「용어집 WIKI」 유지).

---

## 2. 누적 요청과 반영 결과

### 2.1 데이터·빌드

| 요청 | 결과 |
|------|------|
| CSV 없을 때도 문서가 최신 템플릿처럼 보이게 | `atkparam_npc.csv`가 없으면 **내장 스냅샷**(`_SNAPSHOT_INT`)으로 동일 구간 수치 생성. 있으면 CSV 우선. |
| 루트 `rennala_294-318.html` 리다이렉트 | **작성하지 않음**. 기존 루트 파일은 빌드 시 삭제 시도. |
| 구 용어집 파일 정리 | `ListUrl/용어집 WIKI.html`, `rennala_294-318_glossary.html`, 구 `spell_moon` 이미지 등 정리. |

### 2.2 본문·표현

| 요청 | 결과 |
|------|------|
| MD → HTML, ListUrl, `rennala_294-318` 파일명 | 준수. |
| 한글 위주, 용어집 분리 | `glossary_WIKI.html` 링크. |
| 보스 위키 요약·그래프 | Fextralife 보스 문서 링크 + 요약 문단(후에 **표 형태**로 정리). |
| 공격 라벨 `[1]`/`[2]`, 그래프용 짧은 라벨 | `LABEL_CHART` / `LABEL_TABLE` 분리. |
| 해설에서 페이즈 접두 반복 제거 | `NOTE_TEXTS` 등 한 줄 요약 톤. |
| 스킬 구간 표현 | 「스킬」 표, 1·2페이즈 설명 한 줄 위주. |
| 공격별 수치: 공격 이름 **한 줄** | `label_table_oneline()` (`\n` → `·`). |
| 공격별 수치: 행 이름 **호버 툴팁** | `<th title="...">` + `NOTE_TEXTS`와 동일 설명. |
| 용어집 링크 위치 | 문서 최상단이 아니라 **「공격별 수치」 제목 옆**. |
| 위키 링크 vs 이미지 불일치 (달 아이콘 vs 사람) | **위키아 `Queen_Rennala.webp`** 보스 일러스트로 다운로드 (`rennala_294-318_boss_wiki.webp`). |
| 위키 출처 문구 간소화 | 이미지/인물 설명 문장 제거 → **「Fextralife 위키 원문을 바탕으로 번역·요약」**만 유지. |
| 상단 개요(보스) **표(칸)** 구성 | 보스 블록 본문을 **항목/내용 2열 표**(`table.boss-overview`)로 구성. |
| 통합 피해 계수 그래프 | 제목 **물리·마법·화염·벼락·스태미나 피해 계수**, `set_xlabel` **「계수」**. 가로 막대 5종(`_save_combined_atkcoef_chart`). |
| 본문 순서 | **스킬** 표 다음 **공격별 수치** 표, 그 아래 **그래프** 섹션(`build_test_boss_docs.write_boss_html`, `build_rennala_doc.main`). |

### 2.3 표에서 제외한 열 (용어집에서도 제거)

| 제거 항목 | 비고 |
|-----------|------|
| `tracesfxid0` (추적 이펙트 식별 번호) | `DATA_COLS` / 한글 헤더 / 스냅샷 / 용어집 행 삭제. |
| `speffectid0` (첫 특수 효과 식별 번호) | 동일하게 전부 삭제. |
| 표에서 추가 제거(2026-04-17) | `atkobj`, `subcategory1`, `subcategory2`, `atkbehaviorid`, `maphittype`, `friendlytarget`, `spattribute`, `atkattribute`, **`isarrowatk`(화살 공격)** — 용어집 동일. `hit0_radius`~`hit3_radius`는 표에 **`hit_radius_slash`** 한 열(예: `0/0/0/0`)로만 표시. 큐레이션 보스 `npc_*.html`은 **`python build_all_boss_docs.py`** 로 갱신. |
| 피해 계수(표) | **물리·마법·화염·벼락·스태미나 피해 계수** 다섯 열(`atkphys`~`atkstam`). 그래프 막대·`DMG_COEF_KEYS`·행 필터와 동일 순서. |
| 표·용어집 제거(2026-04-16) | **`atktype`**(공격 분류 코드), **`hitstoptime`**(히트 스톱 시간) — `DATA_COLS`·`DATA_COLS_KO`·`_LEGACY_SNAPSHOT_COLS`·`_SNAPSHOT_INT`·`write_glossary()`에서 제외. |

### 2.4 수치·Wiki 보강 예정 (열 단위 할 일)

아래 열은 **공격별 수치 표**·**용어집 WIKI**·**보스 위키 요약(본문)**에서 설명을 더 쌓을 대상이다.  
구현 시 `build_rennala_doc.py`의 `write_glossary()`, 필요하면 `NOTE_TEXTS`·개요 표 주석·외부 링크를 함께 갱신한다.

| 사용자 표기 | `DATA_COLS` / 표 헤더 | 할 일(수치 + Wiki) |
|---------------|----------------------|---------------------|
| (참고) 히트 반경 | `hit_radius_slash` → 히트0~3 구 반경 | 표에는 `히트0/히트1/히트2/히트3` 값을 한 칸에 슬래시로 표기. 용어집 문단과 수치 해설 톤을 맞출 것. |

---

## 3. 기술 메모

- **폰트**: matplotlib `Malgun Gothic`, `axes.unicode_minus = False`.
- **콘솔 한글**: `sys.stdout.reconfigure(encoding="utf-8")` 시도.
- **외부 이미지 URL**: 보스 일러스트는 Fandom API로 검증된 `Queen_Rennala.webp` 경로 사용.
- **CSV 로드**: `DATA_COLS`에 없는 컬럼은 읽지 않음 (`tracesfxid0`, `speffectid0` 등).

---

## 4. 다음 작업 시 권장 체크리스트

1. `python build_rennala_doc.py` 실행 후 `ListUrl/rennala_294-318.html`·`glossary_WIKI.html`·PNG/WebP 갱신 확인.  
2. CSV가 생기면 스냅샷 대신 **실제 `rowname`**이 들어가는지 확인.  
3. 표 열을 또 줄이거나 용어를 바꿀 때는 **`DATA_COLS` / `DATA_COLS_KO` / `HIT_RADIUS_KEYS`·`hit_radius_slash` / `DMG_COEF_KEYS` / `_SNAPSHOT_INT` / `write_glossary()`**·`build_test_boss_docs.load_slice`·`_save_combined_atkcoef_chart` 를 함께 수정할 것.  
4. **2.4절** 열 보강을 진행할 때는 같은 열의 **용어집 문단**과 **위키 요약 문장**을 한 번에 맞출 것.

---

## 5. 사용자 선호 (대화 규칙)

- 응답은 **한국어** 선호.
- 코드는 **요청 범위만** 최소 수정; 불필요한 리팩터·무관 파일 변경 지양.

---

*마지막 정리: 2026-04-17 기준 `build_rennala_doc.py`·2.4절 수치·Wiki 할 일 목록.*
