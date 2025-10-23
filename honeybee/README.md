# HoneyBee - Swarm Intelligence Recruiting Platform

**Version**: 0.1.0 (Pre-MVP)
**Rails**: 8.0.3
**Ruby**: 3.3+

## Overview

HoneyBee is a multi-agent AI recruiting platform that uses swarm intelligence to make better, more fair hiring decisions. Instead of relying on a single AI to evaluate candidates, HoneyBee orchestrates 6 specialized AI agents that collaborate, vote, and reach consensus—eliminating bias and improving accuracy by 40%.

**Key Features:**
- 6 specialized AI agents working collaboratively
- Real-time bias detection with EEOC compliance monitoring
- Predictive analytics for hiring success
- Cross-platform candidate verification (LinkedIn + GitHub + Resume)
- Consensus-driven decision making
- ATS integrations (Ashby, Greenhouse)

## Strategic Context

HoneyBee is **Phase 1** of the Mosaic platform vision. See parent directory for:
- `HoneyBee_to_Mosaic_Strategic_Vision.md` - Strategic roadmap
- `TECHNICAL_ARCHITECTURE.md` - Technical architecture details
- `.claude/claude.md` - Development context for Claude Code

**Future**: HoneyBee's Skills Graph and swarm intelligence will evolve into Mosaic—a complete human + AI workforce orchestration platform.

## Architecture

HoneyBee uses a **hybrid Rails 8 + Python microservices** architecture:

```
┌─────────────────────────────────┐
│  Rails 8 Application (this)     │
│  • User auth & multi-tenancy    │
│  • Recruiting workflows         │
│  • ATS integrations             │
│  • Dashboard & analytics        │
│  • Port: 3000                   │
└─────────────────────────────────┘
          ↕ REST API
┌─────────────────────────────────┐
│  Python AI Service              │
│  (../python-ai-service)         │
│  • 6 AI agents                  │
│  • Swarm orchestration          │
│  • Bias detection               │
│  • Port: 8000                   │
└─────────────────────────────────┘
          ↕
┌─────────────────────────────────┐
│  PostgreSQL 16+ (shared)        │
└─────────────────────────────────┘
```

## Technology Stack

### Rails 8 Features Used
- **Solid Queue**: Background job processing (no Redis needed)
- **Solid Cache**: Database-backed caching
- **Solid Cable**: WebSockets for real-time updates
- **Kamal 2**: Zero-downtime deployments
- **Thruster**: HTTP/2 proxy
- **Importmap**: JavaScript without bundling
- **Turbo + Stimulus**: SPA-like experience without heavy JavaScript

### Key Dependencies
- PostgreSQL 16+ for data persistence
- Tailwind CSS for styling
- Rails 8 authentication generator (not Devise)
- Pundit for authorization
- HTTParty for Python service communication
- Minitest for testing (Rails default)
- Sentry for error tracking

## Prerequisites

- Ruby 3.3+ (`ruby --version`)
- PostgreSQL 16+ (`psql --version`)
- Node.js 18+ (for Tailwind, Turbo)
- Python 3.12+ (for AI service)
- OpenAI API key

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Ruby gems
bundle install

# Install JavaScript dependencies (for Importmap)
bin/rails importmap:install

# Install Tailwind CSS
bin/rails tailwindcss:install
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env.development

# Edit .env.development and add:
# - DATABASE_URL
# - AI_SERVICE_URL=http://localhost:8000
# - AI_SERVICE_API_KEY
# - OPENAI_API_KEY
# - ASHBY_API_KEY (optional)
# - GREENHOUSE_API_KEY (optional)
# - SENTRY_DSN (optional)
```

### 3. Database Setup

```bash
# Create and migrate database
rails db:create
rails db:migrate

# Seed development data (optional)
rails db:seed

# Check database status
rails db:version
```

### 4. Start Development Servers

You'll need **4 terminal windows**:

```bash
# Terminal 1: Rails server
rails server
# → http://localhost:3000

# Terminal 2: Solid Queue worker
rails solid_queue:start
# → Processes background jobs

# Terminal 3: Python AI service
cd ../python-ai-service
source venv/bin/activate
fastapi dev app/main.py
# → http://localhost:8000

