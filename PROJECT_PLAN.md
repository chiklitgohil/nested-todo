Here’s your **complete technical specification and documentation** for the **Nested To-Do App**, written in full Markdown, ready for your GitHub README.md or CS50 final project submission.

---

# **Nested To-Do App**

#### Video Demo:

*(Add your YouTube URL here once you record it)*

#### Author:

**Chiklit Gohil**

#### Technologies:

Python (Flask), SQLite, HTML, CSS (Bootstrap), JavaScript (ES6), SortableJS

---

## **Overview**

Nested To-Do is a minimalist, yet deeply functional web-based task manager designed to let users **infinitely nest tasks** and **visually break large goals into smaller subtasks**.

It combines the simplicity of a linear to-do list with the power of hierarchical task management, allowing every task to contain any number of subtasks, each with its own description, completion state, and metadata.

This app was developed as a **CS50 Final Project**, adhering to principles of clean UI, minimal friction, and deep structural flexibility.

---

## **Core Idea**

Most task apps stop at one or two levels of nesting. This project allows **infinite recursion** — a task may contain a subtask, which itself can contain other subtasks, and so on.

This structure makes it ideal for programmers, writers, and planners who break problems into smaller atomic units.

---

## **Key Features**

| Feature                            | Description                                                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Infinite nesting**               | Each task can have an unlimited number of subtasks, visually connected with a branching structure.           |
| **Collapsible hierarchy**          | Parent tasks can expand or collapse their subtasks for better focus and reduced visual clutter.              |
| **Inline editing**                 | Titles and descriptions can be edited directly by clicking; no separate “Edit” buttons or modals.            |
| **Auto-save**                      | Task details are saved automatically after 1 second of inactivity, no manual save needed.                    |
| **My Day**                         | Users can mark tasks as “My Day” to focus on them temporarily; the list resets every midnight automatically. |
| **Bulk actions**                   | Select multiple tasks to mark as done, delete, or add to “My Day”.                                           |
| **Soft delete + Undo**             | Deleted tasks are moved to a “trash” state and can be restored within a grace period.                        |
| **Progress tracking**              | Parent tasks show a live progress bar based on completion ratio of subtasks.                                 |
| **Drag-and-drop reordering**       | Users can rearrange tasks or move subtasks between parents using SortableJS.                                 |
| **Responsive design**              | Works smoothly across desktop and mobile, with a collapsible sidebar and adaptive layouts.                   |
| **Accessible & keyboard-friendly** | Includes ARIA roles, keyboard shortcuts for navigation, and proper semantic HTML.                            |

---

## **Project Structure**

```
nested-todo/
│
├── app.py                  # Flask backend server
├── tasks.db                # SQLite database
│
├── static/
│   ├── styles.css          # Custom styles
│   └── logo.png            # Optional app logo
│
├── templates/
│   ├── layout.html         # Base HTML structure with Bootstrap
│   ├── index.html          # Main page layout (sidebar + task list + detail pane)
│   └── tasks.html          # Jinja macro for recursive task rendering
│
├── venv/                   # Python virtual environment
└── README.md               # Documentation (this file)
```

---

## **Component Breakdown**

### **1. Flask Application (`app.py`)**

**Purpose:**
Serves as the web server and handles all application logic and API endpoints.

#### **Core Functions**

| Function                    | Role                                                                    |
| --------------------------- | ----------------------------------------------------------------------- |
| `init_db()`                 | Creates and initializes the `tasks` table schema in SQLite.             |
| `get_db_connection()`       | Opens a persistent SQLite connection.                                   |
| `get_subtasks()`            | Recursively retrieves tasks and their subtasks.                         |
| `compute_progress()`        | Calculates the percentage of completed subtasks recursively.            |
| `delete_recursive()`        | Deletes a task and all its subtasks from the database.                  |
| `midnight_reset_thread()`   | Background thread that resets “My Day” flags at midnight automatically. |
| `start_background_thread()` | Initializes the midnight thread once when the app starts.               |

---

### **2. Database Schema**

