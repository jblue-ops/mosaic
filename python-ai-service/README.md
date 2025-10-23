# HoneyBee AI Service (Python/FastAPI)

Python microservice for AI-powered candidate evaluation using swarm intelligence.

## Overview

This service orchestrates 6 specialized AI agents that collaborate to evaluate candidates:

1. **LinkedIn Agent** - Analyzes professional experience
2. **GitHub Agent** - Evaluates code contributions
3. **Resume Agent** - Parses and analyzes resume
4. **Bias Detection Agent** - Ensures EEOC compliance
5. **Predictive Agent** - Forecasts hiring success
6. **Consensus Builder** - Aggregates votes

## Architecture

- **Framework**: FastAPI 0.109+
- **Python**: 3.12+
- **Database**: PostgreSQL (shared with Rails via SQLAlchemy)
- **AI**: OpenAI GPT-4 + LangChain
- **Server**: Uvicorn (ASGI)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run Service

```bash
# Development mode (auto-reload)
fastapi dev app/main.py

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Service will be available at: http://localhost:8000

## API Endpoints

### Health Check
```bash
GET /api/v1/health
GET /api/v1/agents/status
```

### Candidate Evaluation
```bash
POST /api/v1/evaluate
Authorization: Bearer <AI_SERVICE_API_KEY>

{
  "candidate_id": 123,
  "resume_url": "https://...",
  "linkedin_url": "https://linkedin.com/in/...",
  "github_url": "https://github.com/...",
  "job_opening_id": 456
}
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_agents.py
```

## Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Project Structure

```
python-ai-service/
├── app/
│   ├── agents/           # 6 AI agents + orchestrator
│   │   ├── base_agent.py
│   │   ├── linkedin_agent.py
│   │   ├── github_agent.py
│   │   ├── resume_agent.py
│   │   ├── bias_detection_agent.py
│   │   ├── predictive_agent.py
│   │   ├── consensus.py
│   │   └── orchestrator.py
│   ├── api/              # FastAPI endpoints
│   │   ├── evaluate.py
│   │   └── health.py
│   ├── db/               # Database models (SQLAlchemy)
│   │   ├── database.py
│   │   └── models.py
│   └── main.py           # FastAPI app
├── tests/                # Pytest tests
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md            # This file
```

## Communication with Rails

This service receives HTTP requests from Rails and sends webhook responses:

**Rails → Python (Request):**
```python
POST /api/v1/evaluate
Headers: Authorization: Bearer <token>
Body: { candidate_id, resume_url, ... }
```

**Python → Rails (Webhook):**
```python
POST https://rails-app/api/webhooks/swarm_decision
Headers: Authorization: Bearer <token>
Body: { agent_votes, consensus_details, bias_flags, ... }
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection (shared with Rails)
- `OPENAI_API_KEY` - OpenAI API key for LLM agents
- `AI_SERVICE_API_KEY` - API key for Rails to authenticate
- `RAILS_API_URL` - Rails application URL for webhooks

## Deployment

### Docker

```bash
docker build -t honeybee-ai-service .
docker run -p 8000:8000 --env-file .env honeybee-ai-service
```

### With Rails (Kamal)

See parent `config/deploy.yml` for deploying both services together.

## Development Workflow

1. Start service: `fastapi dev app/main.py`
2. Test endpoint: `curl http://localhost:8000/api/v1/health`
3. Make changes to agent code
4. Service auto-reloads (dev mode)
5. Test with Rails integration

## Next Steps

- [ ] Implement actual LinkedIn scraping/API
- [ ] Implement GitHub API integration
- [ ] Add resume parsing (PDF/DOCX)
- [ ] Build ML model for predictive agent
- [ ] Add comprehensive bias detection rules
- [ ] Implement Redis for agent communication
- [ ] Add rate limiting
- [ ] Add request logging/monitoring
- [ ] Write comprehensive tests

## License

Proprietary
