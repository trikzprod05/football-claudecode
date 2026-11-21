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
        subprocess.run(["python3","scripts/trends.py","--query",q,"--hours","0","--limit","50"], cwd=ROOT, check=True, timeout=300)
        # parse top trending video URL from trends.md
        import re
        trends_path = os.path.join(ROOT, "trends.md")
        url = None
        if os.path.exists(trends_path):
            with open(trends_path) as f:
                content = f.read()
            # find any youtube URL
            m = re.search(r'https?://www\.youtube\.com/watch\?v=[\w-]+', content)
            if m:
                url = m.group(0)
            else:
                # fallback: any https URL
                m = re.search(r'https?://[^\s)]+', content)
                if m:
                    url = m.group(0)
        if url:
            subprocess.run(["python3","scripts/moments.py",url,"--top","3"], cwd=ROOT, check=True, timeout=600)
            # find the job dir
            import glob as g
            job_dirs = sorted(g.glob(os.path.join(ROOT, "jobs", "*")), key=os.path.getmtime, reverse=True)
            if job_dirs:
                subprocess.run(["python3","scripts/cut.py", job_dirs[0], "--pick", "1", "--layout", "blur"], cwd=ROOT, check=True, timeout=600)
            return jsonify({"ok": True, "msg": "Clip created from top trending video!"})
        debug = ""
        if os.path.exists(trends_path):
            with open(trends_path) as f:
                debug = f.read()[:300]
        return jsonify({"ok": False, "msg": "No URL. trends.md: " + debug})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

@app.route("/api/videos")
def api_videos():
    exts = {".mp4",".webm",".mov",".mkv"}
    files = [f for f in os.listdir(ROOT) if os.path.splitext(f)[1].lower() in exts]
    return jsonify({"videos": sorted(files)})
def files(filename):
    return send_from_directory(ROOT, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))