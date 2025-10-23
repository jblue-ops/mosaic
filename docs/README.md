# Mosaic / HoneyBee Documentation

Welcome to the Mosaic project documentation. This directory contains additional documentation and resources for developing HoneyBee and the future Mosaic platform.

## Core Documentation

### Strategic & Architecture Documents (Parent Directory)

- **[HoneyBee to Mosaic Strategic Vision](../HoneyBee_to_Mosaic_Strategic_Vision.md)**
  - Product vision and roadmap
  - Market opportunity ($250B → $2T+)
  - Go-to-market strategy
  - Investor positioning
  - Development milestones

- **[Technical Architecture](../TECHNICAL_ARCHITECTURE.md)**
  - Hybrid Rails 8 + Python architecture
  - Core models and database schema
  - Rails ↔ Python communication patterns
  - Deployment strategy (Kamal 2)
  - Development workflow

- **[Claude Code Context](../.claude/claude.md)**
  - Project context for Claude Code sessions
  - Technology stack details
  - Development patterns
  - Multi-tenancy implementation
  - Common commands and workflows

### Application Documentation

- **[HoneyBee README](../honeybee/README.md)**
  - Rails application setup
  - Development workflow
  - Testing strategy
  - Deployment instructions

## Additional Documentation

### Development Guides
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Comprehensive development guide
  - Quick start instructions
  - Environment setup
  - Running services
  - Testing workflows
  - Troubleshooting
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - S-Tier SaaS design checklist
  - Design system foundation
  - Component library
  - HoneyBee-specific patterns
  - Accessibility guidelines
  - Performance targets
- `CONTRIBUTING.md` - Contribution guidelines (coming soon)
- `TESTING.md` - Testing best practices (coming soon)
- `DEPLOYMENT.md` - Production deployment guide (coming soon)

### API Documentation
- `API.md` - Rails API documentation
- `PYTHON_API.md` - Python service API documentation
- `ATS_INTEGRATIONS.md` - ATS provider integration guides

### Architecture Decision Records (ADRs)
- `adr/001-hybrid-rails-python-architecture.md`
- `adr/002-rails-8-over-devise.md`
- `adr/003-solid-queue-over-sidekiq.md`
- `adr/004-minitest-over-rspec.md`

### Domain Documentation
- `MULTI_TENANCY.md` - Multi-tenancy implementation guide
- `SKILLS_GRAPH.md` - Skills Graph architecture
- `SWARM_INTELLIGENCE.md` - AI agent swarm architecture
- `BIAS_DETECTION.md` - EEOC compliance and bias detection

### Operations
- `MONITORING.md` - Production monitoring guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `SECURITY.md` - Security best practices
- `PERFORMANCE.md` - Performance optimization guide

## Quick Links

### Getting Started
1. Read [Strategic Vision](../HoneyBee_to_Mosaic_Strategic_Vision.md) to understand the product vision
2. Read [Technical Architecture](../TECHNICAL_ARCHITECTURE.md) to understand the technical approach
3. Follow setup instructions in [HoneyBee README](../honeybee/README.md)
4. Check [Claude Code Context](../.claude/claude.md) for development patterns

### For Developers
- **Setup**: See [HoneyBee README](../honeybee/README.md#setup-instructions)
- **Testing**: See [HoneyBee README](../honeybee/README.md#testing-strategy)
- **Code Quality**: See [HoneyBee README](../honeybee/README.md#code-quality)

### For Product/Business
- **Vision**: See [Strategic Vision](../HoneyBee_to_Mosaic_Strategic_Vision.md)
- **Roadmap**: See [Strategic Vision - Development Roadmap](../HoneyBee_to_Mosaic_Strategic_Vision.md#development-roadmap)
- **Success Metrics**: See [Strategic Vision - Success Metrics](../HoneyBee_to_Mosaic_Strategic_Vision.md#success-metrics-by-phase)

## External Resources

### Rails 8
- [Rails 8 Release Notes](https://rubyonrails.org/2024/11/7/rails-8-0-0-released)
- [Solid Queue Documentation](https://github.com/rails/solid_queue)
- [Kamal 2 Documentation](https://kamal-deploy.org/)
- [Rails Guides](https://guides.rubyonrails.org/)

### Python & AI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

### Deployment & Operations
- [Kamal 2 Documentation](https://kamal-deploy.org/)
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Docker Documentation](https://docs.docker.com/)

## MCP (Model Context Protocol) Servers

### Available MCPs
- **Chrome DevTools MCP**: For web application testing and debugging
- **Context7 MCP**: For accessing library documentation (Rails, FastAPI, etc.)

### Recommended MCPs for This Project
1. **Context7** - Access Rails and FastAPI documentation while coding
2. **Chrome DevTools** - Test and debug the Rails web application
3. **Playwright** (optional) - For advanced browser automation testing

### Enabling MCPs
See Claude Code documentation for MCP configuration.

## Project Structure Overview

```
mosaic/                                    # Root project directory
├── docs/                                 # This directory
│   └── README.md                         # This file
├── .claude/                              # Claude Code configuration
│   ├── claude.md                         # Project context
│   └── commands/                         # Custom slash commands
├── honeybee/                             # Rails 8 application
│   ├── app/                             # Rails app code
│   ├── config/                          # Rails configuration
│   ├── db/                              # Database migrations
│   ├── test/                            # Minitest tests
│   └── README.md                        # Rails app documentation
├── python-ai-service/                    # Python AI microservice (to be created)
│   ├── app/                             # FastAPI application
│   ├── tests/                           # Pytest tests
│   └── requirements.txt                 # Python dependencies
├── HoneyBee_to_Mosaic_Strategic_Vision.md
└── TECHNICAL_ARCHITECTURE.md
```

## Contributing

When adding new documentation:

1. **Placement**:
   - Strategic/business docs → Root directory
   - Technical guides → `docs/` directory
   - Application-specific → `honeybee/docs/` or `python-ai-service/docs/`

2. **Format**:
   - Use Markdown (.md)
   - Include table of contents for long documents
   - Add code examples where applicable
   - Link to related documents

3. **Naming**:
   - Use UPPERCASE for root-level docs (README.md, CONTRIBUTING.md)
   - Use lowercase-with-hyphens for subdirectory docs (api-guide.md)

4. **Maintenance**:
   - Update this index when adding new documents
   - Keep docs in sync with code changes
   - Archive outdated docs to `docs/archive/`

## Support

- **Development Questions**: Check docs or `.claude/claude.md`
- **Production Issues**: See `TROUBLESHOOTING.md` (coming soon)
- **Feature Requests**: Create GitHub issue
- **Security Issues**: Contact team directly

---

**Last Updated**: October 22, 2025
**Status**: Initial Setup
