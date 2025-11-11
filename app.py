import os
import sqlite3
import threading
import time
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

DB = "tasks.db"

# ---------------- Database helpers ----------------

def get_db_connection():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.executescript("""
    DROP TABLE IF EXISTS tasks;
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        is_done INTEGER DEFAULT 0,
        parent_id INTEGER,
        category TEXT,
        is_today INTEGER DEFAULT 0,
        position INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES tasks(id)
    );
    CREATE INDEX IF NOT EXISTS idx_parent ON tasks(parent_id);
    CREATE INDEX IF NOT EXISTS idx_category ON tasks(category);
    CREATE INDEX IF NOT EXISTS idx_today ON tasks(is_today);
    """)
    conn.commit()
    conn.close()

def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    # sqlite returns integers; normalize booleans to 0/1
    d['is_done'] = int(d.get('is_done') or 0)
    d['is_today'] = int(d.get('is_today') or 0)
    return d

# Recursive fetch for rendering
def get_subtasks(parent_id=None):
    conn = get_db_connection()
    if parent_id is None:
        rows = conn.execute("SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY position, id").fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE parent_id = ? ORDER BY position, id", (parent_id,)).fetchall()
    tasks = []
    for r in rows:
        task = row_to_dict(r)
        task['children'] = get_subtasks(task['id'])
        tasks.append(task)
    conn.close()
    return tasks

# Immediate children only (for detail pane)
def get_children(parent_id):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE parent_id = ? ORDER BY position, id", (parent_id,)).fetchall()
    children = [row_to_dict(r) for r in rows]
    conn.close()
    return children

# Recursive progress calculation
def compute_progress(task_id):
    conn = get_db_connection()
    children = conn.execute("SELECT id FROM tasks WHERE parent_id = ?", (task_id,)).fetchall()
    if not children:
        row = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if row is None:
            return {"done": 0, "total": 0, "percent": 0}
        return {"done": int(row["is_done"]), "total": 1, "percent": 100 if int(row["is_done"]) else 0}
    # accumulate child progress
    total_percent = 0
    total_count = 0
    for c in children:
        p = compute_progress(c["id"])
        # treat leaf as total 1; use percent
        total_percent += p["percent"]
        total_count += 1
    conn.close()
    percent = int(total_percent / total_count) if total_count else 0
    return {"done": None, "total": total_count, "percent": percent}

# Recursive delete
def delete_recursive(conn, task_id):
    subs = conn.execute("SELECT id FROM tasks WHERE parent_id = ?", (task_id,)).fetchall()
    for s in subs:
        delete_recursive(conn, s["id"])
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

# ---------------- Routes / API ----------------

@app.route("/")
def index():
    # render main page with the whole tree for initial load
    tasks = get_subtasks()
    # fetch distinct categories for sidebar
    conn = get_db_connection()
    cats = [r[0] for r in conn.execute("SELECT DISTINCT category FROM tasks WHERE category IS NOT NULL").fetchall()]
    conn.close()
    return render_template("index.html", tasks=tasks, categories=cats)

# API: get single task (with immediate children and progress)
@app.route("/api/task/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404
    task = row_to_dict(row)
    task["children"] = get_children(task_id)
    task["progress"] = compute_progress(task_id)
    conn.close()
    return jsonify(task)

# API: update description
@app.route("/api/task/<int:task_id>/description", methods=["POST"])
def api_update_description(task_id):
    data = request.get_json() or request.form
    desc = data.get("description", "")
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (desc, task_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# API: update title
@app.route("/api/task/<int:task_id>/title", methods=["POST"])
def api_update_title(task_id):
    data = request.get_json() or request.form
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"ok": False, "error": "empty title"}), 400
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, task_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# API: toggle done
@app.route("/api/task/<int:task_id>/toggle", methods=["POST"])
def api_toggle(task_id):
    conn = get_db_connection()
    row = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"ok": False}), 404
    new = 0 if int(row["is_done"]) else 1
    if new:
        conn.execute("UPDATE tasks SET is_done = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
    else:
        conn.execute("UPDATE tasks SET is_done = 0, completed_at = NULL WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "is_done": new})

# API: toggle is_today
@app.route("/api/task/<int:task_id>/today", methods=["POST"])
def api_toggle_today(task_id):
    data = request.get_json() or request.form
    val = data.get("is_today")
    if val is None:
        return jsonify({"ok": False, "error": "missing is_today"}), 400
    val = 1 if int(val) else 0
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET is_today = ? WHERE id = ?", (val, task_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "is_today": val})

# API: add task (general; supports parent_id)
@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json() or request.form
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"ok": False, "error": "empty title"}), 400
    parent = data.get("parent_id")
    category = data.get("category")
    is_today = int(data.get("is_today") or 0)
    conn = get_db_connection()
    if parent:
        conn.execute("INSERT INTO tasks (title, parent_id, category, is_today) VALUES (?, ?, ?, ?)",
                     (title, parent, category, is_today))
    else:
        conn.execute("INSERT INTO tasks (title, category, is_today) VALUES (?, ?, ?)",
                     (title, category, is_today))
    conn.commit()
    last = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.close()
    return jsonify({"ok": True, "id": last})

# API: delete (recursive)
@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.get_json() or request.form
    tid = data.get("id")
    if not tid:
        return jsonify({"ok": False, "error": "missing id"}), 400
    conn = get_db_connection()
    delete_recursive(conn, int(tid))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# simple helper endpoints for sidebar filters
@app.route("/api/list/<string:list_name>", methods=["GET"])
def api_list_filter(list_name):
    conn = get_db_connection()
    if list_name == "all":
        rows = conn.execute("SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY position, id").fetchall()
    elif list_name == "myday":
        rows = conn.execute("SELECT * FROM tasks WHERE is_today = 1 AND parent_id IS NULL ORDER BY position, id").fetchall()
    elif list_name == "inbox":
        rows = conn.execute("SELECT * FROM tasks WHERE (category IS NULL OR category = '') AND parent_id IS NULL ORDER BY position, id").fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE category = ? AND parent_id IS NULL ORDER BY position, id", (list_name,)).fetchall()
    tasks = []
    for r in rows:
        task = row_to_dict(r)
        task['children'] = get_subtasks(task['id'])
        tasks.append(task)
    conn.close()
    return jsonify({"tasks": tasks})

# ---------------- Background reset thread ----------------

def midnight_reset_thread():
    # runs continuously. When date flips, clear is_today.
    last_date = date.today()
    while True:
        now = datetime.now()
        if date.today() != last_date:
            # day changed -> clear is_today
            try:
                conn = get_db_connection()
                conn.execute("UPDATE tasks SET is_today = 0 WHERE is_today = 1")
                conn.commit()
                conn.close()
                last_date = date.today()
                print("[midnight_reset] cleared is_today flags for new day.")
            except Exception as e:
                print("Error in midnight reset:", e)
        # sleep 60 seconds to check again
        time.sleep(60)

def start_background_thread():
    thread = threading.Thread(target=midnight_reset_thread, daemon=True)
    thread.start()

# start background thread only once when app runs for real
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or __name__ == "__main__":
    # if DB missing, initialize schema
    if not os.path.exists(DB):
        init_db()
    start_background_thread()

# ---------------- Run server ----------------
# keep the module usable for flask run
if __name__ == "__main__":
    app.run(debug=True)
