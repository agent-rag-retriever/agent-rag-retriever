# DevOps Autonomous Incident Triage Pipeline

Welcome to the **DevOps Autonomous Incident Triage Pipeline**. This system automatically ingests failed CI/CD pipeline runs, extracts relevant code context using a Vector Database (RAG), generates LLM-powered code repairs, and automatically opens a GitHub Pull Request with the fix.

## 🏗 System Architecture & Microservices

Our pipeline is architected as an event-driven system containing 4 isolated AI Agent microservices, orchestrated by a central Node.js backend:

- **Agent 1: Log Parser**
  - **Role:** Extracts the file, line number, and error type from raw GitHub Action logs.
  - **Tech Stack:** Node.js, Regular Expressions (`devops-integration/src/agents/agent1-logParser.js`).

- **Agent 2: RAG Retriever**
  - **Role:** Provides a deterministic code window around the point of failure.
  - **Tech Stack:** Python, FastAPI, ChromaDB. Uses semantic search to locate missing contexts and local filesystem fallback for exact line numbers (`retriever.py`, `app.py`).

- **Agent 3: Code Repair**
  - **Role:** LLM-powered repair agent that generates minimal, safe code patches and outputs strictly validated JSON diagnostics with confidence scores.
  - **Tech Stack:** Python, FastAPI, Pydantic, Gemini API (`agent3_code_repair.py`). Includes a graceful fallback mechanism if rate limits are exceeded.

- **Agent 4: Git Bridge**
  - **Role:** Fully automated GitHub integration that clones the repo, applies the unified diff patch, commits, pushes, and opens a Pull Request.
  - **Tech Stack:** Node.js, `simple-git`, Octokit (`devops-integration/src/agents/agent4-gitBridge.js`).

- **Core Orchestrator & Webhook Receiver**
  - **Role:** Handles incoming GitHub Webhooks, orchestrates the sequential execution of the 4 agents, and broadcasts state via Server-Sent Events (SSE).
  - **Tech Stack:** Node.js, Express (`devops-integration/src/orchestrator.js`).

- **Frontend Dashboard**
  - **Role:** React + Vite dashboard displaying the pipeline's real-time execution, incident history, and side-by-side patch diffs.
  - **Tech Stack:** React, Tailwind CSS, Lucide Icons (`frontend/`).

---

## ⚙️ How it Works in Production

In a real-world production environment, the pipeline operates as a fully autonomous closed-loop system:

1. **Failure Event:** A developer commits broken code, causing a CI/CD pipeline (e.g., GitHub Actions) to fail.
2. **Webhook Trigger:** The CI/CD runner fires a webhook to the Triage Pipeline's Orchestrator containing the workflow run ID.
3. **Log Ingestion:** The Orchestrator authenticates with the GitHub API and downloads the raw execution logs of the failed job.
4. **Log Parsing:** Agent 1 parses the raw logs to identify the exact file, line number, and error type.
5. **Context Retrieval:** Agent 2 pulls the relevant code block from the repository (using semantic RAG search if the file path is ambiguous).
6. **Code Repair:** Agent 3 feeds the error message and the code context to an LLM to generate a precise unified diff patch to fix the bug.
7. **Pull Request:** Agent 4 checks out a new branch, applies the generated patch, and opens a Pull Request back to the main repository for human review.
8. **Real-time Monitoring:** Site Reliability Engineers (SREs) can monitor the entire process live via the SSE-powered Frontend Dashboard.

---

## 🚀 Setup & Execution Guide

To run the full pipeline locally, follow these steps:

### Prerequisites
1. Node.js (v20+)
2. Python (v3.10+)
3. Git
4. A Gemini API Key
5. A GitHub Personal Access Token (with `repo` and `workflow` scopes)

### 1. Environment Variables
Create a `.env` file in the root directory (`c:\dev\DevOps-Autonomous-Incident-Triage-Pipeline-v2\.env`) with the following keys:
```ini
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### 2. Install Dependencies
Run the installation script to setup dependencies for all microservices:
```bash
./install.bat
```

### 3. Start the Pipeline
You can start all 4 services concurrently using the provided batch script. This will open 4 separate terminal windows.
```bash
# Starts Agent 2, Agent 3, the Orchestrator, and the Frontend Dashboard
./start.bat

# Remember to start ngrok in a separate terminal to expose your webhook endpoint!
ngrok http 4000
```

### 4. Stop the Pipeline
To cleanly stop all services and free up the network ports, run:
```bash
./end.bat
```

---

## 🐞 Testing the Pipeline (Live Demo)

Once the pipeline is running, you can test it directly from the Frontend Dashboard (running at `http://localhost:5173`):

1. **Open the Dashboard:** Navigate to `http://localhost:5173` in your browser.
2. **Trigger an Incident:** In the "Trigger Incident" panel, click the **Easy**, **Medium**, or **Hard** button.
3. **Automated CI Failure:** The backend will automatically inject a dummy bug into the repository and push it to GitHub. This triggers the GitHub Action (`ci.yml`), which deliberately fails.
4. **Watch the Magic:** The GitHub Action sends a webhook back to your local `ngrok` instance. You will see the Live Pipeline on the dashboard spring into action, parse the logs, generate a fix, and open a Pull Request entirely autonomously!
