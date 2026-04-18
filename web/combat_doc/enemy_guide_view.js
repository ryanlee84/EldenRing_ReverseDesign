(function () {
  var C = window.EnemyGuideCore;
  if (!C) return;

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function escAttr(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;")
      .replace(/</g, "&lt;");
  }

  function renderPills(items, className) {
    if (!items || !items.length) return "";
    return items
      .map(function (t) {
        return '<span class="' + className + '">' + esc(t) + "</span>";
      })
      .join("");
  }

  function renderLinks(links) {
    if (!links || !links.length) return "";
    return links
      .map(function (l) {
        if (!l.url) return "";
        return (
          '<a class="link-btn" href="' +
          escAttr(l.url) +
          '" target="_blank" rel="noopener noreferrer">' +
          esc(l.label || l.url) +
          "</a>"
        );
      })
      .join("");
  }

  function renderEnemy(enemy) {
    var openAttr = enemy.defaultExpanded ? " open" : "";
    var pri = enemy.priority
      ? '<span class="priority-badge">' + esc(enemy.priority) + "</span>"
      : "";
    var patterns = renderPills(enemy.patterns, "pill-pattern");
    var coverage = renderPills(enemy.coverage, "pill-coverage");
    var summaryBox =
      enemy.summaryBox && enemy.summaryBox.trim()
        ? '<div class="summary-box">' + esc(enemy.summaryBox.trim()) + "</div>"
        : "";

    return (
      "<details class=\"enemy-card\"" +
      openAttr +
      ">" +
      "<summary><span class=\"summary-main\"><span>" +
      esc(enemy.nameKo) +
      '</span> <span class="name-en">' +
      esc(enemy.nameEn) +
      "</span>" +
      pri +
      '</span><span class="chev" aria-hidden="true"></span></summary>' +
      '<div class="card-body">' +
      (enemy.links && enemy.links.length
        ? '<div class="link-row">' + renderLinks(enemy.links) + "</div>"
        : "") +
      '<p class="section-label">추천 이유</p>' +
      '<p class="reason-text">' +
      esc(enemy.reason || "") +
      "</p>" +
      (patterns
        ? '<p class="section-label">예상 패턴</p><div class="pill-row">' + patterns + "</div>"
        : "") +
      (coverage
        ? '<p class="section-label">테스트 커버리지</p><div class="pill-row">' + coverage + "</div>"
        : "") +
      summaryBox +
      "</div></details>"
    );
  }

  function renderStage(stage) {
    var tags = (stage.tags || [])
      .map(function (t) {
        return '<span class="pill-stage">' + esc(t) + "</span>";
      })
      .join("");
    var phaseClass = stage.phaseStyle === "orange" ? "phase-badge orange" : "phase-badge";
    var titleEn = stage.titleEn ? ' <span class="name-en">' + esc(stage.titleEn) + "</span>" : "";
    var enemies = (stage.enemies || []).map(renderEnemy).join("");

    return (
      '<section class="stage-block">' +
      '<div class="stage-head">' +
      '<div class="stage-num theme-' +
      esc(stage.badgeTheme || "green") +
      '">' +
      esc(String(stage.id)) +
      "</div>" +
      '<div class="stage-titles">' +
      "<h2>" +
      esc(stage.titleKo) +
      titleEn +
      (stage.phaseLabel ? '<span class="' + phaseClass + '">' + esc(stage.phaseLabel) + "</span>" : "") +
      "</h2>" +
      (stage.summary ? '<p class="stage-summary">' + esc(stage.summary) + "</p>" : "") +
      (tags ? '<div class="stage-tags">' + tags + "</div>" : "") +
      "</div></div>" +
      '<div class="enemy-cards">' +
      enemies +
      "</div></section>"
    );
  }

  function render(data) {
    var app = document.getElementById("app");
    if (!app) return;
    var stages = (data.stages || []).map(renderStage).join("");
    app.innerHTML =
      '<header class="doc-header">' +
      "<h1>" +
      esc(data.title || "") +
      "</h1>" +
      '<p class="sub">' +
      esc(data.subtitle || "") +
      "</p></header>" +
      '<div class="stages-wrap">' +
      stages +
      "</div>";
  }

  function init() {
    var q = new URLSearchParams(location.search);
    if (q.get("demo") === "1") {
      render(C.defaultData());
      return;
    }
    var fromStore = C.load();
    if (fromStore && fromStore.stages && fromStore.stages.length) {
      render(fromStore);
      return;
    }
    render(C.defaultData());
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
