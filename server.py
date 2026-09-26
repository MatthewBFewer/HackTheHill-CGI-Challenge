from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = "complaints.db"


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


@app.template_filter("datetime")
def format_datetime(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return value


@app.route("/")
def index():
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

    query += " ORDER BY created_at DESC"

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
        status = request.form.get("status", "New").strip()
        category = request.form.get("category", "Other").strip()

        if not customer_name or not subject or not description:
            return render_template(
                "complaint_form.html",
                complaint=request.form,
                form_title="New Complaint",
                error="Customer name, subject, and description are required."
            )

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO complaints
            (customer_name, customer_email, subject, description,
             status, category, urgency, regulatory_risk, assigned_queue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_name,
                customer_email,
                subject,
                description,
                status,
                category,
                "Not assessed",
                "Not assessed",
                "Unassigned"
            )
        )
        db.commit()
        complaint_id = cursor.lastrowid
        db.close()

        return redirect(url_for("view_complaint", complaint_id=complaint_id))

    return render_template(
        "complaint_form.html",
        complaint=None,
        form_title="New Complaint",
        error=None
    )


@app.route("/complaints/<int:complaint_id>")
def view_complaint(complaint_id):
    db = get_db()
    complaint = db.execute(
        "SELECT * FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()
    db.close()

    if complaint is None:
        abort(404)

    return render_template("complaint.html", complaint=complaint)


@app.route("/complaints/<int:complaint_id>/edit", methods=["GET", "POST"])
def edit_complaint(complaint_id):
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
                form_title="Edit Complaint",
                error="Customer name, subject, and description are required."
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
        form_title="Edit Complaint",
        error=None
    )


@app.route("/complaints/<int:complaint_id>/delete", methods=["POST"])
def delete_complaint(complaint_id):
    db = get_db()
    db.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
