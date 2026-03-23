# PyRuleCheck MVP

PyRuleCheck is a static code analysis engine that performs deterministic, rule-based checks on Python repositories without using any AI models. It evaluates code for security flaws, code quality issues, performance bottlenecks, and cross-file dependencies.

## Features
- ✅ **Deterministic Rules:** Uses Python's `ast` (Abstract Syntax Trees), `regex`, and `bandit` logic.
- ✅ **FastAPI Backend:** Fast, async-enabled, and modular architecture.
- ✅ **React Frontend:** Modern, dark-themed dashboard built with Vite and TailwindCSS.
- ✅ **Constraints Checked:** Only parses `.py` files, requires max 3 Python files, and files under 500 lines.
- ✅ **Grading System:** Aggregates findings into security, maintainability, and quality scores, giving an overall A-F grade.

## Technical Stack
- **Backend:** Python 3.9+, FastAPI, Uvicorn, Pydantic, AST, Bandit, Radon, Flake8
- **Frontend:** React, Vite, TailwindCSS, Lucide React, Axios

## Setup Instructions

### 1. Configure Environment Variables
You must set up a GitHub OAuth application to use the login functionality:
1. Go to your GitHub account settings -> Developer settings -> OAuth Apps
2. Click **New OAuth App**.
3. Set **Homepage URL** to `http://localhost:5173`
4. Set **Authorization callback URL** to `http://localhost:8000/api/auth/github/callback`
5. Copy your Client ID and generate a new Client Secret.
6. Create a `.env` file in the `backend` directory (copy the properties from `.env.example`) and fill in `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`.

### 2. Local Development (Without Docker)

#### Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```bash
   uvicorn main:app --reload
   ```
   *The backend will be available at http://localhost:8000*

#### Frontend Setup
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will be available at http://localhost:5173*

### 2. Running with Docker Compose (Production/Deployment)

You can run the full stack (Frontend & Backend) via Docker.
1. Make sure Docker is running.
2. At the root of the project, run:
   ```bash
   docker-compose up --build
   ```
3. Access the web app at `http://localhost:80` (or `http://localhost:5173` depending on setup).

## Security Overview
This infrastructure clones public repositories into a temporary directory using `--depth 1` and cleans it up immediately after parsing the syntax tree. No models are executed, and code evaluation is strictly static syntax inspection preventing arbitrary command execution vulnerabilities.
