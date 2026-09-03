import json
import os
import sqlite3
from datetime import datetime, timezone


DATABASE_PATH = os.getenv(
    "RISKSHIELD_DATABASE_PATH",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../data/riskshield.db")
    )
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_data TEXT NOT NULL,
                result TEXT NOT NULL,
                review_status TEXT NOT NULL DEFAULT 'PENDING',
                reviewer_note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id)
            );
            """
        )


def record_assessment(order_data, result):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO assessments (order_data, result, created_at)
            VALUES (?, ?, ?)
            """,
            (json.dumps(order_data), json.dumps(result), created_at)
        )
        assessment_id = cursor.lastrowid
        record_audit_event(connection, assessment_id, "ASSESSMENT_CREATED", {})
        return assessment_id


def record_audit_event(connection, assessment_id, event_type, event_data):
    connection.execute(
        """
        INSERT INTO audit_events (assessment_id, event_type, event_data, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            assessment_id,
            event_type,
            json.dumps(event_data),
            datetime.now(timezone.utc).isoformat()
        )
    )


def list_assessments(limit=50):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM assessments ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [serialize_assessment(row) for row in rows]


def update_review(assessment_id, review_status, reviewer_note):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE assessments
            SET review_status = ?, reviewer_note = ?
            WHERE id = ?
            """,
            (review_status, reviewer_note, assessment_id)
        )
        if cursor.rowcount == 0:
            return None
        record_audit_event(
            connection,
            assessment_id,
            "REVIEW_UPDATED",
            {"review_status": review_status}
        )
        row = connection.execute(
            "SELECT * FROM assessments WHERE id = ?",
            (assessment_id,)
        ).fetchone()
    return serialize_assessment(row)


def delete_assessment(assessment_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM assessments WHERE id = ?",
            (assessment_id,)
        ).fetchone()
        if row is None:
            return False
        record_audit_event(connection, assessment_id, "ASSESSMENT_DELETED", {})
        connection.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
    return True


def delete_all_assessments():
    with get_connection() as connection:
        ids = connection.execute("SELECT id FROM assessments").fetchall()
        for row in ids:
            record_audit_event(connection, row["id"], "ASSESSMENT_DELETED", {})
        connection.execute("DELETE FROM assessments")


def serialize_assessment(row):
    result = json.loads(row["result"])
    return {
        "id": row["id"],
        "order_data": json.loads(row["order_data"]),
        "result": result,
        "review_status": row["review_status"],
        "reviewer_note": row["reviewer_note"],
        "created_at": row["created_at"]
    }