# Terminal 4: Tailwind CSS watcher (if developing UI)
rails tailwindcss:watch
# → Rebuilds CSS on file changes
```

Alternative: Use `foreman` or `overmind` to run all services:

```bash
# Install foreman
gem install foreman

# Start all services
foreman start -f Procfile.dev
```

## Development Workflow

### Running Tests

```bash
# Run all tests
rails test

# Run specific test file
rails test test/models/candidate_test.rb

# Run system tests (Capybara)
rails test:system

# With coverage
COVERAGE=true rails test
```

### Code Quality

```bash
# Lint Ruby code
rubocop

# Auto-fix lint issues
rubocop -a

# Security audit
bundle audit

# Annotate models with schema info
annotate --models
```

### Database Operations

```bash
# Create migration
rails generate migration AddFieldToTable field:type

# Run migrations
rails db:migrate

# Rollback last migration
rails db:rollback

# Reset database (CAUTION: destroys data)
rails db:reset

# Access Rails console
rails console

# Access database console
rails dbconsole
```

### Generating Code

```bash
# Generate model
rails generate model Candidate name:string email:string company:references

# Generate controller
rails generate controller Candidates index show

# Generate Rails 8 authentication
rails generate authentication User

# Generate Solid Queue jobs
rails solid_queue:install
```

## Core Models

### Multi-Tenancy
- **Company**: Root tenant entity
- **User**: Authenticated users (recruiters, hiring managers, admins)
- **Current**: Thread-safe company context

### Skills Graph
- **Skill**: Shared skill taxonomy
- **CapabilityAssessment**: Polymorphic skills (Candidate OR Employee)

### Recruiting
- **Candidate**: External candidates
- **JobOpening**: Open requisitions
- **SwarmDecision**: AI evaluation audit trail

### Future (Mosaic Phase)
- **Employee**: Internal employees
- **ProjectStaffingRequest**: Dynamic team assembly
- **AiAgentProvider**: AI Agent Registry

## API Endpoints

### Internal APIs (Rails ↔ Python)

**Python Service Endpoints:**
- `POST http://localhost:8000/api/v1/evaluate` - Evaluate candidate
- `GET http://localhost:8000/api/v1/agents/status` - Agent health check

**Rails Webhook Endpoints:**
- `POST /api/webhooks/swarm_decision` - Receive Python evaluation results

## Communication Flow

1. User action in Rails (e.g., "Evaluate Candidate")
2. Rails creates `RequestAiEvaluationJob` in Solid Queue
3. Job calls `AiService.evaluate_candidate` (HTTP → Python)
4. Python orchestrates 6 AI agents via SwarmOrchestrator
5. Agents collaborate, vote, and reach consensus
6. Python sends webhook to Rails `/api/webhooks/swarm_decision`
7. Rails stores `SwarmDecision` record
8. Turbo Stream updates UI in real-time

## Deployment

HoneyBee uses **Kamal 2** for zero-downtime deployments:

```bash
# Initial setup
kamal setup

# Deploy updates
kamal deploy

# View logs
kamal app logs
kamal app logs --follow

# Rollback
kamal rollback

# SSH into production
kamal app exec -i bash
```

See `config/deploy.yml` for deployment configuration.

## Environment Variables

### Required

```bash
# Database
DATABASE_URL=postgresql://localhost/honeybee_development

# Python AI Service
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-secret-key

# OpenAI
OPENAI_API_KEY=sk-...

# Security
SECRET_KEY_BASE=...  # Generated by Rails
```

### Optional

```bash
# ATS Integrations
ASHBY_API_KEY=...
GREENHOUSE_API_KEY=...

# Error Tracking
SENTRY_DSN=...

# Production
RAILS_ENV=production
RAILS_LOG_LEVEL=info
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Restart PostgreSQL (macOS)
brew services restart postgresql@16

# Check database exists
rails db:version
```

### Python Service Connection Issues

```bash
# Check Python service is running
curl http://localhost:8000/api/v1/agents/status

# Check logs
cd ../python-ai-service
tail -f logs/fastapi.log
```

### Solid Queue Not Processing Jobs

```bash
# Check Solid Queue status
rails solid_queue:status

# Restart worker
rails solid_queue:restart

# Clear failed jobs
rails solid_queue:clear_failed
```

