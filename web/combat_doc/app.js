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
