from flask import Flask, render_template, request, redirect, url_for, abort, session
import sqlite3
import json
import os
from datetime import datetime
import time
from google import genai
from google.genai import types


app = Flask(__name__)
app.secret_key = "change-this-to-something-random"  # needed for the staff login session
DATABASE = "complaints.db"
STAFF_PASSWORD = "hackthehill"  # change before the real demo


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def ensure_ai_columns():
    """One-time, safe-to-rerun check: adds the columns our AI triage
    needs (severity as a number, ai_summary as free text) if they
    aren't already there. Doesn't touch any existing columns."""
    db = get_db()
    existing_columns = [row["name"] for row in db.execute("PRAGMA table_info(complaints)")]

    if "severity" not in existing_columns:
        db.execute("ALTER TABLE complaints ADD COLUMN severity INTEGER DEFAULT 0")

    if "ai_summary" not in existing_columns:
        db.execute("ALTER TABLE complaints ADD COLUMN ai_summary TEXT DEFAULT ''")

    db.commit()
    db.close()


def severity_to_urgency_label(severity):
    """Maps the AI's 0-100 severity score onto the categorical labels
    complaint_form.html's Urgency dropdown already expects (Low/Medium/
    High/Critical), so the existing edit form keeps working correctly.
    Thresholds are a starting assumption - tune them if you want urgency
    to trip over at different points. For a 311-style system, think of it
    as: Critical = immediate safety hazard, High = significant
    disruption to daily life, Medium = real but non-urgent issue,
    Low = minor/cosmetic."""
    if severity >= 80:
        return "Critical"
    elif severity >= 55:
        return "High"
    elif severity >= 30:
        return "Medium"
    else:
        return "Low"


@app.template_filter("datetime")
def format_datetime(value):
    if not value:
        return ""

    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return value


# ----------------------------------------------------------------------
# GEMINI AI TRIAGE
# ----------------------------------------------------------------------

# This is the civic-tech reframe: same mechanism as before (one call,
# structured JSON output), but the prompt now speaks the language of a
# city 311 service - road/sanitation/utility categories, and severity
# framed around public safety and service disruption rather than
# generic customer-service urgency. This is the main thing that makes
# the demo feel like a 311 tool rather than a relabeled complaint box.

client = genai.Client()  # reads GEMINI_API_KEY from the environment
GEMINI_MODEL = "gemini-3.8-flash"


SYSTEM_PROMPT = """You are a triage assistant for a city 311 non-emergency
service request system. Residents submit reports about issues in their
community - potholes, missed trash pickup, broken streetlights, water
main leaks, noise complaints, park maintenance, and similar civic
issues. You are NOT a 911/emergency service; if a report describes an
active life-threatening emergency, still triage it (do not refuse),
but flag it as maximum severity so staff see it immediately and can
redirect the resident to call emergency services Users may also submit suggestions and ideas they have instead of complaints, you should give these the out of 100 socre based on how serious and implementable they are.

Given a resident's raw report, you will produce:

- a severity score from 0 to 100, where severity reflects the public
  impact and urgency of the underlying civic issue:
  0-29  = minor/cosmetic, no real disruption to daily life or safety
  30-54 = a real inconvenience affecting some residents
  55-79 = significant disruption or a real (non-immediate) safety risk
  80-100 = urgent public safety hazard or service failure affecting
           many residents (e.g. a collapsed sinkhole, a major water
           main break, a downed live power line)

- a category label, chosen from exactly one of: "Roads & Infrastructure",
  "Sanitation & Waste", "Water & Utilities", "Parks & Public Spaces",
  "Noise & Nuisance", "Public Safety (Non-Emergency)", "Other"

- a single plain-English summary paragraph, (make sure to mention the contact information if any is provided, so we can get in touch with them) that (a) restates the real
  underlying civic issue in plain terms a city staff member can act on
  immediately, and (b) ends with your best-guess proposed next step or
  fix, woven into the same paragraph (e.g. which department should
  likely handle it, or what a first response might look like).

Be concise, specific, and base your severity score on what's actually
described, not assumptions about the neighborhood or resident."""


RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "summary": {"type": "STRING"},
        "category": {"type": "STRING"},
        "severity": {"type": "INTEGER"},
    },
    "required": ["summary", "category", "severity"],
}


