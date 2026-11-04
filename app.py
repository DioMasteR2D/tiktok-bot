import os
import sqlite3
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Flask, abort, flash, g, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
DATABASE = os.environ.get("DATABASE_PATH", "/var/data/tiktok_dashboard.db")
if os.environ.get("RENDER") != "true" and DATABASE.startswith("/var/data/"):
    DATABASE = os.environ.get("DATABASE_PATH", "tiktok_dashboard.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 url TEXT NOT NULL,
 title TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metrics (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
 followers INTEGER NOT NULL DEFAULT 0,
 views INTEGER NOT NULL DEFAULT 0,
 likes INTEGER NOT NULL DEFAULT 0,
 comments INTEGER NOT NULL DEFAULT 0,
 shares INTEGER NOT NULL DEFAULT 0,
 recorded_at TEXT NOT NULL
);
"""

BASE = """
<!doctype html><html lang="el"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · DioMasteR2D TikTok Desk</title>
<style>
:root{color-scheme:dark;--bg:#0b1020;--panel:#151d32;--muted:#9eabc5;--line:#293550;--accent:#62e6b5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#f4f7ff;font:15px system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1050px;margin:32px auto;padding:0 16px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:22px}
h1{font-size:25px;margin:0}h2{font-size:18px;margin:0 0 14px}.muted{color:var(--muted)}.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px}.stat{background:#0f172a;border:1px solid var(--line);padding:15px;border-radius:12px}.stat b{font-size:24px;display:block;margin-top:5px}
input,button{font:inherit;border-radius:9px;padding:11px 12px}input{width:100%;background:#0b1325;color:white;border:1px solid var(--line);margin:5px 0 12px}
button,.btn{background:var(--accent);color:#07140f;border:0;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block;padding:10px 14px;border-radius:9px}
.secondary{background:#26344f;color:#fff}.danger{background:#512b3b;color:#fff}label{display:block;color:var(--muted);font-size:13px}
form.inline{display:inline}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:12px}
a{color:var(--accent);overflow-wrap:anywhere}.notice{padding:12px;border-radius:9px;background:#23344a;margin:10px 0}.flash{padding:10px;border-radius:8px;background:#234333;margin:8px 0}
.actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.small{font-size:12px}
@media(max-width:600px){main{margin:18px auto}.panel{padding:14px}table{font-size:13px}}
</style></head><body><main>
<div class="top"><div><div class="muted small">DioMasteR2D</div><h1>TikTok Desk</h1></div>
{% if session.get('logged_in') %}<a class="btn secondary" href="{{ url_for('logout') }}">Αποσύνδεση</a>{% endif %}</div>
{% for message in get_flashed_messages() %}<div class="flash">{{ message }}</div>{% endfor %}
{{ body|safe }}
<p class="muted small">Εργαλείο οργάνωσης περιεχομένου και χειροκίνητης καταγραφής στατιστικών. Δεν εκτελεί αγορές followers, likes ή views.</p>
</main></body></html>
"""

LOGIN = """
<div class="panel" style="max-width:440px;margin:50px auto"><h2>Σύνδεση</h2>
{% if not configured %}<div class="notice">Δεν έχει οριστεί ακόμη το DASHBOARD_PASSWORD στο περιβάλλον του server.</div>{% endif %}
<form method="post"><input type="hidden" name="csrf" value="{{ csrf }}">
<label>Κωδικός πρόσβασης</label><input type="password" name="password" required autocomplete="current-password">
<button {% if not configured %}disabled{% endif %}>Είσοδος</button></form></div>
"""

DASH = """
<div class="grid">
 <div class="stat"><span class="muted">Βίντεο</span><b>{{ posts|length }}</b></div>
 <div class="stat"><span class="muted">Σύνολο προβολών*</span><b>{{ totals.views }}</b></div>
 <div class="stat"><span class="muted">Σύνολο likes*</span><b>{{ totals.likes }}</b></div>
 <div class="stat"><span class="muted">Followers τελευταίας καταγραφής*</span><b>{{ totals.followers }}</b></div>
</div>
<div class="panel"><h2>Προσθήκη βίντεο</h2><form method="post" action="{{ url_for('add_post') }}">
<input type="hidden" name="csrf" value="{{ csrf }}"><label>Σύνδεσμος TikTok βίντεο</label><input name="url" type="url" placeholder="https://www.tiktok.com/@..." required>
<label>Τίτλος / σημείωση</label><input name="title" maxlength="160" placeholder="π.χ. Νέα προσφορά / βίντεο σούβλας">
<button>Προσθήκη βίντεο</button></form></div>
<div class="panel"><h2>Τα βίντεό σου</h2>
{% if posts %}<table><thead><tr><th>Βίντεο</th><th>Τελευταία στοιχεία</th><th>Ενέργεια</th></tr></thead><tbody>
{% for p in posts %}<tr><td><b>{{ p.title or 'Χωρίς τίτλο' }}</b><br><a href="{{ p.url }}" target="_blank" rel="noopener">Άνοιγμα στο TikTok ↗</a><br><span class="muted small">{{ p.created_at }}</span></td>
<td>{% if p.last %}Views: {{ p.last.views }} · Likes: {{ p.last.likes }}<br>Comments: {{ p.last.comments }} · Shares: {{ p.last.shares }}<br>Followers: {{ p.last.followers }}<br><span class="muted small">{{ p.last.recorded_at }}</span>{% else %}<span class="muted">Δεν υπάρχουν στοιχεία ακόμη</span>{% endif %}</td>
<td><div class="actions"><a class="btn secondary" href="{{ url_for('post_detail',post_id=p.id) }}">Στατιστικά</a>
<form class="inline" method="post" action="{{ url_for('delete_post',post_id=p.id) }}" onsubmit="return confirm('Να διαγραφεί το βίντεο και το ιστορικό του;')"><input type="hidden" name="csrf" value="{{ csrf }}"><button class="danger">Διαγραφή</button></form></div></td></tr>{% endfor %}
</tbody></table>{% else %}<p class="muted">Δεν έχεις προσθέσει ακόμη βίντεο.</p>{% endif %}</div>
<p class="muted small">*Τα συνολικά views και likes αθροίζουν την τελευταία καταγραφή κάθε βίντεο. Τα στοιχεία εισάγονται χειροκίνητα.</p>
"""

DETAIL = """
<div class="panel"><a href="{{ url_for('index') }}">← Πίσω</a><h2 style="margin-top:14px">{{ post.title or 'Βίντεο TikTok' }}</h2><a href="{{ post.url }}" target="_blank" rel="noopener">{{ post.url }}</a></div>
<div class="panel"><h2>Νέα καταγραφή στατιστικών</h2><form method="post"><input type="hidden" name="csrf" value="{{ csrf }}">
<div class="grid">{% for field,label in fields %}<div><label>{{ label }}</label><input type="number" min="0" max="1000000000" step="1" name="{{ field }}" value="{{ latest[field] if latest else 0 }}" required></div>{% endfor %}</div>
<button>Αποθήκευση καταγραφής</button></form></div>
<div class="panel"><h2>Ιστορικό</h2>{% if history %}<table><thead><tr><th>Ημερομηνία</th><th>Followers</th><th>Views</th><th>Likes</th><th>Comments</th><th>Shares</th></tr></thead><tbody>
{% for m in history %}<tr><td>{{ m.recorded_at }}</td><td>{{ m.followers }}</td><td>{{ m.views }}</td><td>{{ m.likes }}</td><td>{{ m.comments }}</td><td>{{ m.shares }}</td></tr>{% endfor %}
</tbody></table>{% else %}<p class="muted">Δεν έχει γίνει καταγραφή.</p>{% endif %}</div>
"""

def db():
    if "db" not in g:
        folder = os.path.dirname(DATABASE)
        if folder:
            os.makedirs(folder, exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.executescript(SCHEMA)
        g.db.commit()
    return g.db

@app.teardown_appcontext
def close_db(_error):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]

def check_csrf():
    if not secrets.compare_digest(request.form.get("csrf", ""), session.get("csrf", "")):
        abort(400, "Invalid form token")

@app.before_request
def protect():
    if request.endpoint in ("login", "health", "static"):
        return
    if not session.get("logged_in"):
        return redirect(url_for("login", next=request.path))

@app.get("/health")
def health():
    return {"status": "ok", "app": "DioMasteR2D TikTok Desk"}

@app.route("/login", methods=["GET", "POST"])
def login():
    configured = bool(os.environ.get("DASHBOARD_PASSWORD"))
    if request.method == "POST":
        check_csrf()
        password = os.environ.get("DASHBOARD_PASSWORD", "")
        if configured and secrets.compare_digest(request.form.get("password", ""), password):
            session.clear()
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("Λάθος κωδικός ή δεν έχει ρυθμιστεί ο κωδικός στον server.")
    body = render_template_string(LOGIN, configured=configured, csrf=csrf_token())
    return render_template_string(BASE, title="Σύνδεση", body=body)

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/")
def index():
    rows = db().execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    posts = []
    totals = {"views": 0, "likes": 0, "followers": 0}
    for row in rows:
        p = dict(row)
        last = db().execute("SELECT * FROM metrics WHERE post_id=? ORDER BY id DESC LIMIT 1", (p["id"],)).fetchone()
        p["last"] = dict(last) if last else None
        if last:
            for k in totals:
                totals[k] += last[k]
        posts.append(p)
    body = render_template_string(DASH, posts=posts, totals=totals, csrf=csrf_token())
    return render_template_string(BASE, title="Πίνακας", body=body)

@app.post("/posts")
def add_post():
    check_csrf()
    url = request.form.get("url", "").strip()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (host == "tiktok.com" or host.endswith(".tiktok.com")):
        abort(400, "Χρειάζεται έγκυρος σύνδεσμος https://www.tiktok.com/...")
    db().execute("INSERT INTO posts(url,title,created_at) VALUES(?,?,?)",
                 (url, request.form.get("title", "").strip()[:160], datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    db().commit()
    flash("Το βίντεο προστέθηκε.")
    return redirect(url_for("index"))

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    post = db().execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        abort(404)
    fields = [("followers","Followers"),("views","Views"),("likes","Likes"),("comments","Comments"),("shares","Shares")]
    if request.method == "POST":
        check_csrf()
        values = []
        for key, _ in fields:
            try:
                value = int(request.form.get(key, ""))
            except ValueError:
                abort(400, "Τα στατιστικά πρέπει να είναι ακέραιοι αριθμοί.")
            if value < 0 or value > 1_000_000_000:
                abort(400, "Μη έγκυρη τιμή στατιστικών.")
            values.append(value)
        db().execute("INSERT INTO metrics(post_id,followers,views,likes,comments,shares,recorded_at) VALUES(?,?,?,?,?,?,?)",
                     (post_id, *values, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
        db().commit()
        flash("Τα στατιστικά αποθηκεύτηκαν.")
        return redirect(url_for("post_detail", post_id=post_id))
    latest = db().execute("SELECT * FROM metrics WHERE post_id=? ORDER BY id DESC LIMIT 1", (post_id,)).fetchone()
    history = db().execute("SELECT * FROM metrics WHERE post_id=? ORDER BY id DESC LIMIT 100", (post_id,)).fetchall()
    body = render_template_string(DETAIL, post=post, fields=fields, latest=latest, history=history, csrf=csrf_token())
    return render_template_string(BASE, title="Στατιστικά", body=body)

@app.post("/post/<int:post_id>/delete")
def delete_post(post_id):
    check_csrf()
    db().execute("DELETE FROM posts WHERE id=?", (post_id,))
    db().commit()
    flash("Το βίντεο και το ιστορικό του διαγράφηκαν.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
