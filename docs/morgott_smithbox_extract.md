# Morgott(c2130) — Smithbox File Browser로 번들만 추출·확인하기

**전제:** Smithbox **2.1.2** + Elden Ring 프로젝트. **Animation Editor(TAE UI)는 ER에서 비활성**이므로, 여기서는 **File Browser**로 파일을 꺼내고 목록만 확보한다.  
배경: `guide.md` 절 “File Browser만으로 anibnd / chrbnd 추출·인벤토리”.

---

## 목표

- `c2130.anibnd.dcx` / `c2130.chrbnd.dcx` 등 **번들이 실제로 참조하는 내부 파일 이름**을 확인한다.
- 필요 시 **추출(Extract)** 해서 로컬 폴더에 두고, **DS Anim Studio** 등으로 `.tae`를 연다.
- 이 저장소 문서용으로는 **`data/morgott_asset_inventory.txt`** 에 한 줄씩 경로를 쌓아 `combat_doc_export.py`의 `--asset-doc-lines`에 넘길 수 있다.

---

## 절차 (Smithbox)

1. **프로젝트 열기** — Elden Ring 데이터가 잡힌 Smithbox 프로젝트를 연다.
2. 상단 **File Browser** 탭으로 전환한다.
3. 왼쪽 트리에서 **`chr`**(또는 동일 역할의 캐릭터 루트)로 이동한다.
4. 목록에서 **`c2130`** 을 검색하거나 스크롤로 찾는다.  
   - 본페 보스: **`c2130.anibnd.dcx`**, **`c2130.chrbnd.dcx`** 가 대표적이다.  
   - 변형(사망 모델 등): **`c2131`** 등 별도 번들이 있을 수 있으니 필요 시 같이 연다.
5. **`c2130.anibnd.dcx`** 를 선택한 뒤, UI에서 **번들 내용(Contents / 내부 파일 트리)** 을 펼친다.
6. 내부에 보이는 **`*.tae`**, **`*.hkx`**(애니), 기타 항목을 메모하거나, **Extract / Export** 메뉴로 지정 폴더에 저장한다.  
   - 정확한 메뉴 이름은 Smithbox 버전에 따른다. 보통 **우클릭 컨텍스트 메뉴** 또는 **상단/측면 툴바의 Extract** 계열이다.
7. 같은 방식으로 **`c2130.chrbnd.dcx`** 를 열어 **FLVER·텍스처 경로** 등을 확인한다. (역기획 문서의 “자산 인벤토리”용)

---

## 추출 후 (로컬 폴더)

1. 추출 루트를 예를 들어 `Smithbox_ER_export/chr/c2130/` 처럼 잡는다.
2. `dir /s /b` (PowerShell: `Get-ChildItem -Recurse -Name`) 등으로 **파일 전체 목록**을 텍스트로 떨군다.
3. 저장소용 상대 힌트만 남기려면 `data/morgott_asset_inventory.txt` 형식으로 정리한다.  
   - 예: `chr/c2130.anibnd.dcx` (게임 트리 기준 표기)  
   - **실제 추출된 `.tae` 파일명**은 번들을 연 뒤에만 확정되므로, 확인 후 한 줄씩 추가한다.

---

## AtkParam 문서와 합치기 (선택)

Morgott 공격 행이 CSV에 있다면:

```text
python tools/combat_doc_export.py --boss-key "[Morgott]" --title "Morgott" ^
  --asset-doc-lines data/morgott_asset_inventory.txt ^
  --out-json data/morgott_combat.json --out-md docs/morgott_combat.md
```

`--boss-key`는 실제 `rowname` 부분 문자열에 맞게 조정한다.

---

## 체크리스트

- [ ] File Browser에서 `c2130.anibnd.dcx` 내부 목록을 캡처 또는 텍스트로 저장했는가  
- [ ] `.tae`를 외부 도구로 열 계획(경로·버전)이 있는가  
- [ ] `data/morgott_asset_inventory.txt`를 실제 목록에 맞게 갱신했는가  

---

*Morgott 자산 추출 가이드 · Smithbox File Browser · 2026*
