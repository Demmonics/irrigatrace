"""
Smoke test for IrrigaTrace services: Qdrant, Gemini, and Ollama.
Obey invariant 9: NEVER print, log, or leak secret keys.
"""
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

def parse_env_file(path):
    env_vars = {}
    if not path.exists():
        return env_vars
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                env_vars[k] = v
    return env_vars

def check_gemini(api_key):
    if not api_key or api_key.startswith("your-"):
        return {"status": "unconfigured", "error": "Missing GEMINI_API_KEY"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "IrrigaTrace-SmokeTest/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", [])]
            return {"status": "ok", "model_count": len(models)}
    except urllib.error.HTTPError as e:
        return {"status": "fail", "error_class": f"HTTPError {e.code}"}
    except Exception as e:
        return {"status": "fail", "error_class": type(e).__name__}

def check_qdrant(url, api_key):
    if not url or url.startswith("your-"):
        return {"status": "unconfigured", "error": "Missing QDRANT_URL"}
    target = url.rstrip("/") + "/collections"
    headers = {"User-Agent": "IrrigaTrace-SmokeTest/1.0"}
    if api_key:
        headers["api-key"] = api_key
    try:
        req = urllib.request.Request(target, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"status": "ok", "collections": data.get("result", {}).get("collections", [])}
    except urllib.error.HTTPError as e:
        return {"status": "fail", "error_class": f"HTTPError {e.code}"}
    except Exception as e:
        return {"status": "fail", "error_class": type(e).__name__}

def check_ollama(host="http://localhost:11434"):
    url = f"{host.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "IrrigaTrace-SmokeTest/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", [])]
            return {"status": "ok", "models": models}
    except Exception as e:
        return {"status": "fail", "error_class": type(e).__name__}

def main():
    root = Path(__file__).resolve().parent.parent
    env_vars = parse_env_file(root / ".env")
    for k, v in env_vars.items():
        if k not in os.environ:
            os.environ[k] = v

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    qdrant_url = os.environ.get("QDRANT_URL", "")
    qdrant_key = os.environ.get("QDRANT_API_KEY", "")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    results = {
        "gemini": check_gemini(gemini_key),
        "qdrant": check_qdrant(qdrant_url, qdrant_key),
        "ollama": check_ollama(ollama_host)
    }

    print(json.dumps(results, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
