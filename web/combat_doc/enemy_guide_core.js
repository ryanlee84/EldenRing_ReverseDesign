/**
 * Enemy Reference Guide — shared data helpers (Document.md §4.5)
 */
(function (global) {
  var STORAGE_KEY = "enemyReferenceGuide_v1";

  function defaultData() {
    return {
      title: "ENEMY REFERENCE GUIDE",
      subtitle: "복잡도 단계별 추천 몬스터 레퍼런스 — 엘든링 기반",
      stages: [
        {
          id: 1,
          titleKo: "기본 패턴형",
          titleEn: "",
          badgeTheme: "green",
          phaseLabel: "프로토타입",
          phaseStyle: "",
          summary: "정직한 텔레그라프, 고정 타이밍, 거리 분기",
          tags: ["액션 페이즈(A-A-R)", "히트박스/허트박스", "기본 AI", "거리 분기"],
          enemies: [
            {
              id: "godrick_soldier",
              nameKo: "고드릭 병사",
              nameEn: "Godrick Soldier",
              priority: "1순위 추천",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Godrick+Soldier" },
                { label: "나무위키", url: "https://namu.wiki/w/고드릭%20병사" },
                { label: "YouTube", url: "https://www.youtube.com/results?search_query=Godrick+Soldier+Elden+Ring" },
              ],
              reason:
                "플레이어와 동일한 무기 조합(한손검+방패). 방어 3종(가드/패링/구르기)을 전부 테스트 가능한 후보. 적도 방패를 들고 있어 가드 브레이크/크리티컬도 테스트 가능.",
              patterns: ["일반 베기 (가드 가능)", "방패 후려치기 (패링 가능)", "내려찍기 강공격 (회피 필요)"],
              coverage: ["가드", "패링", "구르기", "적 가드 브레이크", "거리 분기 AI"],
              summaryBox:
                "플레이어와 체형 동일 → 리그 공유. 방패 있는 적 → 적 측 가드/크리티컬도 검증. 제작비 대비 테스트 커버리지 최고.",
              defaultExpanded: true,
            },
            {
              id: "kaiden",
              nameKo: "카이덴 용병",
              nameEn: "Kaiden Sellsword",
              priority: "",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Kaiden+Mercenary" },
                { label: "나무위키", url: "https://namu.wiki/w/카이덴%20용병" },
                { label: "YouTube", url: "https://www.youtube.com/results?search_query=Kaiden+Sellsword+Elden+Ring" },
              ],
              reason:
                "양손검 공격적 적. 넓은 횡베기로 구르기 타이밍이 다름. 강인도가 높아 약공격 경직 불가 상황 테스트. 고드릭 병사의 보조 역할.",
              patterns: [],
              coverage: ["회피 타이밍", "강인도 차이", "공격적 압박"],
              summaryBox: "방패 없음 → 적 가드 테스트 불가. 대신 강인도 차이 체감 제공.",
              defaultExpanded: false,
            },
            {
              id: "wandering_noble",
              nameKo: "방랑 귀족",
              nameEn: "Wandering Noble",
              priority: "",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Wandering+Noble" },
                { label: "나무위키", url: "https://namu.wiki/w/방랑%20귀족" },
                { label: "YouTube", url: "https://www.youtube.com/results?search_query=Wandering+Noble+Elden+Ring" },
              ],
              reason:
                "1~2패턴의 매우 단순한 적. 2~3체 동시 배치해 다수 적 AI 매니저 테스트용. 단독 선택 비추천.",
              patterns: [],
              coverage: ["다수 적 AI 매니저", "동시 공격 제한"],
              summaryBox: "",
              defaultExpanded: false,
            },
          ],
        },
        {
          id: 2,
          titleKo: "정직한 보스형",
          titleEn: "",
          badgeTheme: "blue",
          phaseLabel: "프로토타입",
          phaseStyle: "",
          summary: "콤보, 높은 강인도, 슈퍼아머, 징벌 윈도우",
          tags: ["1단계 전부", "강인도/슈퍼아머", "콤보 체인 AI", "패링 가능/불가 구분", "크리티컬"],
          enemies: [
            {
              id: "crucible",
              nameKo: "도가니 기사",
              nameEn: "Crucible Knight",
              priority: "1순위 추천",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Crucible+Knight" },
                { label: "나무위키", url: "https://namu.wiki/w/도가니%20기사" },
                { label: "YouTube (노히트)", url: "https://www.youtube.com/results?search_query=Crucible+Knight+no+hit" },
              ],
              reason:
                "프로토타입 미니보스로 이상적. 휴머노이드라 리그 비용 낮음. 패링 가능/불가 공격이 섞여 판단 강제.",
              patterns: ["방패 돌진 (패링 가능)", "종베기 2연속 콤보", "꼬리 휩쓸기", "찌르기", "날개 돌진 (슈퍼아머)"],
              coverage: ["가드", "패링", "구르기", "점프 회피", "강인도", "슈퍼아머", "징벌 윈도우", "크리티컬"],
              summaryBox: "꼬리/날개 단순화 시 비용 절감 가능. 프로토타입 검증 항목 거의 전부 커버.",
              defaultExpanded: true,
            },
            {
              id: "cleanrot",
              nameKo: "부패한 기사",
              nameEn: "Cleanrot Knight",
              priority: "",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Cleanrot+Knight" },
                { label: "나무위키", url: "https://namu.wiki/w/부패한%20기사" },
                { label: "YouTube", url: "https://www.youtube.com/results?search_query=Cleanrot+Knight" },
              ],
              reason: "장창 사용. 사거리가 길어 거리 관리(spacing) 중요. 중거리 찌르기, 밀착 시 패턴 변화.",
              patterns: [],
              coverage: ["거리 분기", "스페이싱"],
              summaryBox: "점프 회피 패턴은 상대적으로 적음.",
              defaultExpanded: false,
            },
            {
              id: "cemetery",
              nameKo: "묘지 그림자",
              nameEn: "Cemetery Shade",
              priority: "",
              links: [
                { label: "Fextralife Wiki", url: "https://eldenring.wiki.fextralife.com/Cemetery+Shade" },
                { label: "나무위키", url: "https://namu.wiki/w/묘지%20그림자" },
                { label: "YouTube", url: "https://www.youtube.com/results?search_query=Cemetery+Shade" },
              ],
              reason: "빠른 쌍검 공격. 느린 중갑 vs 빠른 경량 대비 전투 리듬.",
              patterns: [],
              coverage: ["리듬 대비", "연속 공격"],
              summaryBox: "",
              defaultExpanded: false,
            },
          ],
        },
      ],
    };
  }

  function normalizeEnemy(e) {
    e = e || {};
    return {
      id: String(e.id || "").trim() || "enemy_" + Math.random().toString(36).slice(2, 9),
      nameKo: String(e.nameKo || ""),
      nameEn: String(e.nameEn || ""),
      priority: String(e.priority || ""),
      links: Array.isArray(e.links)
        ? e.links
            .map(function (l) {
              return { label: String((l && l.label) || ""), url: String((l && l.url) || "") };
            })
            .filter(function (l) {
              return l.label || l.url;
            })
        : [],
      reason: String(e.reason || ""),
      patterns: Array.isArray(e.patterns) ? e.patterns.map(String) : [],
      coverage: Array.isArray(e.coverage) ? e.coverage.map(String) : [],
      summaryBox: String(e.summaryBox || ""),
      defaultExpanded: !!e.defaultExpanded,
    };
  }

  function normalizeStage(s) {
    s = s || {};
    return {
      id: Number(s.id) || 0,
      titleKo: String(s.titleKo || ""),
      titleEn: String(s.titleEn || ""),
      badgeTheme: ["green", "blue", "orange", "gray"].indexOf(s.badgeTheme) >= 0 ? s.badgeTheme : "green",
      phaseLabel: String(s.phaseLabel || ""),
      phaseStyle: s.phaseStyle === "orange" ? "orange" : "",
      summary: String(s.summary || ""),
      tags: Array.isArray(s.tags) ? s.tags.map(String) : [],
      enemies: Array.isArray(s.enemies) ? s.enemies.map(normalizeEnemy) : [],
    };
  }

  function normalizeData(raw) {
    if (!raw || typeof raw !== "object") return defaultData();
    return {
      title: String(raw.title || defaultData().title),
      subtitle: String(raw.subtitle || ""),
      stages: Array.isArray(raw.stages) ? raw.stages.map(normalizeStage) : [],
    };
  }

  function load() {
    try {
      var s = localStorage.getItem(STORAGE_KEY);
      if (!s) return null;
      return normalizeData(JSON.parse(s));
    } catch (e) {
      return null;
    }
  }

  function save(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizeData(data)));
  }

  function clearStorage() {
    localStorage.removeItem(STORAGE_KEY);
  }

  function downloadJson(data) {
    var blob = new Blob([JSON.stringify(normalizeData(data), null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "enemy-reference-guide.json";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function readFileAsJson(file, callback) {
    var reader = new FileReader();
    reader.onload = function () {
      try {
        callback(null, normalizeData(JSON.parse(reader.result)));
      } catch (e) {
        callback(e);
      }
    };
    reader.onerror = function () {
      callback(new Error("read fail"));
    };
    reader.readAsText(file, "UTF-8");
  }

  global.EnemyGuideCore = {
    STORAGE_KEY: STORAGE_KEY,
    defaultData: defaultData,
    normalizeData: normalizeData,
    load: load,
    save: save,
    clearStorage: clearStorage,
    downloadJson: downloadJson,
    readFileAsJson: readFileAsJson,
  };
})(typeof window !== "undefined" ? window : this);
