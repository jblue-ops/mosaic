# HoneyBee → Mosaic Technical Architecture

**Version:** 1.0 | **Date:** Oct 22, 2025 | **Status:** Starting from Scratch

---

## Executive Context

**Product:** HoneyBee (recruiting AI) → Mosaic (workforce orchestration platform)  
**Stage:** Pre-MVP, designing architecture now  
**Timeline:** MVP in 3-6 months, Mosaic in 18-36 months  
**Market:** $250B recruiting → $2T workforce intelligence

---

## Strategic Architecture Decision

### **Hybrid Rails 8 + Python Microservices**

```
┌─────────────────────────────────────────┐
│     RAILS 8 - Core Application          │
│  • User auth, multi-tenancy             │
│  • ATS integrations (Ashby, Greenhouse) │
│  • Recruiting workflows & scheduling    │
│  • Skills Graph data layer              │
│  • Dashboard & analytics                │
│  • Solid Queue (built-in job queue)     │
│  • Solid Cache (built-in caching)       │
└─────────────────────────────────────────┘
              ↕ REST API
┌─────────────────────────────────────────┐
│   PYTHON 3.12+ (FastAPI 0.109+)         │
│  • 6 specialized AI agents              │
│  • Swarm intelligence & consensus       │
│  • Bias detection (EEOC compliance)     │
│  • Predictive analytics                 │
└─────────────────────────────────────────┘
              ↕ Shared Data
┌─────────────────────────────────────────┐
│         Infrastructure                  │
│  • PostgreSQL 16+ (shared)              │
│  • Redis 7+ (optional, agent comms)     │
│  • Solid Queue (Rails 8 built-in)       │
│  • Solid Cache (Rails 8 built-in)       │
└─────────────────────────────────────────┘
```

**Rationale:** Rails 8 for speed with built-in modern features, Python for AI, clear separation, future-proof for Mosaic.

---

## Rails 8 Application Structure

### Core Stack (Rails 8 Defaults + Additions)
```ruby
# Gemfile essentials
gem 'rails', '~> 8.0'
gem 'pg', '~> 1.5'                     # PostgreSQL
gem 'solid_queue', '~> 1.0'            # Built-in: replaces Sidekiq
gem 'solid_cache', '~> 1.0'            # Built-in: replaces Redis for cache
gem 'devise', '~> 4.9'                 # Authentication
gem 'pundit', '~> 2.3'                 # Authorization
gem 'faraday', '~> 2.9'                # HTTP client for Python
gem 'propshaft'                        # Built-in: asset pipeline
gem 'importmap-rails'                  # Built-in: JS without bundler
gem 'turbo-rails', '~> 2.0'            # Hotwire built-in
gem 'stimulus-rails'                   # Hotwire built-in
gem 'thruster'                         # Built-in: HTTP/2 proxy (Rails 8)
gem 'kamal', '~> 2.0'                  # Built-in: deployment (Rails 8)
```

**Rails 8 Key Features Used:**
- **Solid Queue**: No need for Sidekiq, Redis optional
- **Solid Cache**: Database-backed caching, simpler infrastructure
- **Thruster**: Fast HTTP/2 proxy server
- **Kamal 2**: Zero-downtime deployments
- **Authentication Generator**: `rails generate authentication`

### Domain Models (Phase 1: HoneyBee)

