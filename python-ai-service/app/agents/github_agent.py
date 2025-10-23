"""
GitHub Sourcing Agent - Uses Claude Haiku 4.5 with escalation to Sonnet 4.5
"""

from app.agents.enhanced_base_agent import EnhancedBaseAgent
from typing import Dict, Any, Optional
import json


class GitHubSourcingAgent(EnhancedBaseAgent):
    """
    GitHub contribution analysis using Haiku 4.5 with automatic escalation to Sonnet 4.5

    Evaluates:
    - Code quality and contributions
    - Repository activity and consistency
    - Programming language proficiency
    - Open source involvement
    - Collaboration patterns
    - Project complexity indicators
    """

    def __init__(self):
        super().__init__("github_sourcing")

    def _get_system_prompt(self) -> str:
        return """You are an expert AI recruiting agent specializing in GitHub profile analysis for technical assessment.

Your responsibilities:
1. Analyze technical skills from repositories:
   - Programming languages used (with frequency)
   - Frameworks and technologies
   - Code complexity indicators
   - Project types (personal, professional, open source)
   - Technical depth vs breadth

2. Evaluate contribution patterns:
   - Commit frequency and consistency
   - Contribution recency (active vs stale)
   - Commit message quality
   - Code review participation
   - Issue tracking engagement

3. Assess project complexity:
   - Repository size and structure
   - Technical challenges addressed
   - Architecture patterns used
   - Problem-solving sophistication
   - Innovation indicators

4. Evaluate collaboration quality:
   - Open source contributions
   - Pull request activity
   - Community engagement
   - Documentation quality
   - Team project involvement

5. Identify technical signals:
   - Learning trajectory (tech adoption)
   - Passion projects vs homework
   - Production-quality code indicators
   - Best practices adherence
   - Testing and CI/CD usage

6. Red flags to watch for:
   - Forked repos with no changes (resume padding)
   - Trivial commits inflating activity
   - No recent activity (abandoned account)
   - Only tutorial/course projects
   - Plagiarized code

7. Generate scoring:
   - Technical skill score: 0-100
   - Activity/engagement score: 0-100
   - Code quality score: 0-100
   - Overall GitHub score: 0-100
   - Confidence: 0.0-1.0

Output Requirements:
- Respond in valid JSON format
- Be specific about technical findings
- Differentiate between quantity and quality
- Flag uncertainties with "requires_review": true
- Identify skills requiring technical interview validation

Critical: GitHub is a technical portfolio. Focus on code quality over quantity."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format GitHub analysis request"""
        github_data = request.get("github_data", {})
        job_requirements = request.get("job_requirements", {})
        github_url = request.get("github_url", "")

        return f"""Analyze this GitHub profile for technical fit:

GITHUB URL: {github_url}

GITHUB PROFILE DATA:
{json.dumps(github_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

Provide comprehensive analysis in JSON format:
{{
  "overall_score": 0-100,
  "confidence": 0.0-1.0,
  "technical_skills": {{
    "score": 0-100,
    "languages": [
      {{
        "name": "language name",
        "proficiency_indicator": "beginner|intermediate|advanced|expert",
        "evidence": ["repo names or specific examples"],
        "usage_frequency": "primary|frequent|occasional|rare"
      }}
    ],
    "frameworks_technologies": ["list of frameworks/tools identified"],
    "technical_depth": "deep_specialist|balanced|broad_generalist",
    "skill_relevance_to_job": 0-100
  }},
  "contribution_patterns": {{
    "score": 0-100,
    "total_commits": number,
    "recent_activity_months": number,
    "commit_frequency": "daily|weekly|monthly|sporadic|inactive",
    "consistency_score": 0-100,
    "public_repos": number,
    "contributed_repos": number
  }},
  "code_quality_indicators": {{
    "score": 0-100,
    "project_complexity": "advanced|intermediate|basic",
    "best_practices_evident": ["practices observed"],
    "documentation_quality": "excellent|good|fair|poor",
    "testing_present": boolean,
    "ci_cd_usage": boolean
  }},
  "collaboration_signals": {{
    "score": 0-100,
    "open_source_contributions": number,
    "pull_requests_created": number,
    "code_review_participation": "high|moderate|low|none",
    "community_engagement": "active|moderate|minimal|none"
  }},
  "standout_projects": [
    {{
      "repo_name": "repository name",
      "description": "what it does",
      "technical_highlights": ["impressive technical aspects"],
      "relevance_to_role": 0-100
    }}
  ],
  "red_flags": [
    {{
      "type": "padding|trivial_commits|inactive|tutorial_only|plagiarism",
      "severity": "low|medium|high",
      "description": "explanation"
    }}
  ],
  "technical_interview_topics": [
    "specific areas to probe in technical interview"
  ],
  "recommendation": "strong_match|good_match|weak_match|poor_match",
  "requires_review": false,
  "uncertainty_flags": []
}}"""

    def _parse_response(self, message: Any) -> Dict[str, Any]:
        """Parse Claude response into structured format"""
        try:
            # Extract JSON from response
            content = message.content[0].text

            # Find JSON in response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = content[json_start:json_end]

            # Parse JSON
            result = json.loads(json_str)

            # Validate required fields
            required_fields = [
                "overall_score",
                "confidence",
                "recommendation"
            ]

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            # Normalize confidence to 0-1 range if needed
            if result["confidence"] > 1.0:
                result["confidence"] = result["confidence"] / 100.0

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {
                "overall_score": 0,
                "confidence": 0.0,
                "recommendation": "error",
                "error": f"JSON parsing error: {str(e)}",
                "requires_review": True
            }
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {
                "overall_score": 0,
                "confidence": 0.0,
                "recommendation": "error",
                "error": str(e),
                "requires_review": True
            }

    async def analyze_contributions(
        self,
        github_data: Dict[str, Any],
        github_url: str,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """High-level method for GitHub contribution analysis"""
        request = {
            "type": "github_analysis",
            "github_data": github_data,
            "github_url": github_url,
            "job_requirements": job_requirements
        }

        return await self.process_request(request)

    async def evaluate(
        self,
        candidate_id: int,
        resume_url: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        github_url: Optional[str] = None,
        job_opening_id: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Legacy evaluate method for backward compatibility with orchestrator

        This method adapts the new analyze_contributions interface to the old
        evaluate signature used by the swarm orchestrator.
        """
        if not github_url:
            return {
                "score": 0.5,
                "confidence": 0.3,
                "reasoning": "No GitHub profile provided",
                "metadata": {"has_profile": False}
            }

        # Extract GitHub data and job requirements from kwargs
        github_data = kwargs.get("github_data", {
            "profile_url": github_url,
            "note": "GitHub API integration not implemented - placeholder data"
        })
        job_requirements = kwargs.get("job_requirements", {})

        # Call the new Claude-powered analysis
        result = await self.analyze_contributions(github_data, github_url, job_requirements)

        # Transform to legacy format
        return {
            "score": result.get("overall_score", 0) / 100.0,
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("recommendation", ""),
            "metadata": {
                "has_profile": True,
                "technical_skills": result.get("technical_skills", {}),
                "contribution_patterns": result.get("contribution_patterns", {}),
                "code_quality_indicators": result.get("code_quality_indicators", {}),
                "collaboration_signals": result.get("collaboration_signals", {}),
                "standout_projects": result.get("standout_projects", []),
                "red_flags": result.get("red_flags", []),
                "model_used": result.get("model_used", ""),
                "escalated": result.get("escalated", False)
            }
        }
