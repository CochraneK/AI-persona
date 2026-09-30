"""Local showcase server — real-time persona generation for the web page.

Pure standard library, zero dependencies. The showcase page (web/index.html)
stays a self-contained single file for double-click use; when it is served by
this server, its "live generation" section (伍 实时生成) calls /api/persona to
run the engine in real time — not limited to the pre-built 70-person pool.

Run (from anywhere):
    python scripts/serve_showcase.py            # http://127.0.0.1:8765/
    python scripts/serve_showcase.py --port 9000

Endpoints:
    GET /                 -> web/index.html
    GET /api/diagnoses    -> {"diagnoses": [10 中文名], "healthy": "无精神障碍（健康）"}
    GET /api/persona      -> ?diagnosis=<中文名>&seed=<可选 int>
                             Returns the pool card shape (same fields the page
                             renders) plus "system_prompt" (the assembled LLM
                             System Prompt, copy-paste ready). If seed is
                             omitted a random one is drawn and returned in the
                             payload so the result can be reproduced.
"""

import argparse
import json
import os
import random
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# --- Determinism guard (defense in depth) ------------------------------------
# The engine's sampling path is audited to be hash-independent (full rationale
# in scripts/make_full_pool.py). The guard is kept as belt-and-braces so live
# persona generation stays reproducible across server restarts (same diagnosis
# + seed -> same card) even if a future hash-ordered sampling path appears.
# Must run before make_showcase_pool is imported (it carries the same guard).
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import PersonaGenerator  # noqa: E402
from core import ontology_native_fill as ofill  # noqa: E402
# Reuse the pool builder's diagnosis list and card projection so the API
# response has EXACTLY the shape the page already renders (plus seed /
# diagnosis_key / system_prompt).
from make_showcase_pool import DIAGNOSES, HEALTHY, _fill_rng, _persona_to_card  # noqa: E402

WEB_DIR = os.path.join(_REPO, "web")
KNOWN = set(DIAGNOSES) | {HEALTHY}


def generate(diagnosis: str, seed: int) -> dict:
    gen = PersonaGenerator(rng_seed=seed)
    p = gen.generate(primary_diagnosis=diagnosis)
    card = _persona_to_card(p)
    card["seed"] = seed
    card["diagnosis_key"] = diagnosis
    # Same ontology-native 5-domain block as the pre-built pool cards,
    # sampled on the per-card RNG so the page renders live cards identically.
    card["ontology"] = ofill.sample_context_fields(
        ofill.persona_context(p), None, rng=_fill_rng(diagnosis, seed))
    card["system_prompt"] = p.system_prompt
    return card


class Handler(BaseHTTPRequestHandler):
    server_version = "AIPersonaShowcase/2.0"

    def log_message(self, fmt, *args):  # noqa: N802 - stdlib name
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body, ctype, binary=False):
        data = body if binary else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False),
                   "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802 - stdlib name
        u = urlparse(self.path)
        path = u.path
        if path in ("/", "/index.html"):
            try:
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                    data = f.read()
            except OSError:
                self._send(404, "index.html not found", "text/plain; charset=utf-8")
                return
            self._send(200, data, "text/html; charset=utf-8", binary=True)
        elif path == "/api/diagnoses":
            self._json(200, {"diagnoses": DIAGNOSES, "healthy": HEALTHY})
        elif path == "/api/persona":
            q = parse_qs(u.query)
            diag = (q.get("diagnosis") or [""])[0]
            if diag not in KNOWN:
                self._json(400, {"error": "unknown diagnosis",
                                 "known": sorted(KNOWN)})
                return
            seed_raw = (q.get("seed") or [""])[0].strip()
            if seed_raw:
                try:
                    seed = int(seed_raw)
                except ValueError:
                    self._json(400, {"error": "seed must be an integer"})
                    return
            else:
                seed = random.randint(0, 2 ** 31 - 1)
            if not (0 <= seed < 2 ** 31):
                self._json(400, {"error": "seed out of range"})
                return
            try:
                card = generate(diag, seed)
            except Exception as e:  # engine error -> readable 500
                self._json(500, {"error": str(e)})
                return
            self._json(200, card)
        else:
            self._send(404, "not found", "text/plain; charset=utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="AI-Persona showcase local server")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--bind", default="127.0.0.1",
                    help="bind address (default: localhost only)")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.bind, args.port), Handler)
    print(f"AI-Persona showcase server: http://{args.bind}:{args.port}/  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
