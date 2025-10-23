# Mosaic Project - Claude Code Context

## Project Overview

**Mosaic** is a workforce intelligence platform with a strategic two-phase approach:
- **Phase 1 (HoneyBee)**: Swarm intelligence recruiting platform (MVP, 12-18 months)
- **Phase 2 (Mosaic)**: Complete human + AI workforce orchestration platform (18-36 months)

**Current Stage**: Setting up HoneyBee MVP foundation

## Strategic Vision

See `/HoneyBee_to_Mosaic_Strategic_Vision.md` and `/TECHNICAL_ARCHITECTURE.md` for complete details.

### HoneyBee (Current Focus)
- Multi-agent AI platform for hiring decisions
- 6 specialized AI agents working collaboratively via swarm intelligence
- Bias detection with EEOC compliance monitoring
- Target market: $250B recruiting technology market
- Goal: 5-10 pilot customers, $500K-$1M ARR in Year 1

### Mosaic (Future Vision)
- Complete human + AI workforce orchestration
- Work Intelligence Engine + Unified Skills Graph
- Dynamic staffing with AI agents as workers
- Target market: $2T+ workforce intelligence opportunity

## Technical Architecture

### Hybrid Rails 8 + Python Microservices

```
┌─────────────────────────────────┐
│  Rails 8 - Core Application     │
│  • User auth, multi-tenancy     │
│  • ATS integrations             │
│  • Recruiting workflows         │
│  • Skills Graph data layer      │
│  • Dashboard & analytics        │
│  • Port: 3000                   │
└─────────────────────────────────┘
          ↕ REST API
┌─────────────────────────────────┐
│  Python 3.12+ (FastAPI)         │
│  • 6 specialized AI agents      │
│  • Swarm intelligence           │
│  • Bias detection (EEOC)        │
│  • Predictive analytics         │
│  • Port: 8000                   │
└─────────────────────────────────┘
          ↕ Shared Data
┌─────────────────────────────────┐
│  PostgreSQL 16+ (shared)        │
│  • Single database              │
│  • Rails Active Record          │
│  • Python SQLAlchemy            │
└─────────────────────────────────┘
```

### Technology Stack

**Rails 8 (HoneyBee Core)**
- Rails 8.0.3+ with modern defaults
- PostgreSQL 16+ for persistence
- Solid Queue (job processing, NO Redis needed)
- Solid Cache (database-backed caching)
- Solid Cable (WebSockets)
- Turbo + Stimulus (Hotwire)
- Tailwind CSS
- Rails 8 authentication generator (not Devise)
- Kamal 2 for deployment
- Thruster for HTTP/2 proxy

**Python AI Service**
- FastAPI 0.109+
- Python 3.12+
- OpenAI API for LLM agents
- LangChain for agent orchestration
- SQLAlchemy for database (shared with Rails)
- AsyncPG for PostgreSQL
- Uvicorn server

**Additional Gems/Tools**
- Pundit for authorization
- HTTParty for Rails → Python HTTP
- Annotate for model documentation
- Minitest (Rails default, not RSpec)
- Sentry for error tracking
- rswag for API documentation

## Directory Structure

```
mosaic/                                    # Parent folder (strategic vision)
├── HoneyBee_to_Mosaic_Strategic_Vision.md
├── TECHNICAL_ARCHITECTURE.md
├── .claude/
│   ├── claude.md                         # This file
│   └── commands/                         # Custom slash commands
├── docs/                                 # Additional documentation
├── honeybee/                             # Rails 8 application
│   ├── app/
│   │   ├── models/
│   │   │   ├── company.rb               # Multi-tenant root
│   │   │   ├── user.rb                  # Auth via Rails 8 generator
│   │   │   ├── candidate.rb             # External candidates
│   │   │   ├── employee.rb              # Internal employees (Mosaic phase)
│   │   │   ├── skill.rb                 # Skills Graph
│   │   │   ├── capability_assessment.rb # Polymorphic skills
│   │   │   ├── swarm_decision.rb        # AI evaluation audit
│   │   │   ├── job_opening.rb
│   │   │   └── current.rb               # Multi-tenancy helper
│   │   ├── services/
│   │   │   ├── ai_service.rb            # Rails → Python API client
│   │   │   └── ats/                     # ATS integrations
│   │   ├── jobs/
│   │   │   ├── request_ai_evaluation_job.rb
│   │   │   └── sync_ats_job.rb
│   │   └── controllers/
│   ├── config/
│   ├── db/
│   └── ...
└── python-ai-service/                    # Python AI microservice
    ├── app/
    │   ├── agents/
    │   │   ├── base_agent.py
    │   │   ├── orchestrator.py          # Swarm coordinator
    │   │   ├── linkedin_agent.py        # LinkedIn analysis
    │   │   ├── github_agent.py          # GitHub analysis
    │   │   ├── resume_agent.py          # Resume parsing
    │   │   ├── bias_detection_agent.py  # EEOC compliance
    │   │   ├── predictive_agent.py      # Success forecasting
    │   │   └── consensus.py             # Voting mechanisms
    │   ├── api/
    │   │   ├── evaluate.py              # Main evaluation endpoint
    │   │   └── webhooks.py              # Rails callbacks
    │   ├── db/
    │   │   └── models.py                # SQLAlchemy models
    │   └── main.py
    ├── requirements.txt
    ├── Dockerfile
    └── pytest.ini
```