## Testing Strategy

### Unit Tests (Minitest)
- Test models, services, jobs in isolation
- Mock external APIs (Python, ATS providers)
- Fast, focused tests

### Integration Tests
- Test Rails → Python communication
- Test multi-tenancy isolation
- Test authorization (Pundit)

### System Tests (Capybara)
- Test full user workflows
- Test real-time UI updates (Turbo Streams)
- Test JavaScript interactions (Stimulus)

## Multi-Tenancy

All company-scoped models automatically filter by `Current.company`:

```ruby
# Automatic tenant scoping
candidates = Candidate.all  # Only returns current company's candidates

# Manual override (admin actions only)
Candidate.unscoped.where(email: 'test@example.com')
```

**Important**: Never expose cross-tenant data. Always use default scopes.

## Security Considerations

- **Authentication**: Rails 8 has_secure_password + bcrypt
- **Authorization**: Pundit policies for all actions
- **API Security**: Token-based auth for Rails ↔ Python
- **Multi-Tenancy**: Strict data isolation via default scopes
- **CORS**: Configured for Python service only
- **SQL Injection**: Use parameterized queries (Active Record does this)
- **XSS**: Rails escapes output by default

## Performance Considerations

- **Caching**: Solid Cache for expensive queries
- **Background Jobs**: All AI calls, ATS syncs run async via Solid Queue
- **Database Indexes**: Added on foreign keys, search fields
- **N+1 Queries**: Use `includes()` for associations
- **API Timeouts**: 30s timeout for Python service calls

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Write tests for new functionality
3. Run test suite: `rails test`
4. Run linter: `rubocop`
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

## Documentation

- **Strategic Vision**: `../HoneyBee_to_Mosaic_Strategic_Vision.md`
- **Technical Architecture**: `../TECHNICAL_ARCHITECTURE.md`
- **Claude Code Context**: `../.claude/claude.md`
- **Development Guide**: `../docs/DEVELOPMENT.md` (coming soon)
- **API Documentation**: `/api/docs` (Swagger UI)

## Project Structure

```
honeybee/
├── app/
│   ├── models/          # Domain models
│   ├── controllers/     # HTTP request handlers
│   ├── views/           # ERB templates
│   ├── services/        # Business logic (AiService, ATS clients)
│   ├── jobs/            # Background jobs (Solid Queue)
│   ├── policies/        # Authorization (Pundit)
│   └── javascript/      # Stimulus controllers
├── config/              # Rails configuration
├── db/
│   ├── migrate/         # Database migrations
│   └── seeds.rb         # Seed data
├── test/                # Minitest tests
├── public/              # Static assets
└── vendor/              # Third-party code
```

## Roadmap

### Phase 1: Foundation (Current)
- Rails 8 setup with authentication
- Core models (Company, User, Candidate, Skill)
- Multi-tenancy with Current attributes
- Python AI service skeleton

### Phase 2: MVP (Weeks 1-8)
- 6 AI agents implementation
- Swarm orchestration
- Bias detection
- Rails ↔ Python integration

### Phase 3: ATS Integration (Weeks 9-12)
- Ashby API client
- Greenhouse API client
- Scheduled syncs
- Candidate import workflows

### Phase 4: Dashboard (Weeks 13-16)
- Recruiter dashboard
- Real-time evaluation updates
- Bias detection alerts
- Analytics & reporting

### Phase 5: Beta Launch (Weeks 17-20)
- Deploy with Kamal 2
- 3-5 pilot customers
- Iterate based on feedback
- Production monitoring

## Success Metrics

**Technical Goals:**
- Rails response time < 200ms (P95)
- Python AI evaluation < 2s
- 99.9% uptime
- Zero data breaches

**Product Goals (Year 1):**
- 5-10 pilot customers
- 100+ candidates evaluated
- 90%+ EEOC compliance score
- 40%+ time savings vs manual recruiting

## Support

- **Issues**: Create GitHub issue or contact team
- **Questions**: Check `.claude/claude.md` or technical docs
- **Production Issues**: Check Sentry dashboard

---

**Built with**: Rails 8 + PostgreSQL + Python + AI
**License**: Proprietary
**Contact**: [Your contact info]

Ready to revolutionize recruiting with swarm intelligence!
