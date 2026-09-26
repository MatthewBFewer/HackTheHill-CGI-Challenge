# Complaint Manager

A small Flask + SQLite customer complaint CRUD application designed with the
original Nintendo 3DS browser in mind.

## Features

- Create, read, update, and delete complaints
- SQLite database
- Server-rendered HTML
- Vanilla JavaScript
- Conservative HTML/CSS/JavaScript for legacy browser compatibility
- Responsive layout for desktop and mobile
- 3DS-friendly 320px-wide core layout
- Status and category filtering
- Placeholder routing fields for future AI classification

## Setup

Create a Python virtual environment:

    python -m venv .venv

Activate it:

Windows:

    .venv\Scripts\activate

Linux/macOS:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

The included `complaints.db` already contains sample data.

To recreate the database from scratch:

    sqlite3 complaints.db < schema.sql
    sqlite3 complaints.db < sample_data.sql

Then run:

    python server.py

Open:

    http://127.0.0.1:5000/

## Project structure

    server.py
    schema.sql
    sample_data.sql
    complaints.db
    requirements.txt
    README.md
    templates/
    static/
        css/
        js/

## Future Gemini integration

The fields `category`, `urgency`, `regulatory_risk`, and `assigned_queue`
are already present so AI classification can be added later without
redesigning the basic complaint model.

Gemini integration should be performed by the Flask server rather than
directly by browser JavaScript, keeping the API key off the client.
