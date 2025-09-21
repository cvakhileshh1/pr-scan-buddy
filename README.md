# PR Review Agent

An AI-assisted system that reviews Pull Requests (PRs) from Git repositories.  
It analyzes code changes, detects potential issues, and provides structured feedback to help developers improve code quality.

---

## Features

- 🔍 Fetch PRs from GitHub (GitLab/Bitbucket can be added)
- ✅ Analyze modified code for:
  - Syntax errors
  - Code quality issues
  - Readability, performance, and security concerns
- 📝 Feedback per file and line
- 📊 Overall PR quality score
- 📄 Export feedback as Markdown
- 🌐 Simple web UI for input and results

---

## Tech Stack

**Backend**  
- Python  
- FastAPI  
- Requests / Git integration  

**Frontend**  
- React  
- Fetch API for backend communication  

---

## Installation & Setup

### Backend
```bash
cd backend
pip install -r requirements.txt

# optional: set GitHub token for higher API limits
export GITHUB_TOKEN="your_github_token"

pr-review-agent/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py                 # FastAPI app
│  │  ├─ git_integration.py      # clone/fetch PRs (GitHub implemented)
│  │  ├─ analyzer.py             # code analysis & feedback generation
│  │  ├─ reporter.py             # markdown export, scoring utilities
│  │  └─ settings.py             # config (tokens, tmp paths)
│  ├─ requirements.txt
│  └─ README_BACKEND.md
├─ frontend/
│  ├─ README_FRONTEND.md
│  ├─ package.json
│  ├─ src/
│  │  ├─ index.jsx
│  │  └─ App.jsx
│  └─ public/
│     └─ index.html
└─ README.md

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
