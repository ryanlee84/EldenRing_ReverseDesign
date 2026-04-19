/* global Papa */

/** AtkParam 문서 열 — app.js / combat_doc_export.py 와 동일 */
const DOC_COLUMNS = [
  "rowid",
  "rowname",
  "atkphys",
  "atkmag",
  "atkfire",
  "atkthun",
  "atkstam",
  "hit0_radius",
  "hit1_radius",
  "hit2_radius",
  "hit3_radius",
  "knockbackdist",
  "hitstoptime",
  "dmglevel",
  "guardatkrate",
  "guardbreakrate",
  "speffectid0",
  "speffectid1",
  "speffectid2",
  "speffectid3",
  "speffectid4",
  "atksuperarmor",
  "atkbehaviorid",
  "isarrowatk",
];

function normKey(s) {
  return String(s ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "")
    .replace(/_/g, "");
}

/** @param {string[]} headers */
function findHeader(headers, candidates) {
  const map = new Map(headers.map((h) => [normKey(h), h]));
  for (const c of candidates) {
    const hit = map.get(normKey(c));
    if (hit) return hit;
  }
  for (const h of headers) {
    const n = normKey(h);
    for (const c of candidates) {
      if (n.includes(normKey(c)) || normKey(c).includes(n)) return h;
    }
  }
  return null;
}

function rowGet(row, headers, candidates, fallback = "") {
  const h = findHeader(headers, candidates);
  if (!h) return fallback;
  const v = row[h];
  return v != null && String(v).trim() !== "" ? String(v).trim() : fallback;
}

function parseNum(v) {
  const n = parseFloat(String(v).replace(/,/g, ""));
  return Number.isFinite(n) ? n : NaN;
}

/** Param 컷율(0~100 등) → 표시용 % 문자열 */
function fmtCut(v) {
  if (v === "" || v == null) return "—";
  const n = parseNum(v);
  if (!Number.isFinite(n)) return String(v);
  if (Math.abs(n - Math.round(n)) < 1e-6) return `${Math.round(n)}%`;
  return `${n}%`;
}

function fmtResist(v) {
  if (v === "" || v == null) return "—";
  const n = parseNum(v);
  if (!Number.isFinite(n)) return String(v);
  if (n === 0) return "—";
  if (Math.abs(n - Math.round(n)) < 1e-6) return `${Math.round(n)}`;
  return String(n);
}

function escMdCell(s) {
  return String(s ?? "")
    .replace(/\|/g, "\\|")
    .replace(/\r?\n/g, " ");
}

