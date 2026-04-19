# 보스 역기획 데이터 파이프라인 — 단계별 우선순위 (B형 요약)

**부제:** 구현·문서 공통 명세 초안  
**한 줄 스코프:** Elden Ring 보스 1체를 기준으로 Param·TAE·웹 산출물까지 **재현 가능한 JSON/표**를 만든 뒤, AI·고급 시각화는 단계적으로 확장한다.

**웹에서 보기 (Document.md 4절 스타일):** 저장소 `web/combat_doc/reverse_design_phases.html` — GitHub Pages 배포 시  
[https://ryanlee84.github.io/EldenRing_ReverseDesign/combat-doc/reverse_design_phases.html](https://ryanlee84.github.io/EldenRing_ReverseDesign/combat-doc/reverse_design_phases.html)  
로컬: `web/combat_doc` 폴더에서 `python -m http.server` 후 같은 파일명으로 접속.

**규격 정렬:** `Document.md` **B형(프로토타이핑 명세서)** — 표지·요약 대시보드·시스템 번호·강조 블록·의도적 생략. 웹 표현은 **문서 4절(웹 UI)** 의 단계 배지·칩·아코디언·링크 행·요약 박스 패턴에 맞춘 정적 HTML로 제공한다.

---

## 요약 대시보드

| 항목 | 값 |
|------|-----|
| 명세 시스템 수(본 문서) | **4** (Param / TAE / 웹·배포 / 확장) |
| 기준 레퍼런스 | `Document.md`, `guide.md`, `data/tree_sentinel_tae.example.json` |
| 기준 엔진·데이터 | Elden Ring regulation / Smithbox·Param CSV·TAE JSON 덤프 |

**파라미터 타입 범례 (B형 2절 및 문서 3절 표 (4)와 동일 분류)**

| 타입 | 의미 | 예시 필드 |
|------|------|-----------|
| `frame` | 애니·TAE 기준 프레임 구간 | `frameStart`, `frameEnd` |
| `value` | 실수·정수 스칼라 | `atkphys`, 파생 `%` |
| `bool` | 참/거짓 플래그 | `parryable` (계획) |
| `enum` | 문자열 토큰 | `kind`: `Windup` / `Hit` / `Recovery` / `CancelWindow` |

---

## 시스템 목차 (고정 자릿수)

| ID | 시스템명 | 항목 수(Phase) | 비고 |
|----|----------|----------------|------|
| 01 | Param → JSON | 3 (0~2) | AtkParam 우선, 확장 시 SpEffect·Npc |
| 02 | TAE 스키마 | 3 (0~2) | `schemaVersion` 아래 표 참고 |
| 03 | 웹·정적 산출 | 3 (0~2) | `combat_doc`·`combat_doc_export.py` |
| 04 | AI·Lua·긴장도 | 2 (1~2) | Phase 1부터 칸만 확보 권장 |

---

## Phase 0 — 1보스·수치·형식 고정 (지금 레포와 정합)

| 작업 | 데이터·도구 | 산출·검증 |
|------|----------------|-----------|
| AtkParam 등 Param CSV 필터·슬림 열 | Smithbox / regulation CSV | `combat_doc_export.py` → `data/*_combat.json`, 표·MD |
| 자산 경로·TAE 자리 | `guide.md` (Smithbox·TAE 전제) | `asset_inventory` 상대 힌트, `tae` 키 유무 |
| 웹 미리보기 | 브라우저 + `web/combat_doc` | CSV 업로드, TAE JSON 시 SVG 타임라인(`animations[]`) |
| A형 UI 칸 | 문서 4절 스키마 | `enemy_guide_*` — 단계·카드·링크는 **수동·소량**으로 시작 |

**리스크 / 결정:** `rowid` ↔ TAE 이벤트 연결 규칙은 **chr·게임 빌드마다 검증** 필요. 자동 추정 금지, 수동 매핑 테이블을 Phase 0에 포함.

---

## Phase 1 — 프레임 구간 명명·파생 수치·가독성

| 작업 | 데이터·도구 | 산출·검증 |
|------|----------------|-----------|
| TAE 이벤트를 기획 용어로 정렬 | TAE 덤프 + 수동 라벨 | `kind`를 `Startup` / `Active` / `Recovery` / `Cancel`(가능 시)로 통일한 JSON |
| 파생 열 | Python (표준만으로도 가능, Pandas 선택) | 체력 기준 `%`, 가드·강인도 관련 **전제(`meta.baseline`)** 명시 |
| 시각화 색 규약 | Chart.js / D3 또는 현 SVG 확장 | 회색=Startup, 빨강=Active, 파랑=Recovery, 초록=Cancel — **범례를 JSON에 포함** |
| 패턴·AI | Lua / ESD 등 | **요약 블록만** (트리 전체 파싱은 범위 외로 명시) |

**TAE `schemaVersion` 확장 계획**

| 버전 | 내용 |
|------|------|
| **1** (현재) | `animations[].events[]` — `frameStart`, `frameEnd`, `kind`, `rowid?`, `note?` · `byRowid` 선택 |
| **2** (계획) | 이벤트에 `phase`: `startup` \| `active` \| `recovery` \| `cancel` 정규화 필드 추가(또는 `kind`와 매핑표 병행), `tags[]` (`parryable` 등 `bool`), `meta.animFps`, `meta.baseline` (파생 `%`용) |

구현 시 **`schemaVersion` 읽고 분기** — 웹·export는 하위 호환 유지.

---

## Phase 2 — “손맛” 지표·히트박스·대시보드

| 작업 | 데이터·도구 | 산출·검증 |
|------|----------------|-----------|
| 긴장도·점유율 | TAE + 애니 길이 + Idle 정의 문서화 | 공격 점유 vs 간격 비율 그래프, 정의 한 줄을 그래프 툴팁에 고정 |
| 리스크/리워드 | Recovery vs 다음 공격 Startup 등 | 보스 단면만 자동, 플레이어 액션 길이는 **별도 전제** |
| 히트박스 | Smithbox 캡처·또는 collider 덤프 | 이미지 자산 경로를 JSON에 연결, 본문 옆 배치 |
| 배포·빌드 | GitHub Pages / 선택 Astro·Next | 정적 우선; 인터랙티브 필터는 빌드 도입 시 |

**의도적 생략 (참고사항):** HKX 정밀 판정 기하 전량 재현, 서버 권한 Lua 전량 AST 파싱, 패치별 밸런스 자동 동기화는 본 문서 범위 밖. 필요 시 별도 부록 명세로 분리.

---

## B형 항목 스키마 예시 (스프레드시트·DB 열)

`시스템ID | 시스템명 | 항목ID | 항목명 | 설명 | 파라미터타입 | 기본값/범위 | 비고`

예: `02 | TAE | E-01 | Active 구간 | 히트박스 유효 프레임 | frame | [f0,f1] | rowid 필수`

---

## 초안 체크리스트 (`Document.md` 3절 — 초안 완료 시 체크리스트 항목 대응)

- [ ] 표지 한 줄 스코프(본 문서 상단) 충족  
- [ ] A형 웹 카드로 옮길 때 **동일 필드**를 JSON에 유지 (문서 4절 공통 스키마)  
- [ ] B형: 범례·시스템 ID 자릿수·**생략 범위** 블록 분리  
- [ ] `schemaVersion`·`meta.baseline` 변경 시 **용어집·그래프 범례** 동시 갱신  

---

*보스 역기획 파이프라인 단계표 • Elden Ring / Smithbox·Param • 2026*
