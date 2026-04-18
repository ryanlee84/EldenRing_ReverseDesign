/* global XLSX, Papa */

/** @type {string[]} combat_doc_export.DOC_COLUMNS 과 동일 */
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

let lastPayload = null;
let lastMarkdown = "";

function downloadBlob(filename, mime, text) {
  const blob = new Blob([text], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function attacksToCsv(attacks) {
  if (!attacks || !attacks.length) return "";
  const keys = Object.keys(attacks[0]);
  const esc = (s) => {
    const v = String(s ?? "");
    if (/[",\n]/.test(v)) return `"${v.replace(/"/g, '""')}"`;
    return v;
  };
  const lines = [keys.join(",")];
  for (const row of attacks) {
    lines.push(keys.map((k) => esc(row[k])).join(","));
  }
  return lines.join("\n");
}

function loadRows(allRows, include, exclude) {
  const rows = [];
  for (const row of allRows) {
    const name = (row.rowname || "").trim();
    if (!name.includes(include)) continue;
    if (exclude && name.includes(exclude)) continue;
    const o = {};
    for (const k of Object.keys(row)) {
      o[k] = String(row[k] ?? "").trim();
    }
    rows.push(o);
  }
  rows.sort((a, b) => (parseInt(a.rowid, 10) || 0) - (parseInt(b.rowid, 10) || 0));
  return rows;
}

function slimAttack(row) {
  const o = {};
  for (const k of DOC_COLUMNS) {
    o[k] = row[k] ?? "";
  }
  return o;
}

function renderMarkdown(meta, attacks, inventory, taeExtra) {
  const lines = [];
  lines.push(`# 전투 문서 데이터 — ${meta.title || "Boss"}`);
  lines.push("");
  lines.push(`- 생성: \`${meta.generated || ""}\``);
  lines.push(`- 소스 CSV: \`${meta.csv_path || ""}\``);
  lines.push(`- 필터: 포함 \`${meta.include_key || ""}\``);
  if (meta.exclude_substr) {
    lines.push(`- 제외: \`${meta.exclude_substr}\``);
  }
  lines.push("");

  if (inventory && inventory.length) {
    lines.push("## 자산 폴더 인벤토리");
    lines.push("");
    lines.push("*(바이너리는 이 툴이 해석하지 않음. 파일 경로만 기록.)*");
    lines.push("");
    for (const p of inventory) {
      lines.push(`- \`${p}\``);
    }
    lines.push("");
  }

  lines.push("## 공격 행 (AtkParam_Npc)");
  lines.push("");
  if (!attacks.length) {
    lines.push("*(해당 조건의 행이 없습니다.)*");
  } else {
    const cols = DOC_COLUMNS.filter((c) => attacks.some((r) => c in r));
    lines.push(`| ${cols.join(" | ")} |`);
    lines.push(`| ${cols.map(() => "---").join(" | ")} |`);
    for (const r of attacks) {
      lines.push(
        `| ${cols
          .map((c) => (r[c] || "").replace(/\|/g, "\\|"))
          .join(" | ")} |`
      );
    }
  }
  lines.push("");

  if (taeExtra != null) {
    lines.push("## TAE (외부 JSON 병합)");
    lines.push("");
    lines.push("```json");
    lines.push(JSON.stringify(taeExtra, null, 2));
    lines.push("```");
    lines.push("");
  } else {
    lines.push("## TAE (프레임·이벤트)");
    lines.push("");
    lines.push(
      "*(비어 있음. 별도 도구로 덤프한 JSON을 올리면 이 절이 채워짐.)*"
    );
    lines.push("");
  }

  return lines.join("\n");
}

function buildJsonPayload(meta, attacks, taeExtra) {
  const payload = {
    meta,
    attacks: attacks.map(slimAttack),
  };
  if (taeExtra != null) {
    payload.tae = taeExtra;
  }
  return payload;
}

const TAE_KIND_COLORS = {
  Hit: "#c94c4c",
  Windup: "#5a9c6a",
  Damage: "#c94c4c",
  default: "#6b7a8f",
};

const SVG_NS = "http://www.w3.org/2000/svg";

function colorForTaeKind(kind) {
  const k = String(kind || "");
  return TAE_KIND_COLORS[k] || TAE_KIND_COLORS.default;
}

/**
 * 스키마 v1: tae.animations[].{ name, events: [{ frameStart, frameEnd, kind, rowid?, note? }] }
 */
function renderTaePreview(tae) {
  const wrap = document.getElementById("tae-timeline-wrap");
  if (!wrap) return;
  wrap.innerHTML = "";
  if (tae == null) {
    wrap.classList.add("hidden");
    return;
  }
  wrap.classList.remove("hidden");

  const anims = tae.animations;
  if (!Array.isArray(anims) || anims.length === 0) {
    const p = document.createElement("p");
    p.className = "tae-preview-muted";
    p.textContent =
      "TAE JSON은 있으나 animations[] 타임라인이 없습니다. " +
      "스키마 v1 예시: data/tree_sentinel_tae.example.json " +
      "(events[].frameStart / frameEnd / kind).";
    wrap.appendChild(p);
    return;
  }

  const h3 = document.createElement("h3");
  h3.className = "tae-timeline-title";
  h3.textContent = "TAE 타임라인 (미리보기)";
  wrap.appendChild(h3);

  const W = 640;
  const H = 44;
  const padL = 6;
  const padR = 10;
  const innerW = W - padL - padR;
  const axisY = H - 10;
  const barY = 8;
  const barH = 16;

  for (const anim of anims) {
    const events = Array.isArray(anim.events) ? anim.events : [];
    let maxF = 1;
    for (const ev of events) {
      const fs = Number(ev.frameStart) || 0;
      const fe = Number(ev.frameEnd);
      const end = Number.isFinite(fe) ? fe : fs;
      maxF = Math.max(maxF, fs, end, 1);
    }

    const track = document.createElement("div");
    track.className = "tae-track";

    const nameEl = document.createElement("div");
    nameEl.className = "tae-track-name";
    nameEl.textContent = anim.name || "(이름 없음)";
    track.appendChild(nameEl);

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("class", "tae-svg");
    svg.setAttribute("role", "img");

    const axis = document.createElementNS(SVG_NS, "line");
    axis.setAttribute("x1", String(padL));
    axis.setAttribute("y1", String(axisY));
    axis.setAttribute("x2", String(W - padR));
    axis.setAttribute("y2", String(axisY));
    axis.setAttribute("stroke", "#5c6570");
    axis.setAttribute("stroke-width", "1");
    svg.appendChild(axis);

    for (const ev of events) {
      const fs = Number(ev.frameStart) || 0;
      const fe = Number(ev.frameEnd);
      const end = Number.isFinite(fe) ? fe : fs;
      const lo = Math.min(fs, end);
      const hi = Math.max(fs, end);
      const x1 = padL + (lo / maxF) * innerW;
      const x2 = padL + (hi / maxF) * innerW;
      const bw = Math.max(x2 - x1, 2);

      const rect = document.createElementNS(SVG_NS, "rect");
      rect.setAttribute("x", String(x1));
      rect.setAttribute("width", String(bw));
      rect.setAttribute("y", String(barY));
      rect.setAttribute("height", String(barH));
      rect.setAttribute("fill", colorForTaeKind(ev.kind));
      rect.setAttribute("rx", "2");

      const tip = document.createElementNS(SVG_NS, "title");
      const parts = [String(ev.kind || "?"), `${lo}–${hi} f`];
      if (ev.rowid != null && String(ev.rowid).length) parts.push(`rowid ${ev.rowid}`);
      if (ev.note) parts.push(String(ev.note));
      tip.textContent = parts.join(" · ");
      rect.appendChild(tip);
      svg.appendChild(rect);
    }

    const cap = document.createElementNS(SVG_NS, "text");
    cap.setAttribute("x", String(padL));
    cap.setAttribute("y", String(H - 1));
    cap.setAttribute("fill", "#9aa0a6");
    cap.setAttribute("font-size", "10");
    cap.textContent = `0 — ${maxF} f`;
    svg.appendChild(cap);

    track.appendChild(svg);
    wrap.appendChild(track);
  }
}

function renderTable(attacks) {
  const wrap = document.getElementById("table-wrap");
  wrap.innerHTML = "";
  if (!attacks || !attacks.length) {
    wrap.textContent = "(행 없음)";
    return;
  }
  const keys = Object.keys(attacks[0]);
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const trh = document.createElement("tr");
  for (const k of keys) {
    const th = document.createElement("th");
    th.textContent = k;
    trh.appendChild(th);
  }
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  for (const row of attacks) {
    const tr = document.createElement("tr");
    for (const k of keys) {
      const td = document.createElement("td");
      td.textContent = row[k] ?? "";
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  wrap.appendChild(table);
}

function applyResult(data) {
  lastPayload = data.json;
  lastMarkdown = data.markdown || "";
  document.getElementById("md-raw").textContent = lastMarkdown;
  renderTaePreview(data.json && data.json.tae);
  renderTable(data.json.attacks || []);
  document.getElementById("result").classList.remove("hidden");
  document.getElementById(
    "status"
  ).textContent = `완료 — ${data.rowCount}행`;
}

async function documentFromClient(form) {
  if (typeof Papa === "undefined") {
    throw new Error("PapaParse 로드 실패 — index.html의 스크립트를 확인하세요.");
  }
  const file = form.querySelector('input[name="atkparam"]').files[0];
  if (!file) throw new Error("CSV 파일을 선택하세요.");

  const text = await file.text();
  const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
  if (parsed.errors && parsed.errors.length) {
    throw new Error(`CSV 파싱: ${parsed.errors[0].message}`);
  }

  const bossKey = form.boss_key.value.trim() || "[Tree Sentinel]";
  const exclude = form.exclude.value.trim() || "";
  const title = form.title.value.trim() || "Boss";
  const attacks = loadRows(parsed.data, bossKey, exclude || null);

  let taeExtra = null;
  const taeFile = form.querySelector('input[name="tae_json"]').files[0];
  if (taeFile && taeFile.size) {
    const raw = await taeFile.text();
    taeExtra = JSON.parse(raw);
  }

  const meta = {
    title,
    generated: new Date().toISOString(),
    csv_path: file.name,
    include_key: bossKey,
    exclude_substr: exclude,
    asset_inventory: [],
    mode: "static",
  };

  const md = renderMarkdown(meta, attacks, [], taeExtra);
  const json = buildJsonPayload(meta, attacks, taeExtra);
  applyResult({
    ok: true,
    rowCount: attacks.length,
    markdown: md,
    json,
  });
}

async function documentFromApi(form) {
  const fd = new FormData(form);
  const tae = form.querySelector('input[name="tae_json"]').files[0];
  if (!tae || !tae.size) {
    fd.delete("tae_json");
  }

  const apiUrl = new URL("api/document", window.location.href).toString();
  const res = await fetch(apiUrl, { method: "POST", body: fd });
  const ct = res.headers.get("content-type") || "";
  if (!res.ok || !ct.includes("application/json")) {
    throw new Error("api");
  }
  const data = await res.json();
  if (!data.ok) throw new Error("응답 오류");
  applyResult(data);
}

document.getElementById("doc-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = document.getElementById("status");
  const result = document.getElementById("result");
  status.textContent = "처리 중…";
  status.classList.remove("error");
  result.classList.add("hidden");

  const form = e.target;
  try {
    try {
      await documentFromApi(form);
    } catch (_) {
      await documentFromClient(form);
    }
  } catch (err) {
    status.textContent = String(err.message || err);
    status.classList.add("error");
  }
});

document.getElementById("dl-md").addEventListener("click", () => {
  const title =
    (lastPayload && lastPayload.meta && lastPayload.meta.title) || "combat";
  downloadBlob(`${title}_combat.md`, "text/markdown;charset=utf-8", lastMarkdown);
});

document.getElementById("dl-json").addEventListener("click", () => {
  const title =
    (lastPayload && lastPayload.meta && lastPayload.meta.title) || "combat";
  downloadBlob(
    `${title}_combat.json`,
    "application/json;charset=utf-8",
    JSON.stringify(lastPayload, null, 2)
  );
});

document.getElementById("dl-csv").addEventListener("click", () => {
  const title =
    (lastPayload && lastPayload.meta && lastPayload.meta.title) || "combat";
  const csv = attacksToCsv((lastPayload && lastPayload.attacks) || []);
  downloadBlob(`${title}_combat.csv`, "text/csv;charset=utf-8", csv);
});

document.getElementById("dl-xlsx").addEventListener("click", () => {
  if (typeof XLSX === "undefined") {
    alert("SheetJS 로드 실패 — 네트워크·CDN 차단을 확인하세요.");
    return;
  }
  const title =
    (lastPayload && lastPayload.meta && lastPayload.meta.title) || "combat";
  const rows = (lastPayload && lastPayload.attacks) || [];
  const ws = XLSX.utils.json_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "attacks");
  XLSX.writeFile(wb, `${title}_combat.xlsx`);
});
