from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- Database Helpers ----------

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_subtasks(parent_id=None):
    """Fetch tasks recursively."""
    conn = get_db_connection()
    if parent_id is None:
        rows = conn.execute("SELECT * FROM tasks WHERE parent_id IS NULL ORDER BY id DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE parent_id = ? ORDER BY id DESC", (parent_id,)).fetchall()
    conn.close()

    tasks = []
    for row in rows:
        task = dict(row)
        task["children"] = get_subtasks(task["id"])
        tasks.append(task)
    return tasks


# ---------- Routes ----------

@app.route("/")
def index():
    tasks = get_subtasks()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    parent_id = request.form.get("parent_id")

    if not title.strip():
        return redirect("/")

    conn = get_db_connection()
    if parent_id:
        conn.execute("INSERT INTO tasks (title, parent_id) VALUES (?, ?)", (title, parent_id))
    else:
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/toggle/<int:task_id>")
def toggle(task_id):
    conn = get_db_connection()
    cur = conn.execute("SELECT is_done FROM tasks WHERE id = ?", (task_id,))
    current = cur.fetchone()["is_done"]
    new_status = 0 if current else 1
    conn.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_db_connection()
    delete_recursive(conn, task_id)
    conn.commit()
    conn.close()
    return redirect("/")


def delete_recursive(conn, task_id):
    """Recursively delete a task and its subtasks."""
    subs = conn.execute("SELECT id FROM tasks WHERE parent_id = ?", (task_id,)).fetchall()
    for sub in subs:
        delete_recursive(conn, sub["id"])
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


# ---------- Run ----------

if __name__ == "__main__":
    app.run(debug=True)
