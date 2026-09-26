PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS complaints;

CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'New',
    category TEXT NOT NULL DEFAULT 'Other',
    urgency TEXT NOT NULL DEFAULT 'Not assessed',
    regulatory_risk TEXT NOT NULL DEFAULT 'Not assessed',
    assigned_queue TEXT NOT NULL DEFAULT 'Unassigned',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_category ON complaints(category);
CREATE INDEX idx_complaints_created_at ON complaints(created_at);
