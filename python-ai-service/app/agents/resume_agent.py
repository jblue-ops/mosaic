"""
Resume Analysis Agent - Uses Claude Haiku 4.5 with escalation to Sonnet 4.5
"""

from app.agents.enhanced_base_agent import EnhancedBaseAgent
from typing import Dict, Any, Optional
import json


class ResumeAnalysisAgent(EnhancedBaseAgent):
    """
    Resume analysis using Haiku 4.5 with automatic escalation to Sonnet 4.5

    Evaluates:
    - Resume structure and clarity
    - Skills mentioned with proficiency levels
    - Experience relevance
    - Education background
    - Career gaps or red flags
    - Culture fit indicators
    """

    def __init__(self):
        super().__init__("resume_analysis")

    def _get_system_prompt(self) -> str:
        return """You are an expert AI recruiting agent specializing in resume analysis.

Your responsibilities:
1. Extract skills and assign proficiency levels:
   - beginner: 0-1 years experience
   - intermediate: 1-3 years experience
   - advanced: 3-5 years experience
   - expert: 5+ years experience

2. Analyze experience relevance:
   - Match job requirements to candidate background
   - Assess project complexity and scale
   - Evaluate impact and achievements

3. Identify potential concerns:
   - Employment gaps (>6 months)
   - Job hopping (>3 jobs in 2 years)
   - Inconsistencies in dates or descriptions
   - Skill mismatches

4. Assess culture fit indicators:
   - Company types and sizes
   - Team collaboration mentions
   - Leadership experience

5. Generate confidence scores:
   - Overall match: 0-100
   - Individual skill matches: 0-100
   - Red flag severity: none/low/medium/high

Output Requirements:
- Respond in valid JSON format
- Be thorough but concise
- Flag any uncertainties with "requires_review": true
- If confidence < 70%, explain why

Critical: This analysis feeds into hiring decisions. Be accurate and conservative."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format resume analysis request"""
        resume_text = request.get("resume_text", "")
        job_requirements = request.get("job_requirements", {})

        return f"""Analyze this resume for job fit:

RESUME TEXT:
{resume_text}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

Provide comprehensive analysis in JSON format:
{{
  "overall_match_score": 0-100,
  "confidence": 0.0-1.0,
  "skills_found": [
    {{
      "skill": "skill name",
      "proficiency": "beginner|intermediate|advanced|expert",
      "evidence": "where found in resume",
      "match_score": 0-100
    }}
  ],
  "experience_analysis": {{
    "total_years": number,
    "relevant_years": number,
    "key_projects": ["project descriptions"],
    "impact_indicators": ["achievement descriptions"]
  }},
  "concerns": [
    {{
      "type": "gap|hopping|mismatch|inconsistency",
      "severity": "low|medium|high",
      "description": "explanation"
    }}
  ],
  "culture_fit_indicators": {{
    "company_sizes": ["startup|mid|enterprise"],
    "industries": ["industry names"],
    "team_orientation": "individual|collaborative|leadership"
  }},
  "recommendation": "strong_match|good_match|weak_match|poor_match",
  "next_steps": ["action items"],
  "requires_review": false,
  "uncertainty_flags": []
}}"""

    def _parse_response(self, message: Any) -> Dict[str, Any]:
        """Parse Claude response into structured format"""
        try:
            # Extract JSON from response
            content = message.content[0].text

            # Find JSON in response (Claude sometimes adds explanation text)
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = content[json_start:json_end]

            # Parse JSON
            result = json.loads(json_str)

            # Validate required fields
            required_fields = [
                "overall_match_score",
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
                "overall_match_score": 0,
                "confidence": 0.0,
                "recommendation": "error",
                "error": f"JSON parsing error: {str(e)}",
                "requires_review": True
            }
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {
                "overall_match_score": 0,
                "confidence": 0.0,
                "recommendation": "error",
                "error": str(e),
                "requires_review": True
            }

    async def analyze_candidate(
        self,
        resume_text: str,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """High-level method for resume analysis"""
        request = {
            "type": "resume_analysis",
            "resume_text": resume_text,
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

        This method adapts the new analyze_candidate interface to the old
        evaluate signature used by the swarm orchestrator.
        """
        if not resume_url:
            return {
                "score": 0.4,
                "confidence": 0.2,
                "reasoning": "No resume provided",
                "metadata": {"has_resume": False}
            }

        # Extract resume text and job requirements from kwargs
        resume_text = kwargs.get("resume_text", "Resume text extraction not implemented")
        job_requirements = kwargs.get("job_requirements", {})

        # Call the new Claude-powered analysis
        result = await self.analyze_candidate(resume_text, job_requirements)

        # Transform to legacy format
        return {
            "score": result.get("overall_match_score", 0) / 100.0,
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("recommendation", ""),
            "metadata": {
                "has_resume": True,
                "skills_found": result.get("skills_found", []),
                "experience_analysis": result.get("experience_analysis", {}),
                "concerns": result.get("concerns", []),
                "model_used": result.get("model_used", ""),
                "escalated": result.get("escalated", False)
            }
        }
