from flask import Flask, render_template, request 
import json
import sqlite3
from collections import Counter

app = Flask(__name__)

DB_PATH = "events.db"

def get_events():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT event_data FROM events ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    events = [json.loads(row[0]) for row in rows]
    return events

def get_chart_data(events):
    block_counts = Counter([e.get("blockNumber") for e in events if e.get("blockNumber")])
    labels = list(map(str, block_counts.keys()))
    values = list(block_counts.values())
    return labels, values

def get_total_event_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM events")
    total = c.fetchone()[0]
    conn.close()
    return total

@app.route("/")
def index():
    page = request.args.get("page", default=1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT event_data FROM events ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
    rows = c.fetchall()
    conn.close()

    events = [json.loads(row[0]) for row in rows]
    labels, values = get_chart_data(events)

    # total event count for frontend pagination controls
    total = get_total_event_count()
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "index.html",
        events=events,
        labels=labels,
        values=values,
        page=page,
        total_pages=total_pages,
    )

if __name__ == "__main__":
    app.run(debug=True)