function formatFileSize(bytes) {
  const n = Number(bytes) || 0;
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

/** 파일명에서 c3251 / 3251 형태 chr 힌트 */
function chrHintFromFilename(name) {
  const m = /(?:^|[^\d])(c?)(\d{4})\b/i.exec(String(name || ""));
  if (!m) return "";
  const num = m[2];
  return m[1].toLowerCase() === "c" ? `c${num}` : num;
}

/**
 * @param {{ kind: string, name: string, size: number, chrHint: string }[]} entries
 * @returns {string}
 */
function buildBundleMarkdownSection(entries) {
  if (!entries || !entries.length) return "";
  const lines = [];
  lines.push("### 번들 등록 (자산)");
  lines.push("");
  lines.push(
    "*(브라우저는 `anibnd`/`chrbnd`를 열지 않습니다. Smithbox·DS Anim Studio 등으로 TAE를 뽑은 뒤 위 폼의 TAE JSON을 합치면 `docs/reverse_engineering_combat_sheet.md` 2단계와 연결됩니다.)*"
  );
  lines.push("");
  for (const e of entries) {
    const hint = e.chrHint ? ` — \`${e.chrHint}\`` : "";
    lines.push(
      `- **${escMdCell(e.kind)}** \`${escMdCell(e.name)}\` — ${formatFileSize(e.size)}${hint}`
    );
  }
  lines.push("");
  return lines.join("\n");
}

function loadAtkRows(allRows, headers, include, exclude) {
  const nameKey =
    findHeader(headers, ["rowname", "Row Name", "Name"]) || "rowname";
  const rows = [];
  for (const row of allRows) {
    const name = String(row[nameKey] ?? "").trim();
    if (!name.includes(include)) continue;
    if (exclude && name.includes(exclude)) continue;
    const o = {};
    for (const k of Object.keys(row)) {
      o[k] = String(row[k] ?? "").trim();
    }
    rows.push(o);
  }
  const ridKey = findHeader(headers, ["rowid", "Row ID", "ID"]) || "rowid";
  rows.sort(
    (a, b) => (parseInt(a[ridKey], 10) || 0) - (parseInt(b[ridKey], 10) || 0)
  );
  return rows;
}

function pickFirstNpcRow(allRows, headers, include, exclude) {
  const nameKey =
    findHeader(headers, ["rowname", "Row Name", "Name"]) || "rowname";
  for (const row of allRows) {
    const name = String(row[nameKey] ?? "").trim();
    if (!name.includes(include)) continue;
    if (exclude && name.includes(exclude)) continue;
    const o = {};
    for (const k of Object.keys(row)) {
      o[k] = String(row[k] ?? "").trim();
    }
    return o;
  }
  return null;
}

function guessAtkKind(row, atkHeaders) {
  const p = parseNum(rowGet(row, atkHeaders, ["atkphys"])) || 0;
  const m = parseNum(rowGet(row, atkHeaders, ["atkmag"])) || 0;
  const f = parseNum(rowGet(row, atkHeaders, ["atkfire"])) || 0;
  const t = parseNum(rowGet(row, atkHeaders, ["atkthun"])) || 0;
  const max = Math.max(p, m, f, t, 1e-9);
  if (m === max && m >= p) return "마력";
  if (f === max && f >= p) return "화염";
  if (t === max && t >= p) return "벼락";
  return "물리";
}

function slimAtkRow(row, atkHeaders) {
  const o = {};
  for (const c of DOC_COLUMNS) {
    const hk = findHeader(atkHeaders, [c, c.replace(/_/g, "")]);
    if (hk && row[hk] !== undefined) o[c] = row[hk];
    else o[c] = row[c] ?? "";
  }
  return o;
}

function dmgRatioHint(row) {
  const p = parseNum(row.atkphys) || 0;
  if (p <= 0) return "—";
  const r = p / 100;
  if (Math.abs(r - Math.round(r * 10) / 10) < 0.02)
    return String(Math.round(r * 10) / 10);
  return r.toFixed(2);
}

function buildNotionMarkdown(opts) {
  const {
    titleKo,
    titleEn,
    wikiLabel,
    wikiUrl,
    npcRow,
    npcHeaders,
    atkRows,
    atkHeaders,
    imageMdLine,
    bundleSection,
    taeNote,
    regulationNote,
  } = opts;

  const lines = [];
  lines.push(`# ${escMdCell(titleKo)}`);
  lines.push("");
  lines.push(`**${escMdCell(titleEn)}**`);
  lines.push("");
  if (imageMdLine) {
    lines.push(imageMdLine);
    lines.push("");
  }

  let displayName = "";
  if (npcRow) {
    displayName =
      rowGet(npcRow, npcHeaders, ["name", "Name", "characterName"]) ||
      rowGet(npcRow, npcHeaders, ["rowname", "Row Name"]) ||
      "";
  }
  const hp =
    npcRow &&
    rowGet(npcRow, npcHeaders, [
      "hp",
      "HP",
      "maxHp",
      "HitPoint",
      "hitPoint",
    ]);
  const poise =
    npcRow &&
    rowGet(npcRow, npcHeaders, [
      "toughness",
      "poise",
      "saDurability",
      "superArmorDurability",
    ]);
  const npcType =
    npcRow &&
    rowGet(npcRow, npcHeaders, ["npcKind", "npcType", "kind", "NPCType"]);

  lines.push("| **이름** | **" + escMdCell(displayName || "*(NpcParam 행 선택 필요)*") + "** |");
  if (wikiUrl) {
    lines.push(
      "| **등장 지역** | [" +
        escMdCell(wikiLabel || "위키") +
        "](" +
        wikiUrl.trim() +
        ") |"
    );
  } else {
    lines.push("| **등장 지역** | *(위키 URL 입력)* |");
  }
  lines.push("| **등급** | **" + escMdCell(npcType || "—") + "** |");
  lines.push("| **체력 (1주차 기준)** | **" + escMdCell(hp || "—") + "** |");
  lines.push("| **강인도** | **" + escMdCell(poise || "—") + "** |");
  lines.push("");
  lines.push("---");
  lines.push("");

  if (npcRow && npcHeaders.length) {
    lines.push("### 경감률");
    lines.push("");
    lines.push(
      "| **표준** | **참격** | **관통** | **타격** | **마력** | **화염** | **벼락** | **신성** |"
    );
    lines.push("| --- | --- | --- | --- | --- | --- | --- | --- |");
    const std = rowGet(npcRow, npcHeaders, [
      "neutralDamageCutRate",
      "neutralPhysDamageCutRate",
      "physicsDamageCutRate",
      "physDamageCutRate",
      "physicalDamageCutRate",
    ]);
    const sl = rowGet(npcRow, npcHeaders, ["slashDamageCutRate", "slashAttackCutRate"]);
    const th = rowGet(npcRow, npcHeaders, ["thrustDamageCutRate", "pierceDamageCutRate"]);
    const bl = rowGet(npcRow, npcHeaders, ["blowDamageCutRate", "strikeDamageCutRate"]);
    const mg = rowGet(npcRow, npcHeaders, ["magicDamageCutRate"]);
    const fr = rowGet(npcRow, npcHeaders, ["fireDamageCutRate"]);
    const thu = rowGet(npcRow, npcHeaders, ["thunderDamageCutRate", "lightningDamageCutRate"]);
    const hol = rowGet(npcRow, npcHeaders, [
      "holyDamageCutRate",
      "faithDamageCutRate",
      "lightDamageCutRate",
      "darkDamageCutRate",
    ]);
    lines.push(
      "| **" +
        fmtCut(std) +
        "** | **" +
        fmtCut(sl) +
        "** | **" +
        fmtCut(th) +
        "** | **" +
        fmtCut(bl) +
        "** | **" +
        fmtCut(mg) +
        "** | **" +
        fmtCut(fr) +
        "** | **" +
        fmtCut(thu) +
        "** | **" +
        fmtCut(hol) +
        "** |"
    );
    lines.push("");

    lines.push("### 내성치 (1주차 기준)");
    lines.push("");
    lines.push(
      "| **독** | **붉은 부패** | **수면** | **발광** | **출혈** | **동상** | **죽음** |"
    );
    lines.push("| --- | --- | --- | --- | --- | --- | --- |");
    const rp = rowGet(npcRow, npcHeaders, ["resistPoison"]);
    const rr = rowGet(npcRow, npcHeaders, [
      "resistPlague",
      "resistRot",
      "resistScarletRot",
      "resistDisease",
    ]);
    const rs = rowGet(npcRow, npcHeaders, ["resistSleep"]);
    const rm = rowGet(npcRow, npcHeaders, ["resistMadness"]);
    const rb = rowGet(npcRow, npcHeaders, ["resistBlood", "resistBleed"]);
    const rf = rowGet(npcRow, npcHeaders, ["resistFrost", "resistCold", "resistFreeze"]);
    const rc = rowGet(npcRow, npcHeaders, ["resistCurse", "resistDeathBlight"]);
    lines.push(
      "| **" +
        fmtResist(rp) +
        "** | **" +
        fmtResist(rr) +
        "** | **" +
        fmtResist(rs) +
        "** | **" +
        fmtResist(rm) +
        "** | **" +
        fmtResist(rb) +
        "** | **" +
        fmtResist(rf) +
        "** | **" +
        fmtResist(rc) +
        "** |"
    );
    lines.push("");
  } else {
    lines.push("### 경감률");
    lines.push("");
    lines.push("*(NpcParam CSV를 올리고 행 필터를 맞추면 자동 채워집니다.)*");
    lines.push("");
    lines.push("### 내성치 (1주차 기준)");
    lines.push("");
    lines.push("*(동일)*");
    lines.push("");
  }

  lines.push("### **스킬**");
  lines.push("");
  lines.push(
    "| No | 스킬명 | 속성 | 기획적 특징(의도) | 데미지 배율 | 강인도 데미지 |"
  );
  lines.push("| --- | --- | --- | --- | --- | --- |");
  if (atkRows.length) {
    let no = 1;
    for (const row of atkRows) {
      const slim = slimAtkRow(row, atkHeaders);
      const name = slim.rowname || "—";
      const kind = guessAtkKind(slim, atkHeaders);
      const ratio = dmgRatioHint(slim);
      const sa = slim.atksuperarmor || "—";
      lines.push(
        "| " +
          no +
          " | " +
          escMdCell(name) +
          " | " +
          escMdCell(kind) +
          " | *(노션에서 수정)* | " +
          escMdCell(ratio) +
          " | " +
          escMdCell(sa) +
          " |"
      );
      no += 1;
    }
  } else {
    lines.push(
      "| — | *(AtkParam CSV + 필터)* | — | — | — | — |"
    );
  }
  lines.push("");

  if (bundleSection) {
    lines.push(bundleSection);
  }

  lines.push("### **프레임 분석**");
  lines.push("");
  if (taeNote) {
    lines.push(taeNote);
  } else {
    lines.push(
      "[*(TAE JSON을 올리면 여기에 애니 요약이 붙습니다. `anibnd`만 등록된 경우에도 JSON 추출 전까지는 이 안내가 표시됩니다.)*](#)"
    );
  }
  lines.push("");

  if (regulationNote) {
    lines.push("---");
    lines.push("");
    lines.push(`*regulation / 출처: ${escMdCell(regulationNote)}*`);
  }

  return lines.join("\n");
}

async function fileToDataUrl(file, maxBytes) {
  if (!file || !file.size) return null;
  if (file.size > maxBytes) return { error: `이미지가 큼 (${(file.size / 1024 / 1024).toFixed(1)}MB > ${(maxBytes / 1024 / 1024).toFixed(1)}MB). 노션에는 파일을 따로 드래그하세요.` };
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve({ dataUrl: r.result });
    r.onerror = () => reject(new Error("이미지 읽기 실패"));
    r.readAsDataURL(file);
  });
}

