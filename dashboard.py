from flask import Flask, render_template
from flask_cors import CORS
from api import api_bp

app = Flask(__name__)

# solution to the "Failed to fetch" error.
CORS(app)

# Register all the API routes from api.py
app.register_blueprint(api_bp)

# This route just serves the main HTML page.
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)