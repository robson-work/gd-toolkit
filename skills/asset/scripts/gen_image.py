#!/usr/bin/env python3
"""Generate final game image assets with OpenAI's GPT Image models (gd /asset).

No dependencies beyond Python 3 (urllib). The API key is never printed.

Commands:
  check                         find the key and show which model would be used (no cost)
  models                        list the GPT Image models this key can use, newest first
  generate --prompt P --out F   generate one image (PNG) at F
      [--size 1024x1024] [--quality high] [--background transparent|opaque|auto]
      [--model auto|<id>] [--prefer detail|fast] [--ref IMG ...] [--log LOG.jsonl]

--ref switches to the edits endpoint so the result matches existing art.
--model auto (default) picks the newest gpt-image model, version 2 or later,
preferring the detail variant (sunburst) for final assets, or the fast one
(flare) with --prefer fast; "mini" models are never auto-picked.

Key lookup order: $OPENAI_API_KEY, OPENAI_API_KEY in the game repo's .env.local
or .env (from the current folder up to the repo root), macOS Keychain item
"gd-toolkit-openai", ~/.config/gd-toolkit/openai_api_key. Run it from the game
repo. $OPENAI_BASE_URL overrides the API host.

Exit codes: 0 ok, 2 usage, 3 no API key, 4 API error, 5 no usable model.
"""
import argparse
import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

FALLBACK_MODEL = "gpt-image-2"
KEYCHAIN_SERVICE = "gd-toolkit-openai"
KEY_FILE = Path.home() / ".config" / "gd-toolkit" / "openai_api_key"
MODEL_RE = re.compile(r"^gpt-image-(\d+(?:\.\d+)*)(?:-([a-z0-9-]+))?$")
VARIANT_RANK = {"detail": {"sunburst": 3, None: 2, "flare": 1},
                "fast": {"flare": 3, None: 2, "sunburst": 1}}


def emit(obj) -> None:
    print(json.dumps(obj, indent=2))


def die(code: int, msg: str, **extra) -> None:
    print(msg, file=sys.stderr)
    if extra:
        emit(extra)
    sys.exit(code)


def base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


ENV_FILES = (".env.local", ".env")


def repo_root(start: Path) -> Path:
    """The nearest folder at or above start that holds .git, else start."""
    for d in (start, *start.parents):
        if (d / ".git").exists():
            return d
    return start


def read_env_file(path: Path):
    """The OPENAI_API_KEY value in a dotenv file, or None. Never prints it."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        line = line.strip()
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, sep, value = line.partition("=")
        if not sep or name.strip() != "OPENAI_API_KEY":
            continue
        value = value.strip()
        if value[:1] in ("'", '"') and value.count(value[0]) >= 2:
            value = value[1:value.index(value[0], 1)]
        else:
            value = value.split(" #", 1)[0].strip()
        return value or None
    return None


def env_file_tracked(path: Path) -> bool:
    """True if git tracks this file, which would mean the key is committed."""
    try:
        r = subprocess.run(["git", "-C", str(path.parent), "ls-files", "--error-unmatch", path.name],
                           capture_output=True, timeout=10)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def find_env_key():
    """(key, path) from the game repo's .env.local or .env, or (None, None)."""
    cwd = Path.cwd()
    root = repo_root(cwd)
    folders = [cwd] + [d for d in cwd.parents if d == root or root in d.parents]
    for d in folders:
        for name in ENV_FILES:
            p = d / name
            if p.is_file():
                key = read_env_file(p)
                if key:
                    return key, p
    return None, None


def find_key():
    """(key, source) or (None, None)."""
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"].strip(), "env OPENAI_API_KEY"
    key, path = find_env_key()
    if key:
        warn = " — WARNING: this file is tracked by git" if env_file_tracked(path) else ""
        return key, f"{path}{warn}"
    if sys.platform == "darwin":
        try:
            r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip(), f"macOS Keychain ({KEYCHAIN_SERVICE})"
        except (OSError, subprocess.TimeoutExpired):
            pass
    if KEY_FILE.is_file() and KEY_FILE.read_text().strip():
        return KEY_FILE.read_text().strip(), str(KEY_FILE)
    return None, None


def require_key() -> str:
    key, _ = find_key()
    if not key:
        die(3, "No OpenAI API key found. Set one up as described in the gd asset skill "
               f"(env OPENAI_API_KEY, OPENAI_API_KEY in the repo's .env.local or .env, "
               f"Keychain item '{KEYCHAIN_SERVICE}', or {KEY_FILE}).")
    return key


def request(method, path, key, body=None, content_type=None, timeout=300):
    req = urllib.request.Request(base_url() + path, data=body, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw).get("error", {}).get("message", raw)
        except ValueError:
            msg = raw
        raise ApiError(e.code, msg) from None
    except urllib.error.URLError as e:
        raise ApiError(0, f"network error: {e.reason}") from None


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status, self.message = status, message


