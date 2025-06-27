# dashboard.py

from flask import Flask, render_template, request
from flask_cors import CORS 
import json
import sqlite3
from collections import Counter

# Import the blueprint from api.py file
from api import api_bp 

app = Flask(__name__)

# This line enables CORS for the entire Flask application, allowing
# frontend dashboard to make API requests to this server.
CORS(app)

# Register the blueprint. This makes /api/stats and other routes active.
app.register_blueprint(api_bp)

# This is the original route for the old dashboard.
# It now just serves the static HTML file for the new dashboard.
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
