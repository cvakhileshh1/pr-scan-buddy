# PR Review Agent Backend

## Overview
Python backend for the PR Review Agent - an AI-powered system that analyzes pull requests and provides code review feedback.

## Features
- Git repository integration (GitHub, GitLab, Bitbucket)
- Automated code quality analysis
- Security vulnerability detection
- Code style and best practices review
- RESTful API for frontend integration

## Installation

1. **Create Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Setup**
Create a `.env` file in the backend directory:
```env
# Optional: Add API keys for enhanced analysis
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here  # For AI-powered suggestions
```

## Running the Backend

### Development Mode
```bash
python main.py
```
The API will be available at `http://localhost:8000`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoints

- `POST /api/analyze-pr` - Analyze a pull request
- `GET /api/health` - Health check endpoint

### Example Request
```json
{
  "repository_url": "https://github.com/username/repository",
  "pr_number": 123
}
```

### Example Response
```json
{
  "score": 85,
  "feedback": [
    {
      "file": "src/auth.py",
      "line": 23,
      "type": "warning",
      "message": "Consider using environment variables for sensitive configuration",
      "severity": 3
    }
  ],
  "summary": "Good code quality with some areas for improvement...",
  "files_changed": 4,
  "lines_added": 156,
  "lines_removed": 23,
  "recommendations": ["Address security issues before merging"]
}
```

## Architecture

- **main.py** - FastAPI application and routes
- **models.py** - Pydantic data models
- **git_integration.py** - Git repository handling
- **code_analyzer.py** - Code quality analysis engine

## Supported Platforms

- ✅ GitHub (Full support)
- 🚧 GitLab (Coming soon)
- 🚧 Bitbucket (Coming soon)

## Code Analysis Features

### Security Checks
- SQL injection detection
- Hardcoded credentials
- Dangerous function usage (eval, exec)
- Shell injection vulnerabilities

### Quality Checks
- Missing documentation
- Code style violations
- Long lines and complexity
- Import optimization

### Language Support
- ✅ Python (Full support)
- 🚧 JavaScript/TypeScript (Planned)
- 🚧 Java (Planned)
- 🚧 Other languages (Extensible)

## Development

### Adding New Language Support
1. Create a new analyzer class in `code_analyzer.py`
2. Add language-specific patterns and rules
3. Update `_is_code_file()` method

### Adding New Git Platforms
1. Implement platform-specific methods in `git_integration.py`
2. Add API integration for the platform
3. Update URL parsing logic

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Direct Deployment
Deploy to any Python hosting service (Heroku, Railway, DigitalOcean, etc.)

## License
MIT License - Feel free to use in your projects!