| Column         | Type                | Description                                |
| -------------- | ------------------- | ------------------------------------------ |
| `id`           | INTEGER PRIMARY KEY | Unique task identifier                     |
| `title`        | TEXT                | The name of the task                       |
| `description`  | TEXT                | Optional description (markdown-compatible) |
| `is_done`      | INTEGER (0/1)       | Task completion flag                       |
| `parent_id`    | INTEGER             | Parent task’s ID (for nesting)             |
| `category`     | TEXT                | Label like “Work” or “Personal”            |
| `is_today`     | INTEGER (0/1)       | Flag for inclusion in “My Day”             |
| `position`     | INTEGER             | Custom order index for siblings            |
| `created_at`   | TIMESTAMP           | Task creation time                         |
| `updated_at`   | TIMESTAMP           | Last update time                           |
| `completed_at` | TIMESTAMP           | Completion timestamp                       |
| `deleted_at`   | TIMESTAMP           | For soft delete and undo support           |

---

### **3. Templates**

#### **layout.html**

* Base structure with:

  * Bootstrap & FontAwesome CDN links.
  * Responsive meta tag.
  * Placeholder `{% block content %}` for page injection.
* Script includes at the bottom:

  * Bootstrap bundle.
  * SortableJS.
  * Main JavaScript logic.

#### **index.html**

* Defines the main interface layout:

  * **Left Sidebar (20%)**

    * App logo and collapse toggle button.
    * Smart lists:

      * “All” (shows all tasks)
      * “My Day” (tasks marked with `is_today=1`)
      * “Inbox” (uncategorized tasks)
    * Custom user-created categories below a divider.
  * **Main Content (40%)**

    * Add new task form.
    * Nested task list rendered using `tasks.html`.
  * **Detail Pane (40%)**

    * Displays selected task title, description, and immediate children.
    * Shows a live progress bar and subtask list.
    * Auto-saves edits to description/title.

#### **tasks.html**

* Recursive macro that:

  * Displays each task as a `<li>` with:

    * Checkbox for completion.
    * Task title (editable on double-click).
    * Collapse toggle button for subtasks.
    * Hover actions: add subtask, add to My Day, delete.
  * Calls itself recursively for child tasks.

---

### **4. Static Files**

#### **styles.css**

Defines:

* **Three-column grid layout**:

  * Sidebar (20%)
  * Task List (40%)
  * Detail Pane (40%)
* **Connector lines** between nested tasks.
* **Hover actions** visibility logic.
* **Active task highlighting**.
* **Responsive breakpoints** for smaller screens.
* **Collapsed children** with `.collapsed` class.

---

## **Client-Side Logic (JavaScript)**

| Function                | Description                                                    |
| ----------------------- | -------------------------------------------------------------- |
| `selectTask(id)`        | Fetches and loads task details + subtasks in the detail pane.  |
| `toggleDone(id)`        | Toggles `is_done` flag for the given task via API.             |
| `saveTitle(id)`         | Saves inline-edited title on blur or Enter key.                |
| `promptAddSubtask(id)`  | Prompts for new subtask title and adds it.                     |
| `deleteTask(id)`        | Sends soft-delete request, then shows undo toast.              |
| `addToMyDay(id)`        | Marks task as part of “My Day” and updates counter.            |
| `toggleCollapse(id)`    | Expands/collapses subtasks and stores state in `localStorage`. |
| `submitAddForm()`       | Adds new top-level task from the main input.                   |
| `autosaveDescription()` | Auto-saves description changes with 1s debounce.               |
| `renderTaskList()`      | Dynamically re-renders visible tasks (or reloads for now).     |
| `updateMyDayCount()`    | Refreshes “My Day” badge count.                                |
| `enableInlineEdit(id)`  | Activates in-place title editing on double-click.              |
| `showToast(msg)`        | Creates lightweight Bootstrap toast for feedback.              |
| `Sortable.onEnd()`      | Updates task positions and parent after drag-and-drop.         |

---

## **User Interface Behavior**

### **Sidebar**

* Collapsible (stays at 68px when collapsed).
* Displays smart lists and user categories.
* Each list loads tasks dynamically via `/api/list/<name>` endpoint.

### **Task List**

* Displays recursive nested structure with visual connectors.
* Hovering over a task reveals:

  * “Add Subtask” button.
  * “Add to My Day” star.
  * “Delete” button.
* Drag handle for reordering tasks (`fa-grip-vertical` icon).
* Collapsible subtasks to prevent clutter.

### **Detail Pane**

* Shows the selected task’s title, description, and progress bar.
* Auto-saves edits to description after 1 second of pause.
* Displays immediate subtasks for quick access.
* Updates instantly when a new subtask is selected.

---

## **Backend API Summary**

