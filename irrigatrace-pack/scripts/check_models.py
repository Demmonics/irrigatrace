"""Prints readiness of local models. Always exits 0; the app must degrade gracefully if models are missing."""
import json, sys, urllib.request
WANT = sys.argv[1:] or ["qwen3:4b", "nomic-embed-text"]
try:
    tags = json.load(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3))
    have = {m["name"] for m in tags.get("models", [])}
except Exception as e:
    print(json.dumps({"ollama": "down", "error": str(e)})); sys.exit(0)
ok = lambda w: any(h == w or h == w + ":latest" for h in have)
print(json.dumps({"ollama": "up", "models": {w: ok(w) for w in WANT}}, indent=2))