function summarizeTae(tae) {
  if (!tae || typeof tae !== "object") return "";
  const anims = tae.animations;
  if (!Array.isArray(anims) || !anims.length) {
    return "*(TAE JSON에 animations[]가 없습니다.)*";
  }
  const parts = [];
  for (const a of anims) {
    const ev = Array.isArray(a.events) ? a.events : [];
    parts.push(`- **${a.name || "(이름 없음)"}** — 이벤트 ${ev.length}개`);
  }
  return parts.join("\n");
}

async function generate() {
  if (typeof Papa === "undefined") {
    throw new Error("PapaParse 로드 실패 — 네트워크를 확인하세요.");
  }
  const status = document.getElementById("status");
  const out = document.getElementById("notion-md");
  const previewImg = document.getElementById("cover-preview");
  status.textContent = "처리 중…";
  status.classList.remove("error");

  const npcFile = document.getElementById("file-npc").files[0];
  const atkFile = document.getElementById("file-atk").files[0];
  const imgFile = document.getElementById("file-img").files[0];
  const taeFile = document.getElementById("file-tae").files[0];
  const anibndFile = document.getElementById("file-anibnd").files[0];
  const chrbndFile = document.getElementById("file-chrbnd").files[0];

  const titleKo = document.getElementById("title-ko").value.trim() || "보스 이름 (한글)";
  const titleEn = document.getElementById("title-en").value.trim() || "Boss Name (English)";
  const wikiLabel = document.getElementById("wiki-label").value.trim();
  const wikiUrl = document.getElementById("wiki-url").value.trim();
  const npcKey = document.getElementById("npc-key").value.trim();
  const npcEx = document.getElementById("npc-exclude").value.trim();
  const atkKey = document.getElementById("atk-key").value.trim() || "[Tree Sentinel]";
  const atkEx = document.getElementById("atk-exclude").value.trim();
  const regNote = document.getElementById("reg-note").value.trim();

  let npcHeaders = [];
  let npcRow = null;
  if (npcFile && npcKey) {
    const t = await npcFile.text();
    const parsed = Papa.parse(t, { header: true, skipEmptyLines: true });
    if (parsed.errors?.length) throw new Error(parsed.errors[0].message);
    npcHeaders = parsed.meta.fields || [];
    npcRow = pickFirstNpcRow(parsed.data, npcHeaders, npcKey, npcEx || null);
  }

  if (!atkFile) throw new Error("AtkParam_Npc CSV는 필수입니다.");

  const atkText = await atkFile.text();
  const atkParsed = Papa.parse(atkText, { header: true, skipEmptyLines: true });
  if (atkParsed.errors?.length) throw new Error(atkParsed.errors[0].message);
  const atkHeaders = atkParsed.meta.fields || [];
  const atkRows = loadAtkRows(atkParsed.data, atkHeaders, atkKey, atkEx || null);

  let imageMdLine = "";
  previewImg.innerHTML = "";
  previewImg.classList.add("hidden");
  if (imgFile) {
    const MAX = 1.5 * 1024 * 1024;
    const r = await fileToDataUrl(imgFile, MAX);
    if (r && r.error) {
      imageMdLine = `*(표지: ${imgFile.name} — ${r.error})*`;
    } else if (r && r.dataUrl) {
      imageMdLine = `![표지 ${escMdCell(imgFile.name)}](${r.dataUrl})`;
      const im = document.createElement("img");
      im.src = r.dataUrl;
      im.alt = "표지 미리보기";
      previewImg.appendChild(im);
      previewImg.classList.remove("hidden");
    }
  }

  let taeNote = "";
  if (taeFile && taeFile.size) {
    const raw = await taeFile.text();
    const tae = JSON.parse(raw);
    taeNote = summarizeTae(tae);
  }

  const bundleEntries = [];
  if (anibndFile && anibndFile.size) {
    bundleEntries.push({
      kind: "anibnd",
      name: anibndFile.name,
      size: anibndFile.size,
      chrHint: chrHintFromFilename(anibndFile.name),
    });
  }
  if (chrbndFile && chrbndFile.size) {
    bundleEntries.push({
      kind: "chrbnd",
      name: chrbndFile.name,
      size: chrbndFile.size,
      chrHint: chrHintFromFilename(chrbndFile.name),
    });
  }
  const bundleSection = buildBundleMarkdownSection(bundleEntries);

  const md = buildNotionMarkdown({
    titleKo,
    titleEn,
    wikiLabel,
    wikiUrl,
    npcRow,
    npcHeaders,
    atkRows,
    atkHeaders,
    imageMdLine,
    bundleSection,
    taeNote,
    regulationNote: regNote,
  });

  out.value = md;
  let msg = `완료 — 스킬 행 ${atkRows.length}개`;
  if (npcFile && npcKey) {
    msg += npcRow ? ", NpcParam 1행" : " · NpcParam에서 행 없음(필터·파일 확인)";
  }
  if (bundleEntries.length) {
    msg += `, 번들 ${bundleEntries.length}개 기록`;
  }
  status.textContent = msg;
}

function init() {
  document.getElementById("btn-gen").addEventListener("click", async () => {
    const status = document.getElementById("status");
    try {
      await generate();
    } catch (e) {
      status.textContent = String(e.message || e);
      status.classList.add("error");
    }
  });

  document.getElementById("btn-copy").addEventListener("click", async () => {
    const ta = document.getElementById("notion-md");
    const t = ta.value;
    if (!t) return;
    try {
      await navigator.clipboard.writeText(t);
      const status = document.getElementById("status");
      status.textContent = "클립보드에 복사했습니다. 노션 페이지에 붙여넣기 하세요.";
      status.classList.remove("error");
    } catch {
      ta.select();
      document.execCommand("copy");
      document.getElementById("status").textContent =
        "복사에 실패했으면 텍스트 상자를 직접 선택해 Ctrl+C 하세요.";
    }
  });

  document.getElementById("btn-dl").addEventListener("click", () => {
    const ta = document.getElementById("notion-md");
    const t = ta.value;
    if (!t) return;
    const name =
      document.getElementById("title-ko").value.trim().replace(/[^\w\uac00-\ud7a3\-]+/g, "_") ||
      "notion_boss";
    const blob = new Blob([t], { type: "text/markdown;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${name.slice(0, 80)}_notion.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