```ruby
# app/models/company.rb - Multi-tenant isolation
has_many :users
has_many :candidates
has_many :job_openings
has_many :employees  # For Mosaic phase

# app/models/user.rb - Recruiters, hiring managers, admins
belongs_to :company
enum role: { recruiter: 0, hiring_manager: 1, admin: 2 }
# Rails 8: Use `rails generate authentication` for secure defaults

# app/models/candidate.rb - External candidates
belongs_to :company
has_many :job_applications
has_many :capability_assessments, as: :person
has_many :swarm_decisions
jsonb :resume_data
string :linkedin_url, :github_url

# app/models/employee.rb - Internal employees (Mosaic phase)
belongs_to :company
has_many :capability_assessments, as: :person
has_many :project_assignments
jsonb :internal_profile

# app/models/job_opening.rb - Open requisitions
belongs_to :company
has_many :interview_stages
has_many :job_applications
jsonb :required_skills  # Array of skill IDs + proficiency levels

# app/models/interview_stage.rb - Multi-stage workflows
belongs_to :job_opening
has_many :interview_assignments
enum stage_type: { screening: 0, technical: 1, onsite: 2, final: 3 }
integer :sequence_order
jsonb :requirements  # Prerequisites, duration

# app/models/interview_assignment.rb - Interviewer coordination
belongs_to :interview_stage
belongs_to :candidate
belongs_to :interviewer, class_name: 'User'
datetime :scheduled_at
enum status: { pending: 0, scheduled: 1, completed: 2 }

# app/models/skill.rb - Skills Graph (HoneyBee → Mosaic)
string :name, null: false, index: true
string :category  # 'technical', 'soft', 'domain'
jsonb :metadata

# app/models/capability_assessment.rb - Verified skills
belongs_to :person, polymorphic: true  # Candidate OR Employee
belongs_to :skill
enum proficiency: { beginner: 0, intermediate: 1, advanced: 2, expert: 3 }
string :verified_by  # 'ai_agent', 'github', 'linkedin', 'manual'
jsonb :evidence
float :confidence_score  # From AI agents

# app/models/swarm_decision.rb - AI evaluation audit trail
belongs_to :candidate
belongs_to :job_opening, optional: true
string :decision_type  # 'initial_screen', 'technical_eval'
jsonb :agent_votes  # Which agents voted, their scores
jsonb :consensus_details  # Voting mechanism used
float :overall_confidence
jsonb :bias_flags  # EEOC compliance alerts
datetime :evaluated_at
```

### Database Schema (PostgreSQL 16+)

```ruby
# db/migrate/XXXXXX_create_core_schema.rb
class CreateCoreSchema < ActiveRecord::Migration[8.0]
  def change
    # Companies - Multi-tenant root
    create_table :companies do |t|
      t.string :name, null: false
      t.string :ats_provider  # 'ashby', 'greenhouse'
      t.jsonb :ats_credentials, default: {}
      t.timestamps
    end
    
    # Users - Authentication via Rails 8 generator
    # rails generate authentication User
    # Adds: email, password_digest, etc.
    
    # Skills Graph - Core of HoneyBee → Mosaic
    create_table :skills do |t|
      t.string :name, null: false, index: true
      t.string :category
      t.jsonb :metadata, default: {}
      t.timestamps
    end
    
    # Capability Assessments - Polymorphic
    create_table :capability_assessments do |t|
      t.references :person, polymorphic: true, null: false
      t.references :skill, null: false, foreign_key: true
      t.integer :proficiency, default: 0
      t.string :verified_by
      t.jsonb :evidence, default: {}
      t.float :confidence_score
      t.timestamps
      
      t.index [:person_type, :person_id, :skill_id], 
              unique: true, 
              name: 'idx_unique_capability_per_person_skill'
    end
    
    # Swarm Decisions - AI audit trail
    create_table :swarm_decisions do |t|
      t.references :candidate, null: false, foreign_key: true
      t.references :job_opening, foreign_key: true
      t.string :decision_type
      t.jsonb :agent_votes, default: {}
      t.jsonb :consensus_details, default: {}
      t.float :overall_confidence
      t.jsonb :bias_flags, default: []
      t.datetime :evaluated_at
      t.timestamps
      
      t.index :evaluated_at
      t.index :overall_confidence
    end
    
    # Candidates, JobOpenings, InterviewStages, etc.
    # (Standard Rails patterns, omitted for brevity)
  end
end
```

---

## Background Jobs (Solid Queue - Rails 8)

```ruby
# app/jobs/sync_ats_job.rb
class SyncAtsJob < ApplicationJob
  queue_as :default
  
  def perform(company_id)
    company = Company.find(company_id)
    AtsService.new(company).sync_candidates
  end
end

# app/jobs/request_ai_evaluation_job.rb
class RequestAiEvaluationJob < ApplicationJob
  queue_as :ai_processing
  retry_on Faraday::Error, wait: 5.seconds, attempts: 3
  
  def perform(candidate_id, job_opening_id)
    candidate = Candidate.find(candidate_id)
    
    # Call Python AI service
    response = AiService.evaluate_candidate(
      candidate_id: candidate.id,
      resume_url: candidate.resume_url,
      job_opening_id: job_opening_id
    )
    
    # Store swarm decision
    SwarmDecision.create!(
      candidate: candidate,
      job_opening_id: job_opening_id,
      agent_votes: response['agent_votes'],
      consensus_details: response['consensus'],
      overall_confidence: response['confidence'],
      bias_flags: response['bias_alerts'],
      evaluated_at: Time.current
    )
  end
end
```