## Core Domain Models

### Multi-Tenancy Root
- **Company**: Root tenant, has many users, candidates, employees
- **Current**: Thread-safe company context (ActiveSupport::CurrentAttributes)

### Authentication & Authorization
- **User**: Rails 8 authentication generator (bcrypt, has_secure_password)
- Roles: recruiter, hiring_manager, admin
- Authorization via Pundit

### Skills Graph (Foundation for HoneyBee → Mosaic)
- **Skill**: Shared skill taxonomy (technical, soft, domain)
- **CapabilityAssessment**: Polymorphic (Candidate OR Employee)
  - Proficiency levels: beginner, intermediate, advanced, expert
  - Verification sources: ai_agent, github, linkedin, manual
  - Confidence scores from AI

### Recruiting (HoneyBee Phase 1)
- **Candidate**: External candidates
- **JobOpening**: Open requisitions with required skills
- **SwarmDecision**: AI evaluation audit trail
  - agent_votes (JSONB): Which agents voted, scores, reasoning
  - consensus_details: Voting mechanism results
  - bias_flags: EEOC compliance issues

### Workforce (Mosaic Phase 2 - Future)
- **Employee**: Internal employees (uses same CapabilityAssessment)
- **ProjectStaffingRequest**: Dynamic team assembly
- **AiAgentProvider**: AI Agent Registry

## Development Workflow

### Starting Development Servers

```bash
# Terminal 1: Rails app
cd honeybee
bundle install
rails db:create db:migrate
rails server  # localhost:3000

# Terminal 2: Solid Queue worker
cd honeybee
rails solid_queue:start

# Terminal 3: Python AI service
cd python-ai-service
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
fastapi dev app/main.py  # localhost:8000

# Terminal 4: Tailwind CSS (if needed)
cd honeybee
rails tailwindcss:watch
```

### Running Tests

```bash
# Rails tests (Minitest)
cd honeybee
rails test
rails test:system  # Capybara system tests

# Python tests
cd python-ai-service
pytest
```

### Common Commands

```bash
# Database operations
rails db:migrate
rails db:seed
rails db:reset

# Generate models
rails generate model ModelName field:type

# Console access
rails console
rails dbconsole

# Code quality
rubocop
bundle audit
```

## Visual Development

### Design Principles
- Comprehensive design checklist in `/context/design-principles.md`
- Brand style guide in `/context/style-guide.md`
- When making visual (front-end, UI/UX) changes, always refer to these files for guidance