| Endpoint                     | Method | Description                                                |
| ---------------------------- | ------ | ---------------------------------------------------------- |
| `/`                          | GET    | Main interface                                             |
| `/api/task/<id>`             | GET    | Fetch task details and children                            |
| `/api/task/<id>/description` | POST   | Update description                                         |
| `/api/task/<id>/title`       | POST   | Update title                                               |
| `/api/task/<id>/toggle`      | POST   | Toggle completion                                          |
| `/api/task/<id>/today`       | POST   | Toggle My Day inclusion                                    |
| `/api/add`                   | POST   | Add new task (supports `parent_id`)                        |
| `/api/delete`                | POST   | Hard delete (recursive)                                    |
| `/api/task/reorder`          | POST   | Save order and parent after drag                           |
| `/api/task/<id>/soft_delete` | POST   | Move to trash (soft delete)                                |
| `/api/task/<id>/restore`     | POST   | Undo delete (restore)                                      |
| `/api/tasks/bulk`            | POST   | Perform bulk operations                                    |
| `/api/list/<name>`           | GET    | Fetch filtered list (“all”, “myday”, “inbox”, or category) |

---

## **UX Flow**

1. **Add a task** → Appears in Inbox by default.
2. **Add subtasks** → Click + icon next to parent task.
3. **Collapse or expand** → Click chevron next to parent task.
4. **Mark complete** → Check the checkbox; parent progress updates.
5. **Add to My Day** → Click the star button; resets automatically at midnight.
6. **Delete** → Soft delete, undo available for 30 seconds.
7. **Reorder** → Drag by grip handle; position saved automatically.
8. **Edit details** → Click on title or description; auto-save handles persistence.

---

## **Auto Reset: “My Day”**

* Runs in a **background daemon thread**.
* Checks system time every 60 seconds.
* At midnight, executes:

  ```sql
  UPDATE tasks SET is_today = 0 WHERE is_today = 1;
  ```
* Resets the “My Day” view automatically.

---

## **Responsive Design Behavior**

| Screen Width | Layout                                          |
| ------------ | ----------------------------------------------- |
| **> 900px**  | 3-column layout (Sidebar + Tasks + Detail Pane) |
| **< 900px**  | Sidebar hidden, task list occupies full width   |
| **< 600px**  | Task detail view stacks vertically under list   |
| **Mobile**   | Floating add button, collapsible list sections  |

---

## **Accessibility Features**

* `aria-label` for all icons and buttons.
* Keyboard support for:

  * `Enter` to confirm edits.
  * `Esc` to cancel inline edit.
  * Arrow keys to navigate tasks.
* High contrast text and visible focus outlines.
* Screen-reader friendly roles:

  * `role="list"` for UL elements.
  * `role="listitem"` for LI elements.

---

## **Possible Future Extensions**

| Category                  | Ideas                                           |
| ------------------------- | ----------------------------------------------- |
| **Reminders & Due Dates** | Add date pickers and notification logic.        |
| **Recurring Tasks**       | Allow tasks to repeat daily/weekly/monthly.     |
| **Collaboration**         | Add user authentication and shared lists.       |
| **Attachments**           | Upload and link files or images to tasks.       |
| **Search & Filters**      | Full-text search and task filtering.            |
| **Notifications**         | Browser push notifications for due tasks.       |
| **Markdown Support**      | Render formatted task descriptions.             |
| **Dark Mode**             | Toggle between light and dark Bootstrap themes. |

---

## **Design Philosophy**

1. **Minimal clicks.** Everything should be editable in place.
2. **Visual clarity.** Indentation and lines show hierarchy instantly.
3. **Performance simplicity.** Flat SQLite DB + recursion for hierarchy.
4. **Automatic behavior.** Auto-save, auto-reset, and auto-refresh minimize friction.
5. **Extensibility.** Every feature (categories, reminders, markdown) can plug into the same schema.

---

## **How to Run Locally**

```bash
# Clone the repo
git clone https://github.com/chiklitgohil/nested-todo.git
cd nested-todo

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows

# Install dependencies
pip install flask

# Initialize database
python
>>> from app import init_db
>>> init_db()
>>> exit()

# Run the app
python app.py
```

Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## **Final Notes**

This project was built to emphasize **nested thinking** and **frictionless flow** — every part of the design, from the connector lines to auto-save and midnight reset, was made to keep users thinking *about their tasks*, not the interface.

The structure and modular backend allow easy evolution into a full productivity platform with reminders, collaboration, and AI insights.

---

Would you like me to generate a version of this README with **GitHub-flavored Markdown formatting** (links, tables, collapsible sections, icons) and **proper CS50 submission tone (academic but concise)** next? It’ll be plug-and-play for your repo and submission form.
