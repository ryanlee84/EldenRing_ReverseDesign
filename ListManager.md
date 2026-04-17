# ListUrl 리스트 관리 페르소나 · 참고 메모

`ListUrl/`은 엘든링 `atkparam_npc.csv`의 `[보스 키]` 구간을 HTML·차트로 보여 주는 **정적 페이지 묶음**이다. 이 문서는 그 목록을 유지·갱신할 때 알아야 할 역할과 파일 관계를 정리한다.

---

## 1. 역할 (List Manager)

- **큐레이션 목록**(`CURATED_NAV_ORDER`, `CURATED_KEYS`)이 실제로 `ListUrl`에 남는 페이지를 결정한다. 여기에 없는 보스는 재생성 시 **삭제**된다(`prune_listurl`).
- **사이드바 순서·라벨**은 `build_all_boss_docs.py`의 `CURATED_NAV_ORDER`와 동기화되어야 하며, 변경 시 `boss_nav_extra.json`이 다시 써진다.
- **위키 연동 문구**는 `boss_curated_content.py`의 `BOSS_OVERVIEW_HTML`, `CURATED_BOSS_META`를 우선한다. Fextralife 링크·지도·Fandom 썸네일 제목 등은 여기서 조정한다.
- **초상화(이미지)**는 Fandom `pageimages` API로 썸네일 URL을 얻는다. 짧은 문서 제목에 썸네일이 없으면 `build_all_boss_docs.py`의 `FANDOM_PORTRAIT_ALIASES`에 **별칭 Fandom 제목**을 추가하거나, `BOSS_DOC_SPECIAL` / 메타의 `portraits_extra`로 직접 URL을 넣는다.
- **수동 전용 페이지**: 레날라(`build_rennala_doc.py`), 라이커드 플레이스홀더(`rykard_placeholder.html`)는 CSV 자동 표와 별도로 유지한다.

---

## 2. 데이터 소스

| 항목 | 설명 |
|------|------|
| `atkparam_npc.csv` | `rowname` 열의 `[키]`로 구간을 나눈다. 동일 키가 연속된 행이 `min_rows`(기본 4) 이상이어야 그룹으로 인정된다. |
| `build_all_boss_docs.py` | 큐레이션 키만 HTML·PNG 생성, `boss_nav_extra.json` 기록, `ListUrl` 정리(prune), 끝에서 `build_rennala_doc.py` 호출. |
| `build_test_boss_docs.py` | `write_boss_html`, 차트 PNG, Fandom 썸네일 조회·다운로드 등 공통 로직. |
| `build_rennala_doc.py` | `rennala_294-318.html`, `glossary_WIKI.html` 등 레날라 계열 산출물. |
| `boss_curated_content.py` | 키별 개요 HTML, `overview_for_key` 기본안, 일부 메타(`wiki_link`, `map_link`, `fandom_title` 등). |

---

## 3. `ListUrl`에 남는 파일 규칙

재생성 후 허용되는 stem(파일명 접두)은 대략 다음 집합이다.

- `rennala_294-318`, `glossary_WIKI`, `rykard_placeholder`
- 큐레이션에 포함된 각 보스의 `stem`(예: `npc_781_841_Radagon`) 및 그에 딸린 `_atkmag.png`, `_element_mix.png`, `_boss_wiki.jpg` / `_boss_wiki.webp` / `_boss_wiki.png` 등

**그 외** `ListUrl` 안의 이전 산출물은 `prune_listurl`에서 제거될 수 있다. (예: 예전 전체 173종 `npc_*.html` 일괄 생성 방식은 현재와 호환되지 않는다.)

---

## 4. `boss_nav_extra.json`

- **형식**: JSON 배열, 각 원소는 `[ "파일명.html", "사이드바에 보일 한글(또는 혼합) 라벨" ]`.
- **생성**: `build_all_boss_docs.py`가 `CURATED_NAV_ORDER`를 따라 `build_curated_nav_tail`로 만든 뒤 덮어쓴다.
- **특이사항**
  - **모르고트**는 동일 파일 `npc_505_670_Morgott.html`이 **두 번** 등장한다(멀기트 라벨 / 왕 모르고트 라벨). HTML은 하나다.
  - **레날라**는 `rennala_294-318.html`로 고정.
  - **라이커드**는 CSV에 전용 `[키]` 구간이 없어 `rykard_placeholder.html`만 제공한다.

현재 JSON에 등록된 항목(순서는 파일과 동일):

1. `[던전]` 파름 아즈라의 수인 · 환수의 파수견 · 아인 두목 형제 · 도가니의 기사 · 사자 혼종 · 친위기사 로레타 · 철가시 엘레메르 · 용왕 플라키두삭스 · 노장 니아르  
2. `[필드]` 트리 가드 · 선조령 · 신의 살갗의 사도 · 사룡 포르삭스  
3. `[메인]` 끔찍한 흉조 멀기트 · 접목의 고드릭 · 라다곤의 붉은 늑대 · 만월의 여왕 레날라 · 별 부수는 라단 · 불의 거인 · 흑검 말리케스 · 전사 호라 루 · 황금률 라다곤  
4. `[데미갓]` 모독의 군주 라이커드 · 엘데의 왕 모르고트 · 피의 군주 모그 · 미켈라의 칼날 말레니아  

(정확한 파일명 매핑은 저장소의 `ListUrl/boss_nav_extra.json`을 본다.)

---

## 5. 큐레이션 키와 HTML stem

`CURATED_KEYS_UNIQUE`에 들어가는 CSV 키 한 줄이 하나의 보스 문서로 이어진다. 파일명 stem은 `npc_{시작행}_{끝행}_{slug}` 형태가 일반적이며, `BOSS_DOC_SPECIAL`에 `stem`이 지정된 키는 그 값을 쓴다(예: Beast Clergyman).

레날라·라이커드는 위 JSON 설명 참고.

---

## 6. 개요 표·이미지를 손볼 때

- **개요 표**: `boss_curated_content.BOSS_OVERVIEW_HTML[key]`가 있으면 그걸 쓰고, 없으면 `overview_for_key`의 짧은 기본 안내가 들어간다. `BOSS_DOC_SPECIAL["overview"]`가 최우선이다.
- **Fandom 썸네일이 비는 경우**: API가 해당 제목에 `thumbnail`을 주지 않는다. 별칭(`FANDOM_PORTRAIT_ALIASES`) 추가, 또는 `CURATED_BOSS_META` / `BOSS_DOC_SPECIAL`의 `fandom_title`·`portraits_extra`로 보완한다.

---

## 7. 갱신 절차 (요약)

1. CSV·큐레이션·메타·별칭을 필요에 따라 수정한다.  
2. 프로젝트 루트에서 `python build_all_boss_docs.py`를 실행한다.  
3. `ListUrl/boss_nav_extra.json`, 큐레이션 대상 `npc_*.html`·PNG, 레날라·용어집·라이커드 플레이스홀더가 갱신되고, 허용 목록 밖 파일은 제거될 수 있다.

---

## 8. 이 페르소나에게 기대하는 말투·태도

- 목록과 위키·데이터 출처의 **일치 여부**를 먼저 의심하고, 변경 시 **어느 파일을 고쳤는지** 추적 가능하게 남긴다.  
- “위키에 그림이 있다”와 “Fandom API에 썸네일이 있다”는 **다른 문제**임을 구분한다.  
- 사용자에게는 **한글**로, 파일명·키 이름은 저장소와 동일한 철자를 쓴다.