**Solid Queue Benefits (Rails 8):**
- No Redis required for job queue (uses PostgreSQL)
- Built-in recurring jobs
- Web UI at `/solid_queue`
- Multi-threaded workers

---

## Python AI Services (FastAPI)

### Stack
```python
# requirements.txt (Python 3.12+)
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
sqlalchemy==2.0.25
asyncpg==0.29.0           # PostgreSQL async driver
openai==1.12.0            # AI agents
langchain==0.1.6          # Agent orchestration
redis==5.0.1              # Optional: agent communication
httpx==0.26.0             # Async HTTP client
```

### Project Structure
```
python-ai-service/
├── app/
│   ├── agents/
│   │   ├── base_agent.py              # Abstract base
│   │   ├── orchestrator.py            # Swarm coordinator
│   │   ├── linkedin_agent.py          # LinkedIn analysis
│   │   ├── github_agent.py            # GitHub analysis
│   │   ├── resume_agent.py            # Resume parsing
│   │   ├── bias_detection_agent.py    # EEOC compliance
│   │   ├── predictive_agent.py        # Success forecasting
│   │   └── consensus.py               # Voting mechanisms
│   ├── api/
│   │   ├── evaluate.py                # Main evaluation endpoint
│   │   └── webhooks.py                # Rails callbacks
│   ├── db/
│   │   └── models.py                  # SQLAlchemy (shared with Rails)
│   └── main.py
├── requirements.txt
└── Dockerfile
```

### Key API Endpoints

```python
# app/api/evaluate.py
from fastapi import APIRouter, HTTPException
from app.agents.orchestrator import SwarmOrchestrator

router = APIRouter()

@router.post("/api/v1/evaluate")
async def evaluate_candidate(request: EvaluationRequest):
    """
    Main endpoint: Rails calls this to evaluate candidates
    
    Returns:
      - agent_votes: dict of agent_name -> {score, confidence, reasoning}
      - consensus: voting mechanism results
      - overall_confidence: float 0-1
      - bias_alerts: list of EEOC compliance issues
    """
    orchestrator = SwarmOrchestrator()
    
    result = await orchestrator.evaluate_candidate(
        candidate_id=request.candidate_id,
        resume_url=request.resume_url,
        linkedin_url=request.linkedin_url,
        github_url=request.github_url,
        job_opening_id=request.job_opening_id
    )
    
    # Optionally: Send webhook back to Rails
    await notify_rails_completion(result)
    
    return result

@router.get("/api/v1/agents/status")
async def agent_status():
    """Health check: show which agents are active"""
    orchestrator = SwarmOrchestrator()
    return {
        "active_agents": orchestrator.get_agent_status(),
        "swarm_metrics": orchestrator.get_metrics()
    }
```

---

## Rails ↔ Python Communication

### Rails Service Object Pattern

```ruby
# app/services/ai_service.rb
class AiService
  include HTTParty
  base_uri ENV.fetch('AI_SERVICE_URL', 'http://localhost:8000')
  
  def self.evaluate_candidate(candidate_id:, resume_url:, job_opening_id:)
    response = post(
      '/api/v1/evaluate',
      body: {
        candidate_id: candidate_id,
        resume_url: resume_url,
        job_opening_id: job_opening_id
      }.to_json,
      headers: { 
        'Content-Type' => 'application/json',
        'Authorization' => "Bearer #{ENV['AI_SERVICE_API_KEY']}"
      },
      timeout: 30
    )
    
    raise AiServiceError, response.body unless response.success?
    
    JSON.parse(response.body)
  end
  
  class AiServiceError < StandardError; end
end
```

### Async Pattern (Recommended)

```ruby
# Rails controller
class CandidatesController < ApplicationController
  def evaluate
    candidate = current_company.candidates.find(params[:id])
    
    # Queue async job (Solid Queue)
    RequestAiEvaluationJob.perform_later(
      candidate.id, 
      params[:job_opening_id]
    )
    
    # Immediate response, job runs in background
    render json: { 
      status: 'processing',
      message: 'AI evaluation queued'
    }
  end
  
  def evaluation_status
    candidate = current_company.candidates.find(params[:id])
    decision = candidate.swarm_decisions.latest
    
    render json: decision
  end
end
```

### Webhook from Python → Rails

```python
# Python sends result back to Rails
async def notify_rails_completion(evaluation_result):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{RAILS_URL}/api/webhooks/swarm_decision",
            json=evaluation_result,
            headers={"Authorization": f"Bearer {RAILS_API_TOKEN}"}
        )
```

