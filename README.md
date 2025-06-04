# smart-contract-monitor

Smart contract monitoring dashboard

A real-time monitoring system that listens for smart contract events on the Ethereum blockchain (currently focused on USDC Transfer events) and displays them in a clean, responsive dashboard.

Built for learning purposes, but designed to be extended and improved over time.

What this project does
- Listens to USDC transfer events live from Ethereum mainnet using Web3.py.
- Logs all captured events into a local SQLite database (events.db).
- Alerts a Slack channel whenever new transfer events are detected.
- Displays recent events and basic analytics (transfer volume per block) in a simple web dashboard built with Flask + Chart.js + Tailwind CSS.
- Supports future workflow automations with n8n, currently integrated via webhook.


How to run it
# Clone the repo
git clone https://github.com/toms-x/smart-contract-monitor.git
cd smart-contract-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your .env file
cp .env.example .env
# Then fill in your Web3 provider URL and Slack webhook URL

# Start the event listener
python monitor/listener.py

# Start the dashboard (in another terminal)
python dashboard.py

=> Dependencies
- web3.py: connecting to Ethereum
- Flask: serving the dashboard
- Chart.js: for chart rendering
- Tailwind CSS: for UI styling
- SQLite: for lightweight event storage
- dotenv: for environment variable loading
- n8n: for automation hooks and future workflow extensibility

🛣️ Roadmap / TODO
- Add filtering options on the dashboard (e.g., filter by address)
- Add pagination or auto-refresh for events table
- Build a dedicated REST API for querying historical data
- Extend event support beyond just Transfer
- Deploy to Render/Heroku with persistent DB
- Integrate OpenAI for automatic summaries of large transfer spikes
- Use n8n to build a historical volume logging workflow (e.g., push to Airtable)
- Add tests and CI/CD pipeline
- Allow user-defined alert thresholds or address watchlists


🤝 Contributions and improvements

I plan to grow this project over time and welcome collaborators or feedback. If you’re interested in blockchain, automation, or backend systems, feel free to open a PR or drop me a message.
