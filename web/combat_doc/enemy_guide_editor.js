(function () {
  var C = window.EnemyGuideCore;
  if (!C) return;

  var root;

  function splitLines(s) {
    return String(s || "")
      .split(/[\n,]+/)
      .map(function (x) {
        return x.trim();
      })
      .filter(Boolean);
  }

  function linksToText(links) {
    return (links || [])
      .map(function (l) {
        return (l.label || "") + "|" + (l.url || "");
      })
      .join("\n");
  }

  function textToLinks(text) {
    return String(text || "")
      .split("\n")
      .map(function (line) {
        line = line.trim();
        if (!line) return null;
        var i = line.indexOf("|");
        if (i < 0) return { label: line, url: "" };
        return { label: line.slice(0, i).trim(), url: line.slice(i + 1).trim() };
      })
      .filter(Boolean);
  }

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "className") e.className = attrs[k];
        else if (k === "html") e.innerHTML = attrs[k];
        else e.setAttribute(k, attrs[k]);
      });
    }
    if (html !== undefined && !attrs.html) e.innerHTML = html;
    return e;
  }

  function fieldLabel(text, input) {
    var lb = document.createElement("label");
    lb.appendChild(document.createTextNode(text + " "));
    lb.appendChild(input);
    return lb;
  }

  function renderEnemyEditor(enemy, index) {
    var wrap = el("div", { className: "enemy-editor" });
    wrap.dataset.enemyIndex = String(index);

    var h = el("h4", {}, "적 #" + (index + 1));
    wrap.appendChild(h);

    var idIn = el("input", { type: "text", name: "enemyId", value: enemy.id || "" });
    wrap.appendChild(fieldLabel("ID (고유)", idIn));

    var ko = el("input", { type: "text", name: "nameKo", value: enemy.nameKo || "" });
    wrap.appendChild(fieldLabel("이름 (한글)", ko));

    var en = el("input", { type: "text", name: "nameEn", value: enemy.nameEn || "" });
    wrap.appendChild(fieldLabel("이름 (영문)", en));

    var pr = el("input", { type: "text", name: "priority", value: enemy.priority || "", placeholder: "예: 1순위 추천 (없으면 비움)" });
    wrap.appendChild(fieldLabel("우선순위 배지", pr));

    var lk = el("textarea", { name: "links", rows: "3" });
    lk.value = linksToText(enemy.links);
    wrap.appendChild(fieldLabel("링크 (한 줄에 라벨|URL)", lk));
    var lkHint = el("p", { className: "hint" });
    lkHint.textContent = "예: Fextralife Wiki|https://...";
    wrap.appendChild(lkHint);

    var rs = el("textarea", { name: "reason", rows: "4" });
    rs.value = enemy.reason || "";
    wrap.appendChild(fieldLabel("추천 이유", rs));

    var pt = el("textarea", { name: "patterns", rows: "2" });
    pt.value = (enemy.patterns || []).join("\n");
    wrap.appendChild(fieldLabel("예상 패턴 (줄바꿈 또는 쉼표)", pt));

    var cv = el("textarea", { name: "coverage", rows: "2" });
    cv.value = (enemy.coverage || []).join("\n");
    wrap.appendChild(fieldLabel("테스트 커버리지", cv));

    var sb = el("textarea", { name: "summaryBox", rows: "2" });
    sb.value = enemy.summaryBox || "";
    wrap.appendChild(fieldLabel("하단 요약 박스", sb));

    var ex = el("label", {});
    var cb = el("input", { type: "checkbox", name: "defaultExpanded" });
    cb.checked = !!enemy.defaultExpanded;
    ex.appendChild(cb);
    ex.appendChild(document.createTextNode(" 기본 펼침"));
    wrap.appendChild(ex);

    var rm = el("button", { type: "button", className: "danger" }, "이 적 삭제");
    rm.addEventListener("click", function () {
      wrap.remove();
      reindexEnemies(wrap.parentElement);
    });
    var ra = el("div", { className: "row-actions" });
    ra.appendChild(rm);
    wrap.appendChild(ra);

    return wrap;
  }

  function reindexEnemies(container) {
    if (!container) return;
    var list = container.querySelectorAll(".enemy-editor");
    list.forEach(function (node, i) {
      var h = node.querySelector("h4");
      if (h) h.textContent = "적 #" + (i + 1);
      node.dataset.enemyIndex = String(i);
    });
  }

  function gatherEnemies(container) {
    var out = [];
    container.querySelectorAll(".enemy-editor").forEach(function (node) {
      var gid = node.querySelector('[name="enemyId"]');
      var ko = node.querySelector('[name="nameKo"]');
      var en = node.querySelector('[name="nameEn"]');
      var pr = node.querySelector('[name="priority"]');
      var lk = node.querySelector('[name="links"]');
      var rs = node.querySelector('[name="reason"]');
      var pt = node.querySelector('[name="patterns"]');
      var cv = node.querySelector('[name="coverage"]');
      var sb = node.querySelector('[name="summaryBox"]');
      var ex = node.querySelector('[name="defaultExpanded"]');
      out.push({
        id: (gid && gid.value) || "",
        nameKo: (ko && ko.value) || "",
        nameEn: (en && en.value) || "",
        priority: (pr && pr.value) || "",
        links: textToLinks(lk && lk.value),
        reason: (rs && rs.value) || "",
        patterns: splitLines(pt && pt.value),
        coverage: splitLines(cv && cv.value),
        summaryBox: (sb && sb.value) || "",
        defaultExpanded: !!(ex && ex.checked),
      });
    });
    return out;
  }

  function renderStageEditor(stage, index) {
    var wrap = el("div", { className: "stage-editor" });
    wrap.dataset.stageIndex = String(index);

    wrap.appendChild(el("h3", {}, "단계 #" + (index + 1)));

    var sid = el("input", { type: "number", name: "stageId", value: String(stage.id || index + 1), min: "1" });
    wrap.appendChild(fieldLabel("단계 번호 (표시 숫자)", sid));

    var tk = el("input", { type: "text", name: "titleKo", value: stage.titleKo || "" });
    wrap.appendChild(fieldLabel("단계명 (한글)", tk));

    var te = el("input", { type: "text", name: "titleEn", value: stage.titleEn || "" });
    wrap.appendChild(fieldLabel("단계명 (영문, 선택)", te));

    var th = el("select", { name: "badgeTheme" });
    ["green", "blue", "orange", "gray"].forEach(function (v) {
      var o = el("option", { value: v }, v);
      if ((stage.badgeTheme || "green") === v) o.selected = true;
      th.appendChild(o);
    });
    wrap.appendChild(fieldLabel("번호 원 색 (badgeTheme)", th));

    var pl = el("input", { type: "text", name: "phaseLabel", value: stage.phaseLabel || "" });
    wrap.appendChild(fieldLabel("개발 단계 배지 (예: 프로토타입)", pl));

    var ps = el("label", {});
    var pcb = el("input", { type: "checkbox", name: "phaseStyleOrange" });
    pcb.checked = stage.phaseStyle === "orange";
    ps.appendChild(pcb);
    ps.appendChild(document.createTextNode(" 배지 스타일 주황(본개발 느낌)"));
    wrap.appendChild(ps);

    var sm = el("textarea", { name: "stageSummary", rows: "2" });
    sm.value = stage.summary || "";
    wrap.appendChild(fieldLabel("한 줄 설명", sm));

    var tg = el("textarea", { name: "stageTags", rows: "2" });
    tg.value = (stage.tags || []).join("\n");
    wrap.appendChild(fieldLabel("단계 특성 칩 (줄바꿈 또는 쉼표)", tg));

    var ec = el("div", { className: "enemies-wrap" });
    (stage.enemies || []).forEach(function (en, j) {
      ec.appendChild(renderEnemyEditor(en, j));
    });
    wrap.appendChild(el("p", { className: "hint" }, "적 카드"));
    wrap.appendChild(ec);

    var addEn = el("button", { type: "button", className: "secondary" }, "+ 적 추가");
    addEn.addEventListener("click", function () {
      ec.appendChild(
        renderEnemyEditor(
          {
            id: "",
            nameKo: "",
            nameEn: "",
            priority: "",
            links: [],
            reason: "",
            patterns: [],
            coverage: [],
            summaryBox: "",
            defaultExpanded: false,
          },
          ec.querySelectorAll(".enemy-editor").length
        )
      );
      reindexEnemies(ec);
    });
    wrap.appendChild(addEn);

    var rmSt = el("button", { type: "button", className: "danger" }, "이 단계 전체 삭제");
    rmSt.addEventListener("click", function () {
      if (!confirm("이 단계를 삭제할까요?")) return;
      wrap.remove();
      reindexStages();
    });
    var ra = el("div", { className: "row-actions" });
    ra.appendChild(rmSt);
    wrap.appendChild(ra);

    return wrap;
  }

  function reindexStages() {
    root.querySelectorAll(".stage-editor").forEach(function (node, i) {
      var h = node.querySelector("h3");
      if (h) h.textContent = "단계 #" + (i + 1);
      node.dataset.stageIndex = String(i);
    });
  }

  function gatherStages() {
    var out = [];
    root.querySelectorAll(".stage-editor").forEach(function (node) {
      var sid = node.querySelector('[name="stageId"]');
      var tk = node.querySelector('[name="titleKo"]');
      var te = node.querySelector('[name="titleEn"]');
      var th = node.querySelector('[name="badgeTheme"]');
      var pl = node.querySelector('[name="phaseLabel"]');
      var po = node.querySelector('[name="phaseStyleOrange"]');
      var sm = node.querySelector('[name="stageSummary"]');
      var tg = node.querySelector('[name="stageTags"]');
      var ec = node.querySelector(".enemies-wrap");
      out.push({
        id: parseInt((sid && sid.value) || "0", 10) || out.length + 1,
        titleKo: (tk && tk.value) || "",
        titleEn: (te && te.value) || "",
        badgeTheme: (th && th.value) || "green",
        phaseLabel: (pl && pl.value) || "",
        phaseStyle: po && po.checked ? "orange" : "",
        summary: (sm && sm.value) || "",
        tags: splitLines(tg && tg.value),
        enemies: gatherEnemies(ec),
      });
    });
    return out;
  }

  function gatherData() {
    var title = root.querySelector('[name="docTitle"]');
    var sub = root.querySelector('[name="docSubtitle"]');
    return {
      title: (title && title.value) || "",
      subtitle: (sub && sub.value) || "",
      stages: gatherStages(),
    };
  }

  function renderEditor(data) {
    root = document.getElementById("editor-root");
    if (!root) return;
    root.innerHTML = "";

    var meta = el("fieldset", { className: "editor-fieldset" });
    meta.appendChild(el("legend", {}, "문서 머리글"));
    var t1 = el("input", { type: "text", name: "docTitle", value: data.title || "" });
    meta.appendChild(fieldLabel("타이틀 (영문 대문자 권장)", t1));
    var t2 = el("input", { type: "text", name: "docSubtitle", value: data.subtitle || "" });
    meta.appendChild(fieldLabel("부제 (한 줄)", t2));
    root.appendChild(meta);

    var sc = el("div", { id: "stages-container" });
    (data.stages || []).forEach(function (st, i) {
      sc.appendChild(renderStageEditor(st, i));
    });
    root.appendChild(sc);

    var addSt = el("button", { type: "button" }, "+ 단계 추가");
    addSt.addEventListener("click", function () {
      sc.appendChild(
        renderStageEditor(
          {
            id: sc.querySelectorAll(".stage-editor").length + 1,
            titleKo: "새 단계",
            titleEn: "",
            badgeTheme: "gray",
            phaseLabel: "프로토타입",
            phaseStyle: "",
            summary: "",
            tags: [],
            enemies: [
              {
                id: "",
                nameKo: "",
                nameEn: "",
                priority: "",
                links: [],
                reason: "",
                patterns: [],
                coverage: [],
                summaryBox: "",
                defaultExpanded: true,
              },
            ],
          },
          sc.querySelectorAll(".stage-editor").length
        )
      );
      reindexStages();
    });
    root.appendChild(addSt);
  }

  function setStatus(msg) {
    var s = document.getElementById("editor-status");
    if (s) s.textContent = msg || "";
  }

  function initToolbar() {
    document.getElementById("btn-save").addEventListener("click", function () {
      var d = gatherData();
      C.save(d);
      setStatus("브라우저에 저장했습니다. 보기 페이지를 새로고침하면 반영됩니다.");
    });
    document.getElementById("btn-export").addEventListener("click", function () {
      C.downloadJson(gatherData());
      setStatus("JSON 파일을 내려받았습니다.");
    });
    document.getElementById("btn-import").addEventListener("click", function () {
      document.getElementById("file-import").click();
    });
    document.getElementById("file-import").addEventListener("change", function (ev) {
      var f = ev.target.files && ev.target.files[0];
      ev.target.value = "";
      if (!f) return;
      C.readFileAsJson(f, function (err, data) {
        if (err) {
          setStatus("JSON 파싱 실패: " + err.message);
          return;
        }
        C.save(data);
        renderEditor(data);
        setStatus("가져오기 완료. 저장됨.");
      });
    });
    document.getElementById("btn-clear").addEventListener("click", function () {
      if (!confirm("저장소를 비우고 샘플 데이터로 되돌릴까요?")) return;
      C.clearStorage();
      renderEditor(C.defaultData());
      setStatus("초기화했습니다.");
    });
  }

  function init() {
    var data = C.load();
    if (!data || !data.stages || !data.stages.length) data = C.defaultData();
    renderEditor(C.normalizeData(data));
    initToolbar();
    setStatus("편집 후 「브라우저에 저장」하면 보기 페이지와 동일 출처(localStorage)를 씁니다.");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