```ruby
# app/controllers/webhooks_controller.rb
class WebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token
  before_action :verify_api_token
  
  def swarm_decision
    # Python AI service sends results here
    SwarmDecision.create!(swarm_decision_params)
    
    # Broadcast to user via Turbo Stream
    Turbo::StreamsChannel.broadcast_update_to(
      "candidate_#{params[:candidate_id]}_evaluations",
      target: "evaluation_status",
      partial: "candidates/evaluation_status",
      locals: { decision: SwarmDecision.last }
    )
    
    head :ok
  end
  
  private
  
  def verify_api_token
    authenticate_or_request_with_http_token do |token, options|
      ActiveSupport::SecurityUtils.secure_compare(
        token, 
        ENV['AI_SERVICE_API_KEY']
      )
    end
  end
end
```

---

## ATS Integrations (Ashby, Greenhouse)

### Service Pattern

```ruby
# app/services/ats/base_client.rb
module Ats
  class BaseClient
    def initialize(company)
      @company = company
      @credentials = company.ats_credentials
    end
    
    def sync_candidates
      raise NotImplementedError
    end
    
    def sync_job_openings
      raise NotImplementedError
    end
  end
end

# app/services/ats/ashby_client.rb
module Ats
  class AshbyClient < BaseClient
    include HTTParty
    base_uri 'https://api.ashbyhq.com/v1'
    
    def sync_candidates
      response = self.class.get(
        '/candidates',
        headers: auth_headers
      )
      
      response['candidates'].each do |ashby_candidate|
        sync_candidate(ashby_candidate)
      end
    end
    
    private
    
    def sync_candidate(ashby_data)
      candidate = @company.candidates.find_or_initialize_by(
        external_id: ashby_data['id'],
        ats_provider: 'ashby'
      )
      
      candidate.update!(
        name: ashby_data['name'],
        email: ashby_data['email'],
        resume_url: ashby_data['resumeUrl'],
        linkedin_url: ashby_data['linkedInUrl']
      )
    end
    
    def auth_headers
      { 'Authorization' => "Bearer #{@credentials['api_key']}" }
    end
  end
end

# app/services/ats/greenhouse_client.rb
# Similar pattern for Greenhouse API
```

### Scheduled Sync Job

```ruby
# app/jobs/scheduled_ats_sync_job.rb
class ScheduledAtsSyncJob < ApplicationJob
  queue_as :ats_sync
  
  # Solid Queue: recurring job configuration
  # config/recurring.yml
  # scheduled_ats_sync:
  #   class: ScheduledAtsSyncJob
  #   schedule: "*/15 * * * *"  # Every 15 minutes
  
  def perform
    Company.where.not(ats_provider: nil).find_each do |company|
      SyncAtsJob.perform_later(company.id)
    end
  end
end
```

---

## Deployment (Kamal 2 - Rails 8)

### Configuration

```yaml
# config/deploy.yml (Kamal 2)
service: honeybee
image: your-org/honeybee

servers:
  web:
    hosts:
      - 192.168.1.1
    labels:
      traefik.http.routers.honeybee.rule: Host(`honeybee.app`)
    options:
      network: "private"
  
  ai_service:
    hosts:
      - 192.168.1.2
    cmd: uvicorn app.main:app --host 0.0.0.0 --port 8000
    labels:
      traefik.http.routers.ai.rule: Host(`ai.honeybee.app`)

registry:
  username: your-username
  password:
    - KAMAL_REGISTRY_PASSWORD

env:
  secret:
    - DATABASE_URL
    - AI_SERVICE_URL
    - AI_SERVICE_API_KEY
    - OPENAI_API_KEY

accessories:
  db:
    image: postgres:16-alpine
    host: 192.168.1.3
    port: 5432
    env:
      secret:
        - POSTGRES_PASSWORD
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
```

### Deploy Commands

```bash
# Initial setup
kamal setup

# Deploy updates (zero-downtime)
kamal deploy

# Check status
kamal app logs
kamal accessory logs db

# Rollback
kamal rollback
```

---

## Development Workflow (MVP - First 12 Weeks)

