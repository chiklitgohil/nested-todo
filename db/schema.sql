CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_done INTEGER DEFAULT 0,          -- 0 or 1
    parent_id INTEGER,                  -- NULL for top-level
    category TEXT,                      -- e.g. 'Work', 'Personal' (nullable)
    is_today INTEGER DEFAULT 0,         -- flag for My Day
    position INTEGER DEFAULT 0,         -- ordering among siblings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES tasks(id)
);
