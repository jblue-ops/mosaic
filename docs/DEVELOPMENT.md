# HoneyBee/Mosaic Development Guide

Complete guide for developing the HoneyBee recruiting platform and future Mosaic platform.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Running Services](#running-services)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Code Quality](#code-quality)
8. [Database Operations](#database-operations)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

## Quick Start

```bash
# 1. Clone and navigate
cd /path/to/mosaic

# 2. Set up Rails
cd honeybee
bundle install
cp .env.example .env
# Edit .env with your credentials
rails db:create db:migrate
cd ..

# 3. Set up Python
cd python-ai-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
cd ..

# 4. Start all services (use 4 terminals or foreman)
# Terminal 1: cd honeybee && rails server
# Terminal 2: cd honeybee && rails solid_queue:start
# Terminal 3: cd python-ai-service && fastapi dev app/main.py
# Terminal 4: cd honeybee && rails tailwindcss:watch
```

## Prerequisites

### Required

- **Ruby** 3.3+ (`ruby --version`)
- **Rails** 8.0.3+ (installed via bundler)
- **PostgreSQL** 16+ (`psql --version`)
- **Python** 3.12+ (`python --version`)
- **Node.js** 18+ (for Tailwind CSS)
- **Git** (`git --version`)

### Recommended

- **Homebrew** (macOS package manager)
- **foreman** or **overmind** (process manager)
- **pg_admin** or **Postico** (database GUI)
- **HTTPie** or **Postman** (API testing)

### API Keys Needed

- **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- **Ashby API Key** (optional) - For ATS integration
- **Greenhouse API Key** (optional) - For ATS integration
- **Sentry DSN** (optional) - For error tracking

## Environment Setup

### 1. PostgreSQL Setup

```bash
# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16

# Ubuntu/Debian
sudo apt-get install postgresql-16

# Verify
psql --version
```

### 2. Ruby and Rails

```bash
# Install rbenv (if not already installed)
brew install rbenv

# Install Ruby
rbenv install 3.3.0
rbenv global 3.3.0

# Verify
ruby --version

# Install Rails
gem install rails -v 8.0.3
```

### 3. Python Setup

```bash
# macOS (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv

# Verify
python3 --version
```

### 4. Node.js (for Tailwind)

```bash
# macOS (Homebrew)
brew install node

# Verify
node --version
npm --version
```

## Environment Variables

### Root `.env` (Mosaic directory)

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - Your OpenAI API key
- `AI_SERVICE_API_KEY` - Shared secret between Rails and Python

### Rails `.env` (honeybee directory)

```bash
cd honeybee
cp .env.example .env

# Required:
# - DATABASE_URL
# - AI_SERVICE_URL (http://localhost:8000)
# - AI_SERVICE_API_KEY
# - OPENAI_API_KEY
# - SECRET_KEY_BASE (generate with: rails secret)
```

### Python `.env` (python-ai-service directory)

```bash
cd python-ai-service
cp .env.example .env

# Required:
# - DATABASE_URL (same as Rails)
# - OPENAI_API_KEY
# - RAILS_API_URL (http://localhost:3000)
```

## Running Services

### Option 1: Individual Terminals (Recommended for debugging)

**Terminal 1: Rails Server**
```bash
cd honeybee
rails server
# → http://localhost:3000
```

**Terminal 2: Solid Queue Worker**
```bash
cd honeybee
rails solid_queue:start
# → Processes background jobs
```

**Terminal 3: Python AI Service**
```bash
cd python-ai-service
source venv/bin/activate
fastapi dev app/main.py
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

**Terminal 4: Tailwind CSS Watcher** (optional, only if developing UI)
```bash
cd honeybee
rails tailwindcss:watch
# → Rebuilds CSS on file changes
```

### Option 2: Foreman (All services at once)

```bash
cd honeybee
gem install foreman
foreman start -f Procfile.dev
```

Edit `Procfile.dev` if needed:
```
web: rails server
worker: rails solid_queue:start
css: rails tailwindcss:watch
python: cd ../python-ai-service && source venv/bin/activate && fastapi dev app/main.py
```

## Development Workflow

### 1. Creating a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Create database migration (if needed)
cd honeybee
rails generate migration AddFieldToTable field:type
rails db:migrate

# 3. Create models/controllers
rails generate model MyModel field:type
rails generate controller MyController action1 action2

# 4. Write tests
# Edit test/models/my_model_test.rb
# Edit test/controllers/my_controller_test.rb

# 5. Run tests
rails test

# 6. Check code quality
rubocop
bundle audit

# 7. Commit (Git hooks will run automatically)
git add .
git commit -m "Add my feature"

# 8. Push and create PR
git push origin feature/my-feature
```

### 2. Working with AI Agents (Python)

```bash
cd python-ai-service

# Activate virtual environment
source venv/bin/activate

# Edit agent code
nano app/agents/linkedin_agent.py

# Test agent
pytest tests/test_linkedin_agent.py

# Format code
black app/
isort app/

# Run all tests
pytest

# Deactivate when done
deactivate
```

### 3. Testing Rails ↔ Python Integration

```bash
# 1. Ensure both services are running
# Rails: http://localhost:3000
# Python: http://localhost:8000

# 2. Test Python service directly
curl http://localhost:8000/api/v1/health

# 3. Test from Rails console
cd honeybee
rails console

# Test AI service connection
AiService.healthy?
# => true

# Test evaluation
result = AiService.evaluate_candidate(
  candidate_id: 1,
  resume_url: "https://example.com/resume.pdf"
)

# 4. Test background job
RequestAiEvaluationJob.perform_later(1, 2)

# Check Solid Queue dashboard
# Visit: http://localhost:3000/solid_queue
```

## Testing

### Rails Tests (Minitest)

```bash
cd honeybee

# Run all tests
rails test

# Run specific test file
rails test test/models/candidate_test.rb

# Run specific test
rails test test/models/candidate_test.rb:42

# Run system tests
rails test:system

# With coverage
COVERAGE=true rails test
```

### Python Tests (Pytest)

```bash
cd python-ai-service
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# With coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Code Quality

### Rails (RuboCop)

```bash
cd honeybee

# Check all files
rubocop

# Auto-fix issues
rubocop -a

# Check specific file
rubocop app/models/candidate.rb

# Security scan
bundle audit
brakeman
```

### Python (Black, isort, flake8, mypy)

```bash
cd python-ai-service
source venv/bin/activate

# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Git Hooks (Overcommit)

Git hooks run automatically on commit:

```bash
# Install hooks (already done)
cd honeybee
overcommit --install

# Update hooks
overcommit --sign

# Run hooks manually
overcommit --run
```

## Database Operations

### Migrations

```bash
cd honeybee

# Create migration
rails generate migration AddEmailToUsers email:string

# Run migrations
rails db:migrate

# Rollback last migration
rails db:rollback

# Rollback to specific version
rails db:migrate VERSION=20230101000000

# Check migration status
rails db:migrate:status

# Reset database (CAUTION: destroys data)
rails db:reset
```

### Seeds

```bash
# Run seeds
rails db:seed

# Reset and seed
rails db:reset

# Edit seed file
nano db/seeds.rb
```

### Console Access

```bash
# Rails console
rails console

# Database console (psql)
rails dbconsole

# Production console (when deployed)
RAILS_ENV=production rails console
```

### Useful Database Commands

```ruby
# Rails console

# Create test company
company = Company.create!(name: "Test Corp", ats_provider: "none")

# Create test user
user = User.create!(
  company: company,
  email_address: "test@example.com",
  password: "password123",
  role: :admin
)

# Create test candidate
candidate = Candidate.create!(
  company: company,
  name: "John Doe",
  email: "john@example.com",
  linkedin_url: "https://linkedin.com/in/johndoe",
  github_url: "https://github.com/johndoe"
)

# Test AI evaluation
RequestAiEvaluationJob.perform_later(candidate.id)

# Check swarm decisions
SwarmDecision.all
```

## Troubleshooting

### Rails Won't Start

```bash
# Check database
pg_isready

# Restart PostgreSQL
brew services restart postgresql@16  # macOS

# Check database exists
rails db:version

# Recreate database
rails db:drop db:create db:migrate
```

### Python Service Won't Start

```bash
# Check virtual environment
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Check database connection
# Edit app/db/database.py and test connection
```

### Solid Queue Not Processing Jobs

```bash
# Check queue status
rails solid_queue:status

# Restart worker
rails solid_queue:restart

# Check for failed jobs
rails console
> SolidQueue::Job.failed.count

# Clear failed jobs
> SolidQueue::Job.failed.destroy_all
```

### Rails ↔ Python Communication Issues

```bash
# 1. Check Python service is running
curl http://localhost:8000/api/v1/health

# 2. Check API key matches
# Compare AI_SERVICE_API_KEY in both .env files

# 3. Test from Rails console
rails console
> AiService.agent_status

# 4. Check logs
tail -f honeybee/log/development.log
tail -f python-ai-service/logs/fastapi.log
```

### Port Already in Use

```bash
# Find process using port 3000 (Rails)
lsof -i :3000
kill -9 <PID>

# Find process using port 8000 (Python)
lsof -i :8000
kill -9 <PID>
```

## Production Deployment

### Kamal 2 (Recommended)

```bash
# Setup (first time only)
kamal setup

# Deploy
kamal deploy

# View logs
kamal app logs
kamal app logs --follow

# Rollback
kamal rollback

# SSH into production
kamal app exec -i bash
```

### Docker (Manual)

```bash
# Build Rails image
cd honeybee
docker build -t honeybee:latest .

# Build Python image
cd ../python-ai-service
docker build -t honeybee-ai:latest .

# Run with docker-compose
cd ..
docker-compose up -d
```

### Environment Variables in Production

**Critical:** Change these before deploying:
- `SECRET_KEY_BASE` - Generate with `rails secret`
- `AI_SERVICE_API_KEY` - Use strong random value
- `OPENAI_API_KEY` - Your production OpenAI key
- `SENTRY_DSN` - Your Sentry project DSN

## Useful Commands Reference

### Rails

```bash
rails server                    # Start server
rails console                   # Rails console
rails db:migrate               # Run migrations
rails test                     # Run tests
rails routes                   # Show all routes
rails stats                    # Code statistics
rails about                    # Rails info
```

### Python

```bash
fastapi dev app/main.py        # Dev server (auto-reload)
uvicorn app.main:app          # Production server
pytest                         # Run tests
black app/                    # Format code
```

### Git

```bash
git status                     # Check status
git log --oneline             # Commit history
git diff                      # Show changes
git stash                     # Stash changes
git stash pop                 # Restore stashed changes
```

## Next Steps

- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure production database backups
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Create admin dashboard
- [ ] Implement candidate management UI
- [ ] Build recruiter dashboard

## Resources

- [Rails 8 Guides](https://guides.rubyonrails.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kamal Documentation](https://kamal-deploy.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Solid Queue](https://github.com/rails/solid_queue)

---

**Questions?** Check the main README or `.claude/claude.md` for more context.