### Week 1-2: Rails Foundation
```bash
rails new honeybee --database=postgresql --css=tailwind
cd honeybee

# Generate authentication (Rails 8)
rails generate authentication User

# Generate core models
rails generate model Company name:string ats_provider:string ats_credentials:jsonb
rails generate model Candidate company:references name:string email:string
rails generate model JobOpening company:references title:string
rails generate model Skill name:string:index category:string metadata:jsonb
rails generate model SwarmDecision candidate:references job_opening:references

# Setup Solid Queue (Rails 8 default)
rails solid_queue:install

rails db:create db:migrate
```

### Week 3-4: Python AI Service (Parallel)
```bash
mkdir python-ai-service && cd python-ai-service
python -m venv venv
source venv/bin/activate

# Create FastAPI skeleton
pip install fastapi uvicorn openai langchain sqlalchemy asyncpg
fastapi dev app/main.py  # Runs on localhost:8000
```

### Week 5-6: Integration
- Connect Rails → Python API
- Implement `AiService` and `RequestAiEvaluationJob`
- Test full workflow: Candidate → Job → Evaluation

### Week 7-8: ATS Integration
- Ashby API client implementation
- Scheduled sync jobs (Solid Queue recurring)
- Candidate import workflows

### Week 9-10: Dashboard & UI
- Recruiter dashboard (Turbo/Stimulus)
- Real-time evaluation updates
- Bias detection alerts

### Week 11-12: Beta Testing
- Deploy with Kamal 2
- Pilot with 3-5 customers
- Iterate based on feedback

---

## Mosaic Evolution Path (Phase 2: Months 13-24)

### Database Additions

```ruby
# Add employee tables (internal mobility)
rails generate model Employee company:references name:string email:string internal_profile:jsonb
rails generate model ProjectStaffingRequest company:references project_name:string required_capabilities:jsonb

# Expand capability_assessments to support employees
# Already polymorphic! Just add Employee records

# New: AI Agent Registry (for Mosaic phase)
rails generate model AiAgentProvider name:string capabilities:jsonb api_endpoint:string
rails generate model AiAgentDeployment company:references agent_provider:references status:integer
```

### Architecture Evolution

```
YEAR 1: HoneyBee              YEAR 2: Mosaic
┌──────────────────┐          ┌──────────────────────────┐
│  Rails (Core)    │          │  Rails (Core + Platform) │
│  • Recruiting    │    →     │  • Recruiting            │
│  • ATS Sync      │          │  • Internal Mobility     │
│                  │          │  • Project Staffing      │
└──────────────────┘          │  • AI Agent Registry     │
        ↕                     └──────────────────────────┘
┌──────────────────┐                      ↕
│  Python (AI)     │          ┌──────────────────────────┐
│  • 6 Agents      │    →     │  Python (AI + Platform)  │
│  • Swarm Intel   │          │  • 6+ Agents             │
└──────────────────┘          │  • Work Decomposition    │
                              │  • Dynamic Team Assembly │
                              └──────────────────────────┘
```

---

## Key Technology Decisions Summary

| **Component** | **Technology** | **Why** |
|---------------|----------------|---------|
| **Web Framework** | Rails 8 | Speed, conventions, built-in modern features |
| **Database** | PostgreSQL 16+ | JSONB, full-text search, shared Rails+Python |
| **Job Queue** | Solid Queue (Rails 8) | Built-in, no Redis required |
| **Cache** | Solid Cache (Rails 8) | Built-in, DB-backed |
| **AI Service** | FastAPI (Python 3.12+) | Async, fast, AI ecosystem |
| **AI Agents** | OpenAI + LangChain | Best-in-class LLM + orchestration |
| **Deployment** | Kamal 2 | Zero-downtime, Rails 8 built-in |
| **Real-time** | Turbo Streams | Hotwire, no separate WebSocket server |
| **Frontend** | Importmap + Stimulus | Rails 8 defaults, simple |

---

## Critical Implementation Notes

### Authentication (Rails 8 Generator)
```bash
# Use Rails 8's new authentication generator
rails generate authentication User
# Creates: User model, SessionsController, views, password reset
# Modern: Uses has_secure_password, no Devise needed (but you can still use Devise)
```

### Multi-Tenancy Pattern
```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  before_action :set_current_company
  
  private
  
  def set_current_company
    Current.company = current_user.company
  end
end

# app/models/current.rb (Rails 8 pattern)
class Current < ActiveSupport::CurrentAttributes
  attribute :company
end

# Usage in models:
class Candidate < ApplicationRecord
  belongs_to :company
  default_scope { where(company: Current.company) }
end
```

### Shared Database Access (Rails + Python)

