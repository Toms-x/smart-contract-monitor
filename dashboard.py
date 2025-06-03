from flask import Flask, render_template
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

@app.route("/")
def index():
    events = get_events()
    labels, values = get_chart_data(events)
    return render_template("index.html", events=events, labels=labels, values=values)

if __name__ == "__main__":
    app.run(debug=True)
