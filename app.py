from flask import Flask, request, jsonify, send_from_directory
import os, subprocess, requests

app = Flask(__name__, static_folder=".")
ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.json or {}
    fb = data.get("fb","").strip()
    if not fb:
        return jsonify({"ok": False, "msg": "Missing token"})
    r = requests.get("https://graph.facebook.com/v19.0/me", params={"access_token": fb}, timeout=15)
    return jsonify({"ok": r.ok, "msg": r.text[:200]})

@app.route("/post", methods=["POST"])
def post():
    data = request.json or {}
    token = data.get("fb","").strip()
    page_id = data.get("page_id","").strip()
    file = data.get("file","").strip()
    path = os.path.join(ROOT, file)
    if not (token and page_id and os.path.exists(path)):
        return jsonify({"ok": False, "msg": "Missing token/page/file"})
    with open(path, "rb") as f:
        r = requests.post(
            f"https://graph.facebook.com/v19.0/{page_id}/videos",
            data={"access_token": token, "description": data.get("desc","")},
            files={"source": f},
            timeout=300,
        )
    return jsonify({"ok": r.ok, "msg": r.text[:300]})

@app.route("/create", methods=["POST"])
def create():
    data = request.json or {}
    q = data.get("query","Football").strip() or "Football"
    try:
        subprocess.run(["python3","scripts/trends.py","--query",q,"--hours","24"], cwd=ROOT, check=True, timeout=300)
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})
    return jsonify({"ok": True, "msg": "Trends updated; run moments/cut next"})

@app.route("/api/videos")
def api_videos():
    exts = {".mp4",".webm",".mov",".mkv"}
    files = [f for f in os.listdir(ROOT) if os.path.splitext(f)[1].lower() in exts]
    return jsonify({"videos": sorted(files)})
def files(filename):
    return send_from_directory(ROOT, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))