def triage_complaint(raw_text):
    """Returns {"summary": str, "category": str, "severity": int 0-100}."""

    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            print(f"[gemini] Attempt {attempt + 1}/{max_attempts}")

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=raw_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.3,
                ),
            )

            print("[gemini] Response received")

            data = json.loads(response.text)

            severity = max(0, min(100, int(data.get("severity", 50))))

            result = {
                "summary": data.get("summary", "(no summary returned)"),
                "category": data.get("category", "Other"),
                "severity": severity,
            }

            print("[gemini] Success")
            print(f"[gemini] Category: {result['category']}")
            print(f"[gemini] Severity: {result['severity']}")

            return result

        except Exception as e:
            print(f"[gemini] Attempt {attempt + 1} failed")
            print(f"[gemini] {type(e).__name__}: {e}")

            if attempt < max_attempts - 1:
                delay = 2 ** attempt
                print(f"[gemini] Retrying in {delay} seconds...")
                time.sleep(delay)

    print("[gemini] All attempts failed")

    return {
        "summary": f"AI unavailable - needs manual review. Original message: {raw_text[:200]}",
        "category": "Other",
        "severity": 50,
    }


# ----------------------------------------------------------------------
# STAFF LOGIN GATE
# ----------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered = request.form.get("password", "")

        if entered == STAFF_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("index"))

        return render_template("login.html", error="Incorrect password.")

    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("login"))


# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------

@app.route("/")
def home():
    submitted = request.args.get("submitted") == "1"

    return render_template(
        "home.html",
        submitted=submitted
    )


@app.route("/admin/dashboard")
def index():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    db = get_db()

    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY severity DESC, created_at DESC"

    complaints = db.execute(query, params).fetchall()
    db.close()

    return render_template(
        "complaints.html",
        complaints=complaints,
        selected_status=status,
        selected_category=category
    )


@app.route("/complaints/new", methods=["GET", "POST"])
def new_complaint():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()

        if not customer_name or not subject or not description:
            return render_template(
                "new_complaint.html",
                error="Name, subject, and description are required."
            )

        # Send the complaint to the AI for triage.
        ai_result = triage_complaint(description)
        urgency_label = severity_to_urgency_label(ai_result["severity"])

        # Save the complaint and AI analysis to the database.
        db = get_db()

        db.execute(
            """
            INSERT INTO complaints
            (customer_name, customer_email, subject, description,
             status, category, urgency, regulatory_risk, assigned_queue,
             severity, ai_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name,
                customer_email,
                subject,
                description,
                "New",
                ai_result["category"],
                urgency_label,
                "Not assessed",
                "Unassigned",
                ai_result["severity"],
                ai_result["summary"],
            )
        )

        db.commit()

        complaint_id = db.execute(
            "SELECT last_insert_rowid() AS id"
        ).fetchone()["id"]

        db.close()

        # Do NOT show the AI result to the customer.
        # Send them back to the homepage with a success message.
        return redirect(url_for("home", submitted="1"))

    return render_template("new_complaint.html")


@app.route("/complaints/<int:complaint_id>")
def view_complaint(complaint_id):
    # Complaint details and AI analysis are staff-only.
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    db = get_db()

    complaint = db.execute(
        "SELECT * FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()

    db.close()

    if complaint is None:
        abort(404)

    return render_template(
        "complaint.html",
        complaint=complaint
    )


@app.route("/complaints/<int:complaint_id>/edit", methods=["GET", "POST"])
def edit_complaint(complaint_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    db = get_db()

    complaint = db.execute(
        "SELECT * FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()

    if complaint is None:
        db.close()
        abort(404)

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "New").strip()
        category = request.form.get("category", "Other").strip()
        urgency = request.form.get("urgency", "Not assessed").strip()
        regulatory_risk = request.form.get("regulatory_risk", "Not assessed").strip()
        assigned_queue = request.form.get("assigned_queue", "Unassigned").strip()

        if not customer_name or not subject or not description:
            db.close()

            return render_template(
                "complaint_form.html",
                complaint=request.form,
                form_title="Edit Report",
                error="Name, subject, and description are required."
            )

        db.execute(
            """
            UPDATE complaints
            SET customer_name = ?,
                customer_email = ?,
                subject = ?,
                description = ?,
                status = ?,
                category = ?,
                urgency = ?,
                regulatory_risk = ?,
                assigned_queue = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                customer_name,
                customer_email,
                subject,
                description,
                status,
                category,
                urgency,
                regulatory_risk,
                assigned_queue,
                complaint_id
            )
        )

        db.commit()
        db.close()

        return redirect(url_for("view_complaint", complaint_id=complaint_id))

    db.close()

    return render_template(
        "complaint_form.html",
        complaint=complaint,
        form_title="Edit Report",
        error=None
    )


@app.route("/complaints/<int:complaint_id>/delete", methods=["POST"])
def delete_complaint(complaint_id):
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    db = get_db()

    db.execute(
        "DELETE FROM complaints WHERE id = ?",
        (complaint_id,)
    )

    db.commit()
    db.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    ensure_ai_columns()
    app.run(host='0.0.0.0', port=5000, debug=False)
