Here’s a **complete project layout plan** in Markdown for your CS50 final project — the **Nested To-Do List App**.
This defines every component before coding so you’ll know exactly what to build.

---

````markdown
# Nested To-Do List App – Project Plan

## 1. Overview
A hierarchical to-do list web app where tasks can contain subtasks infinitely.  
Users can break down goals into smaller steps recursively, helping manage projects or personal goals with clear structure.

---

## 2. Core Concept
Each task has:
- a unique `id`
- a `title`
- a completion status
- a reference to its parent task (`parent_id`)

Tasks without a parent (`parent_id = NULL`) are top-level.  
This structure forms a tree that can expand indefinitely.

---

## 3. Goals
### Must-Have (MVP)
- Add new tasks
- Add subtasks to any task
- Mark tasks complete/incomplete
- Delete tasks (with all nested subtasks)
- Display tasks in a nested, indented structure

### Nice-to-Have (Optional)
- Collapse/expand subtasks
- Progress bar showing % complete
- Edit task titles
- Sort tasks alphabetically or by status
- Save timestamps (created_at, completed_at)
- Minimal dark/light theme

---

## 4. Stack
| Layer | Tool |
|-------|------|
| Backend | Flask (Python) |
| Database | SQLite |
| Frontend | HTML, CSS, Jinja2 templates, JavaScript (optional for expand/collapse) |
| Deployment | Local (CS50 Codespace) or GitHub Pages (static) |

---

## 5. Database Schema
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    is_done BOOLEAN DEFAULT 0,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES tasks(id)
);
````

---

## 6. File Structure

```
project/
│
├── app.py
├── tasks.db
├── templates/
│   ├── layout.html        # Base layout
│   ├── index.html         # Main view for tasks
│   └── tasks.html         # Recursive sub-template for nested rendering
├── static/
│   └── styles.css         # Styling (simple, readable)
├── requirements.txt
└── README.md
```

---

## 7. Routes

| Route          | Method          | Description                    |
| -------------- | --------------- | ------------------------------ |
| `/`            | GET             | Display all tasks recursively  |
| `/add`         | POST            | Add a new task or subtask      |
| `/toggle/<id>` | POST            | Mark task complete/incomplete  |
| `/delete/<id>` | POST            | Delete task (and all subtasks) |
| `/edit/<id>`   | POST (optional) | Edit task title                |

---

## 8. Backend Logic

### Recursive Fetch

```python
def get_subtasks(task_id):
    subtasks = db.execute("SELECT * FROM tasks WHERE parent_id = ?", task_id)
    for sub in subtasks:
        sub["children"] = get_subtasks(sub["id"])
    return subtasks
```

### Recursive Delete

```python
def delete_task(task_id):
    subtasks = db.execute("SELECT id FROM tasks WHERE parent_id = ?", task_id)
    for sub in subtasks:
        delete_task(sub["id"])
    db.execute("DELETE FROM tasks WHERE id = ?", task_id)
```

---

## 9. UI Layout

### Home Page

```
+-------------------------------------------+
| Nested To-Do List                         |
|-------------------------------------------|
| [Add new task] [Submit]                   |
|                                           |
| - Study AI                                |
|     - Finish CS50 Project                 |
|         - Write README                    |
|         - Record Video                    |
|     - Revise notes                        |
| - Workout                                 |
|     - Upper body                          |
|     - Lower body                          |
|-------------------------------------------|
| (✓) toggle | (+) add subtask | (x) delete |
+-------------------------------------------+
```

### Visual Indicators

* Indentation = depth of nesting
* Completed tasks = faded/strikethrough
* Buttons for subtask, delete, toggle

---

## 10. Implementation Plan

| Step | Task            | Description                                       |
| ---- | --------------- | ------------------------------------------------- |
| 1    | Setup Flask app | Create virtual env, install Flask, connect SQLite |
| 2    | Database        | Initialize schema with `schema.sql`               |
| 3    | Basic CRUD      | Add, view, delete, toggle tasks                   |
| 4    | Recursion       | Render nested subtasks                            |
| 5    | Styling         | Add simple CSS for indentation and buttons        |
| 6    | Testing         | Verify recursion and deletes                      |
| 7    | README + Video  | Write documentation, record demo                  |

---

## 11. Design Choices

* **Single table:** simple recursive relationships avoid complex joins.
* **Flask + SQLite:** lightweight, aligns with CS50 stack.
* **Recursion:** elegant way to display infinite nesting.
* **Minimal UI:** clean, fast, focused on function.

---

## 12. Future Enhancements

* User accounts (authentication)
* Drag-and-drop reorder
* API endpoints for mobile integration
* Task sharing or collaboration
* Due dates and reminders
* Progress analytics (e.g., how many subtasks done)

---

## 13. Expected Outcome

A functional, recursive to-do list web app demonstrating:

* SQL data modeling
* Flask routing
* Recursion (Python + Jinja)
* CRUD operations
* Clean UI and documentation

Deliverables:

1. Working Flask project
2. README.md (750+ words)
3. 3-minute video demo