def parse_model(mid):
    m = MODEL_RE.match(mid)
    if not m:
        return None
    version = tuple(int(x) for x in m.group(1).split("."))
    variant = m.group(2)
    if version < (2,) or (variant and "mini" in variant):
        return None
    return version, variant


def rank_models(ids, prefer="detail"):
    ranks = VARIANT_RANK[prefer]
    usable = [(parse_model(i), i) for i in ids]
    usable = [(p, i) for p, i in usable if p]
    usable.sort(key=lambda t: (t[0][0], ranks.get(t[0][1], 0)), reverse=True)
    return [i for _, i in usable]


def list_image_models(key):
    data = request("GET", "/models", key, timeout=30)
    return [m["id"] for m in data.get("data", []) if str(m.get("id", "")).startswith("gpt-image")]


def resolve_model(key, model, prefer):
    if model and model != "auto":
        return model, "pinned"
    try:
        ranked = rank_models(list_image_models(key), prefer)
    except ApiError as e:
        print(f"could not list models ({e.message}); falling back to {FALLBACK_MODEL}", file=sys.stderr)
        return FALLBACK_MODEL, "fallback"
    if not ranked:
        die(5, "this key can't use any gpt-image model of version 2 or later "
               "(check organization verification and model access on platform.openai.com)")
    return ranked[0], "auto"


def multipart(fields, files):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, path in files:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; '
                     f'filename="{path.name}"\r\nContent-Type: {mime}\r\n\r\n'.encode())
        parts.append(path.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def call_images(key, params, refs):
    if refs:
        body, ctype = multipart({k: v for k, v in params.items()}, [("image[]", r) for r in refs])
        return request("POST", "/images/edits", key, body, ctype)
    return request("POST", "/images/generations", key, json.dumps(params).encode(), "application/json")


def cmd_check(_a):
    key, source = find_key()
    if not key:
        emit({"key": None, "ready": False})
        sys.exit(3)
    try:
        ranked = rank_models(list_image_models(key))
    except ApiError as e:
        emit({"key": source, "ready": False, "error": e.message, "status": e.status})
        sys.exit(4)
    emit({"key": source, "ready": bool(ranked), "model": ranked[0] if ranked else None,
          "fast_model": (rank_models(ranked, "fast") or [None])[0]})
    sys.exit(0 if ranked else 5)


def cmd_models(_a):
    key = require_key()
    try:
        ids = list_image_models(key)
    except ApiError as e:
        die(4, f"API error {e.status}: {e.message}")
    emit({"usable_newest_first": rank_models(ids), "all_gpt_image": sorted(ids)})


def cmd_generate(a):
    key = require_key()
    refs = [Path(r) for r in a.ref or []]
    for r in refs:
        if not r.is_file():
            die(2, f"reference image not found: {r}")
    model, how = resolve_model(key, a.model, a.prefer)
    params = {"model": model, "prompt": a.prompt, "size": a.size, "quality": a.quality,
              "output_format": "png", "n": 1}
    if a.background != "auto":
        params["background"] = a.background
    notes = []
    try:
        resp = call_images(key, params, refs)
    except ApiError as e:
        if "background" in params and e.status == 400 and "background" in e.message.lower():
            notes.append(f"{model} rejected background={a.background}; generated opaque instead")
            params.pop("background")
            try:
                resp = call_images(key, params, refs)
            except ApiError as e2:
                die(4, f"API error {e2.status}: {e2.message}")
        else:
            die(4, f"API error {e.status}: {e.message}")
    item = (resp.get("data") or [{}])[0]
    if not item.get("b64_json"):
        die(4, "API returned no image data", response_keys=list(resp))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(item["b64_json"]))
    record = {"when": datetime.now().replace(microsecond=0).isoformat(), "out": str(out),
              "model": model, "model_choice": how, "prompt": a.prompt, "size": a.size,
              "quality": a.quality, "background": params.get("background", "auto"),
              "refs": [str(r) for r in refs], "revised_prompt": item.get("revised_prompt"),
              "notes": notes}
    if a.log:
        log = Path(a.log)
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    emit(record)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("models")
    g = sub.add_parser("generate")
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--size", default="1024x1024")
    g.add_argument("--quality", default="high")
    g.add_argument("--background", default="auto", choices=["auto", "transparent", "opaque"])
    g.add_argument("--model", default="auto")
    g.add_argument("--prefer", default="detail", choices=["detail", "fast"])
    g.add_argument("--ref", nargs="*")
    g.add_argument("--log")
    a = p.parse_args()
    {"check": cmd_check, "models": cmd_models, "generate": cmd_generate}[a.cmd](a)


if __name__ == "__main__":
    main()
