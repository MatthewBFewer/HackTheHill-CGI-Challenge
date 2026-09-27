# InquiryResolverIQ
### Last updated: 09/27/2026

- A 311-style platform built for bringing citizens closer to their municipal governments
- created for HackTheHill III
- Note that some of the files are in the context of collecting "customer complaints" as the scope of this project shifted halfway through development, and not all files were refactored
- contains some minimal authentication but is by no means secure in this version, it is currently just a proof of concept

## Tech Stack

Backend: Python + Flask + Google gemini API + (some js functionality)
Frontend: HTML + Jinja2 + CSS + JS
Database: SQLite

## Setup Guide

Create a Python virtual environment in the project's directory (ensure python 3.14.x is installed first):

    python3 -m venv .venv

### Activate it:

Windows:

    .venv\Scripts\activate

Linux/macOS:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

The included `sample_data.sql` is a database population script that gives you some sample data.

To recreate the database from scratch with the sample data (ensure the SQLite CLI is installed), run the following:

    sqlite3 complaints.db
    .read schema.sql
    .read sample_data.sql

To boot up the server, run:

    python3 server.py

Open a local development server (or listen on port 5000 with your device's IP) to see the application:

    http://127.0.0.1:5000/
