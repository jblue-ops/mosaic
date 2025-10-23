# Context Documentation

This directory contains comprehensive design and style documentation for the HoneyBee/Mosaic project.

## 📁 Files

### `design-principles.md` (21KB)
**S-Tier SaaS Design Checklist**

Comprehensive front-end design principles covering:
- Visual hierarchy and layout
- Typography and readability
- Color and contrast
- Component design
- Accessibility (WCAG AA compliance)
- Responsive design
- Performance optimization
- User experience patterns

**When to reference:**
- Before implementing any UI/UX feature
- During code reviews of front-end changes
- When making visual design decisions
- During accessibility audits

### `style-guide.md` (49KB)
**Strategic Style Guide for Recruiting & Workforce Planning SaaS**

Comprehensive brand voice, messaging, and technical guidelines based on research from 34 industry leaders (Greenhouse, Anthropic, Stripe, Google, Microsoft, Atlassian, etc.)

**Sections:**
1. **Foundational Principles**
   - Core Voice: Expert, Empowering, Clear
   - Tone Spectrum: Guiding ↔ Direct, Enthusiastic ↔ Matter-of-fact, Human ↔ Formal
   - Content Mission & Goals

2. **Content & Messaging Guidelines**
   - Grammar and Mechanics (Oxford comma, sentence case, active voice)
   - UI and UX Writing (button copy, error messages, empty states)
   - **AI Features Communication** (context engineering, agent transparency)
   - Inclusive Communication (person-first language, DE&I standards)

3. **Visual & Brand Identity**
   - Logo Usage
   - Color Palette (primary, secondary, semantic, accessibility)
   - Typography (scale, hierarchy, line spacing)
   - Imagery and Iconography

4. **Technical & Platform Guidelines**
   - API Documentation standards
   - AI/LLM Integration (Skills, Tools, multi-modal inputs)
   - Design System Architecture (tokens, components)

**When to reference:**
- Writing any user-facing copy (UI, marketing, docs)
- Designing AI agent interactions
- Creating error messages or notifications
- Building API documentation
- Implementing design system components
- Ensuring inclusive, accessible communication

## 🎯 Quick Reference

### Voice Attributes (Never Change)
- **Expert** (not arrogant) - Confident, credible, data-driven
- **Empowering** (not reliant) - Inspiring, supportive partner
- **Clear** (not ambiguous) - Simple, direct, jargon-free

### Tone Matrix (Adapt to Context)

| User Feeling | Tone | Example |
|--------------|------|---------|
| Curious (onboarding) | Guiding, Human, Encouraging | "Let's connect your first data source to see the magic happen." |
| Frustrated (error) | Direct, Matter-of-fact, Helpful | "Couldn't save changes. Please check your connection and try again." |
| Accomplished (success) | Enthusiastic, Celebratory | "Congratulations! You've hired a new team member." |
| Technical (API docs) | Direct, Matter-of-fact, Formal | "The candidateId parameter is required for this endpoint." |

### Grammar Quick Rules
- ✅ Oxford comma: "candidates, skills, and jobs"
- ✅ Sentence case: "Create new candidate" (not "Create New Candidate")
- ✅ Active voice: "The system sends a notification" (not "A notification is sent")
- ✅ Present tense: "The agent evaluates the candidate"
- ✅ Capitalize races/ethnicities: Black, Asian, Latino, Indigenous

### AI Communication Principles
1. **Be Clear and Specific** - Detailed instructions, relevant context
2. **Use Few-Shot Examples** - Show desired output format
3. **Decompose Complex Tasks** - Break into smaller, chained prompts
4. **Visualize Chain of Thought** - Show what the agent is doing
5. **Avoid Anthropomorphism** - Refer to "the model" or "the system", never "he/she"

## 🔗 Integration with Claude Code

These guidelines are referenced in `/.claude/CLAUDE.md` under the **Visual Development** section:

```markdown
### Design Principles
- Comprehensive design checklist in `/context/design-principles.md`
- Brand style guide in `/context/style-guide.md`
- When making visual (front-end, UI/UX) changes, always refer to these files for guidance
```

## 🚀 Usage Workflow

When implementing front-end features:

1. **Plan** - Review relevant sections of both documents
2. **Implement** - Follow voice, tone, and design guidelines
3. **Verify** - Use Quick Visual Check from CLAUDE.md
4. **Review** - Invoke design-review agent for comprehensive validation

## 📚 Additional Resources

- **Technical Architecture**: `/TECHNICAL_ARCHITECTURE.md`
- **Development Guide**: `/docs/DEVELOPMENT.md`
- **Claude Code Context**: `/.claude/CLAUDE.md`

---

**Last Updated**: October 22, 2025
**Maintained By**: Design & Product Teams
