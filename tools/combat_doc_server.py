# -*- coding: utf-8 -*-
"""
로컬 웹 UI + API (1·2단계).

  pip install -r requirements-web.txt
  python tools/combat_doc_server.py

브라우저: http://127.0.0.1:8765/
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_ROOT = _TOOLS.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import combat_doc_export as cde  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

try:
    from fastapi import FastAPI, File, Form, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
except ImportError as e:
    print("FastAPI 미설치:", e, file=sys.stderr)
    print("실행: pip install -r requirements-web.txt", file=sys.stderr)
    raise SystemExit(1) from e

WEB = _ROOT / "web" / "combat_doc"
app = FastAPI(title="Combat Doc", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _inventory(asset_dir: str | None, chr_glob: str) -> list[str]:
    if not asset_dir or not str(asset_dir).strip():
        return []
    d = Path(asset_dir.strip())
    if not d.is_dir():
        return []
    pat = re.compile(chr_glob or r".*", re.I)
    return [cde.path_for_meta(p, _ROOT) for p in sorted(d.iterdir()) if pat.match(p.name)]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    p = WEB / "index.html"
    if not p.is_file():
        raise HTTPException(404, "web/combat_doc/index.html 없음")
    return p.read_text(encoding="utf-8")


@app.get("/app.js")
def app_js() -> FileResponse:
    return FileResponse(WEB / "app.js", media_type="application/javascript; charset=utf-8")


@app.get("/style.css")
def style_css() -> FileResponse:
    return FileResponse(WEB / "style.css", media_type="text/css; charset=utf-8")


@app.post("/api/document")
async def api_document(
    atkparam: UploadFile = File(..., description="AtkParam_Npc CSV"),
    boss_key: str = Form("[Tree Sentinel]"),
    exclude: str = Form("Draconic"),
    title: str = Form("Boss"),
    asset_dir: str = Form(""),
    chr_glob: str = Form(r"c3251.*"),
    tae_json: UploadFile | None = File(None),
) -> JSONResponse:
    if not atkparam.filename or not atkparam.filename.lower().endswith(".csv"):
        raise HTTPException(400, "atkparam CSV 파일을 올려 주세요.")

    suffix = Path(atkparam.filename).suffix or ".csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        content = await atkparam.read()
        tmp.write(content)

    try:
        ex = exclude.strip() if exclude else None
        attacks = cde.load_rows(tmp_path, boss_key, ex)
    finally:
        tmp_path.unlink(missing_ok=True)

    tae_extra: dict | None = None
    if tae_json and tae_json.filename:
        raw = await tae_json.read()
        try:
            tae_extra = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as err:
            raise HTTPException(400, f"TAE JSON 파싱 실패: {err}") from err

    inv = _inventory(asset_dir, chr_glob)
    meta = {
        "title": title.strip() or "Boss",
        "generated": datetime.now(timezone.utc).isoformat(),
        "csv_path": atkparam.filename,
        "include_key": boss_key,
        "exclude_substr": ex or "",
        "asset_inventory": inv,
    }
    md = cde.render_markdown(meta, attacks, inv, tae_extra)
    payload = cde.build_json_payload(meta, attacks, tae_extra)
    return JSONResponse(
        {
            "ok": True,
            "rowCount": len(attacks),
            "markdown": md,
            "json": payload,
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
