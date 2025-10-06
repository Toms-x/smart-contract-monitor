# Real-Time Smart Contract Monitoring Dashboard

A full-stack, cloud-deployed monitoring system that listens for smart contract events on the Ethereum blockchain, processes them, and displays them in a real-time, interactive dashboard with AI-powered query capabilities.

## Key Features

- Live Blockchain Listener: A resilient Python worker service using Web3.py and an Alchemy connection to monitor live Transfer events for major token contracts.

- Dynamic Web Dashboard: A sleek, single-page application built with vanilla JavaScript and Tailwind CSS that fetches data from a backend API without page reloads.

- Interactive Data Visualization: Displays a live-updating bar chart of transaction volume per block using Chart.js.

- AI-Powered Queries: A natural language interface that uses the OpenAI API to translate user questions (e.g., "show me the 5 largest transfers") into SQL queries and displays the results.

- Professional Deployment Architecture: The application is fully containerized with Docker and deployed to Google Cloud, showcasing modern DevOps practices.

- Web App: Deployed as a scalable serverless service on Google Cloud Run.
- Listener Worker: Deployed as a persistent background task on a Google Compute Engine VM.
- Image Registry: All Docker images are stored and managed in Google Artifact Registry.


## Architecture Overview
This project uses a modern, multi-service architecture designed for scalability and resilience.

- Frontend: A static HTML/CSS/JS single-page application that runs in the user's browser. It communicates with a backend API to get all its data.

- Backend (Web Server): A Python Flask server with a Gunicorn WSGI, running as a stateless container on Google Cloud Run. Its only job is to serve the frontend and provide the API endpoints.

- Backend (Worker): A Python Web3.py script running as a separate, persistent container on a Google Compute Engine VM. It continuously polls the blockchain and saves events to the database.

- Database: A simple SQLite file is used for this version of the project. A future improvement is to upgrade to a cloud-native database like PostgreSQL to allow the deployed services to share data.

## How to Run It (Docker)
This project is fully containerized, making it incredibly simple to run locally.

### Prerequisites:

Docker and Docker Compose installed.

A .env file created in the project root with your INFURA_URL (Alchemy URL), CONTRACT_ADDRESS, and OPENAI_API_KEY.

1. Clone the repo:

git clone [https://github.com/toms-x/smart-contract-monitor.git](https://github.com/toms-x/smart-contract-monitor.git)
cd smart-contract-monitor

2. Build and run the services:
This single command will build both the web and worker images and start both containers.

docker-compose up --build

3. Access the dashboard:
Open your browser and go to https://www.google.com/search?q=http://127.0.0.1:5001.

## Roadmap / Future Improvements
- [ ] Upgrade to a Cloud Database: Replace SQLite with a managed PostgreSQL instance (e.g., Google Cloud SQL) to enable a shared, persistent state for the deployed services.

- [ ] Implement a CI/CD Pipeline: Create a GitHub Action to automatically build and deploy the services to Google Cloud on every push to the main branch.

- [ ] Improve AI Capabilities: Fine-tune the AI prompt to handle more complex queries and provide deeper analytical insights.

- [ ] Add User Authentication: Secure the dashboard and rate-limit the AI feature to manage costs in a production environment.