### Quick Visual Check
IMMEDIATELY after implementing any front-end change:
1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md` and `/context/style-guide.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages`

This verification ensures changes meet design standards and user requirements.

### Comprehensive Design Review
Invoke the `@agent-design-review` subagent for thorough design validation when:
- Completing significant UI/UX features
- Before finalizing PRs with visual changes
- Needing comprehensive accessibility and responsiveness testing

## Communication Patterns

### Rails → Python (Async Job Pattern)

1. User action in Rails triggers background job
2. Solid Queue processes `RequestAiEvaluationJob`
3. Job calls `AiService.evaluate_candidate` (HTTP POST to Python)
4. Python processes via SwarmOrchestrator
5. Python sends webhook back to Rails `/api/webhooks/swarm_decision`
6. Rails stores SwarmDecision record
7. Turbo Stream updates UI in real-time

### API Endpoints

**Python Service (FastAPI)**
- `POST /api/v1/evaluate` - Main candidate evaluation
- `GET /api/v1/agents/status` - Health check

**Rails Webhooks**
- `POST /api/webhooks/swarm_decision` - Receive Python results

## Key Design Decisions

### Why Hybrid Rails + Python?
- **Rails**: Speed, conventions, excellent for CRUD, multi-tenancy, integrations
- **Python**: AI ecosystem (OpenAI, LangChain), async processing, ML libraries
- **Shared Database**: Single source of truth, simpler architecture

### Why Rails 8 Specifically?
- **Solid Queue**: No Redis needed for jobs (uses PostgreSQL)
- **Solid Cache**: Database-backed caching
- **Kamal 2**: Modern deployment with zero downtime
- **Built-in auth generator**: Simpler than Devise for our needs
- **Thruster**: HTTP/2 proxy out of the box

### Why Not Devise?
- Rails 8 auth generator is simpler and sufficient for MVP
- Fewer dependencies, more control
- Can add Devise later if needed for advanced features

### Why Minitest over RSpec?
- Rails default, faster setup
- Simpler syntax, faster test runs
- Adequate for MVP, can switch to RSpec if team prefers

## Environment Variables

```bash
# Rails (.env.development)
DATABASE_URL=postgresql://localhost/honeybee_development
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
ASHBY_API_KEY=...
GREENHOUSE_API_KEY=...
SENTRY_DSN=...

# Python (.env)
DATABASE_URL=postgresql://localhost/honeybee_development  # Same as Rails!
RAILS_API_URL=http://localhost:3000
RAILS_API_TOKEN=your-secret-key-here
OPENAI_API_KEY=sk-...  # Same as Rails
```

## Multi-Tenancy Pattern

All company-scoped models use this pattern:

```ruby
# app/models/application_record.rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  def self.tenant_scope
    where(company: Current.company) if column_names.include?('company_id')
  end
end

# app/models/candidate.rb
class Candidate < ApplicationRecord
  belongs_to :company
  default_scope { where(company: Current.company) }
end

# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_current_company

  private

  def set_current_company
    Current.company = current_user.company if current_user
  end
end
```

## Deployment (Kamal 2)

```bash
# Initial setup
kamal setup

# Deploy updates (zero-downtime)
kamal deploy

# Logs
kamal app logs
kamal app logs --follow

# Rollback
kamal rollback
```

## Success Metrics (MVP)

**Technical:**
- Rails responds < 200ms (P95)
- Python AI service < 2s per evaluation
- 99.9% uptime

**Product:**
- 5-10 pilot customers
- 100+ candidates evaluated
- 90%+ EEOC compliance
- 40%+ time savings for recruiters

## Important Notes for Claude Code

1. **Always respect multi-tenancy**: Use `Current.company` in controllers, never expose cross-tenant data
2. **Use Rails 8 conventions**: Solid Queue, Solid Cache, not Sidekiq/Redis
3. **Async by default**: Heavy operations (AI calls, ATS sync) go through background jobs
4. **Security first**: API tokens for Rails ↔ Python, Pundit for authorization
5. **Future-proof for Mosaic**: Skills Graph is polymorphic, supports Candidate AND Employee
6. **Test coverage**: Write tests for business logic, especially multi-tenancy
7. **Document decisions**: Update this file when making architectural changes

## Next Immediate Tasks (MVP Development)

1. Generate Rails 8 authentication
2. Create core models (Company, Candidate, Skill, SwarmDecision)
3. Build Python AI service skeleton
4. Implement Rails → Python communication
5. Build recruiter dashboard
6. Integrate first ATS (Ashby or Greenhouse)
7. Deploy with Kamal 2
8. Launch with 3-5 pilot customers

## Getting Help

- **Strategic Vision**: See `/HoneyBee_to_Mosaic_Strategic_Vision.md`
- **Technical Architecture**: See `/TECHNICAL_ARCHITECTURE.md`
- **Development Guide**: See `/docs/DEVELOPMENT.md`
- **Design Principles**: See `/context/design-principles.md` - S-Tier SaaS design checklist
- **Development Questions**: Check `/docs/` directory or ask in team chat
- **Deployment**: Refer to Kamal 2 documentation

---

**Last Updated**: October 22, 2025
**Project Stage**: Foundation Setup / Pre-MVP
**Target Launch**: Q2 2026