```python
# Python reads same PostgreSQL via SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Define models matching Rails schema
class SwarmDecision(Base):
    __tablename__ = "swarm_decisions"
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    # ... matches Rails schema exactly
```

---

## Testing Strategy

### Rails (RSpec + System Tests)
```ruby
# spec/system/candidate_evaluation_spec.rb
RSpec.describe "Candidate Evaluation", type: :system do
  it "evaluates candidate with AI" do
    # Mock Python AI service response
    stub_request(:post, "http://localhost:8000/api/v1/evaluate")
      .to_return(body: { confidence: 0.85 }.to_json)
    
    visit candidate_path(candidate)
    click_button "Evaluate with AI"
    
    expect(page).to have_content "AI Evaluation: 85%"
  end
end
```

### Python (Pytest)
```python
# tests/test_orchestrator.py
import pytest
from app.agents.orchestrator import SwarmOrchestrator

@pytest.mark.asyncio
async def test_swarm_evaluation():
    orchestrator = SwarmOrchestrator()
    result = await orchestrator.evaluate_candidate(
        candidate_id=1,
        resume_url="https://example.com/resume.pdf"
    )
    
    assert result['overall_confidence'] > 0
    assert len(result['agent_votes']) == 6
```

---

## Security Considerations

### API Authentication
```ruby
# Rails generates API tokens for Python service
class ApiToken < ApplicationRecord
  belongs_to :company
  
  before_create :generate_token
  
  private
  
  def generate_token
    self.token = SecureRandom.hex(32)
  end
end

# Verify in webhooks
def verify_api_token
  token = request.headers['Authorization']&.split(' ')&.last
  ApiToken.find_by(token: token) || head(:unauthorized)
end
```

### Multi-Tenant Data Isolation
```ruby
# Strong parameter filtering
def candidate_params
  params.require(:candidate).permit(:name, :email, :resume_url)
    .merge(company: Current.company)  # Force current company
end

# Database constraints
add_foreign_key :candidates, :companies, on_delete: :cascade
```

---

## Environment Variables

```bash
# .env (Rails)
DATABASE_URL=postgresql://localhost/honeybee_dev
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-secret-key
OPENAI_API_KEY=sk-...
ASHBY_API_KEY=...
GREENHOUSE_API_KEY=...

# .env (Python)
DATABASE_URL=postgresql://localhost/honeybee_dev  # Same as Rails
RAILS_API_URL=http://localhost:3000
RAILS_API_TOKEN=your-secret-key
OPENAI_API_KEY=sk-...  # Same as Rails
```

---

## Quick Start Commands

```bash
# Terminal 1: Rails app
rails new honeybee --database=postgresql --css=tailwind
cd honeybee
rails db:create db:migrate
rails server  # localhost:3000

# Terminal 2: Python AI service
mkdir python-ai-service && cd python-ai-service
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn openai
fastapi dev app/main.py  # localhost:8000

# Terminal 3: Solid Queue worker (Rails 8)
cd honeybee
rails solid_queue:start
```

---

## Success Metrics (MVP)

**Technical:**
- ✅ Rails app responds < 200ms (P95)
- ✅ Python AI service responds < 2s for evaluation
- ✅ Solid Queue processes jobs < 10s (P95)
- ✅ 99.9% uptime for both services

**Product:**
- ✅ 5-10 pilot customers using HoneyBee
- ✅ 100+ candidates evaluated via swarm intelligence
- ✅ 90%+ EEOC compliance on bias detection
- ✅ 40%+ time savings for recruiters

---

## Next Steps for Claude Code

**To start building HoneyBee:**

1. **Create Rails 8 app:**
```bash
rails new honeybee --database=postgresql --css=tailwind
cd honeybee
rails generate authentication User
```

2. **Generate core models:**
```bash
rails generate model Company name:string ats_provider:string
rails generate model Candidate company:references name:string email:string
rails generate model Skill name:string category:string
rails generate model SwarmDecision candidate:references confidence:float
```

3. **Build Python AI service** (parallel development)

4. **Connect via Faraday + Solid Queue jobs**

5. **Iterate toward pilot customers**

---

**This architecture is optimized for:**
- ⚡ **Speed to market** (Rails 8 conventions)
- 🤖 **AI-first** (Python microservice)
- 🔮 **Future-proof** (Mosaic evolution path)
- 🧑‍💻 **Claude Code friendly** (clear conventions, minimal decisions)

Ready to start building!