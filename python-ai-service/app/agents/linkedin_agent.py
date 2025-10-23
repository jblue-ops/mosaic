"""
LinkedIn Sourcing Agent - Uses Claude Haiku 4.5 with escalation to Sonnet 4.5
"""

from app.agents.enhanced_base_agent import EnhancedBaseAgent
from typing import Dict, Any, Optional
import json


class LinkedInSourcingAgent(EnhancedBaseAgent):
    """
    LinkedIn profile analysis using Haiku 4.5 with automatic escalation to Sonnet 4.5

    Evaluates:
    - Work experience relevance
    - Career progression trajectory
    - Skills endorsements and recommendations
    - Professional network quality
    - Industry expertise
    - Profile completeness
    """

    def __init__(self):
        super().__init__("linkedin_sourcing")

    def _get_system_prompt(self) -> str:
        return """You are an expert AI recruiting agent specializing in LinkedIn profile analysis.

Your responsibilities:
1. Analyze work experience relevance:
   - Job titles and progression
   - Company reputation and size
   - Role responsibilities alignment
   - Industry experience depth
   - Career trajectory (upward/lateral/downward)

2. Evaluate professional indicators:
   - Skills endorsements count and quality
   - Recommendations authenticity and strength
   - Profile completeness (photo, summary, details)
   - Activity level (posts, articles, engagement)

3. Assess network quality:
   - Connection count (context-appropriate)
   - Industry relevance of connections
   - Quality of mutual connections
   - Thought leadership indicators

4. Identify red flags:
   - Inflated titles or responsibilities
   - Inconsistent dates with resume
   - Lack of details or vague descriptions
   - Suspicious endorsement patterns
   - Inactive or abandoned profile

5. Generate scoring:
   - Experience relevance: 0-100
   - Professional credibility: 0-100
   - Network quality: 0-100
   - Overall LinkedIn score: 0-100
   - Confidence: 0.0-1.0

Output Requirements:
- Respond in valid JSON format
- Be objective and evidence-based
- Flag uncertainties with "requires_review": true
- Identify cross-verification needs

Critical: LinkedIn analysis supplements resume data. Look for consistency and additional context."""

    def _format_request(self, request: Dict[str, Any]) -> str:
        """Format LinkedIn analysis request"""
        linkedin_data = request.get("linkedin_data", {})
        job_requirements = request.get("job_requirements", {})
        linkedin_url = request.get("linkedin_url", "")

        return f"""Analyze this LinkedIn profile for job fit:

LINKEDIN URL: {linkedin_url}

LINKEDIN PROFILE DATA:
{json.dumps(linkedin_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

Provide comprehensive analysis in JSON format:
{{
  "overall_score": 0-100,
  "confidence": 0.0-1.0,
  "experience_relevance": {{
    "score": 0-100,
    "total_years": number,
    "relevant_years": number,
    "career_trajectory": "upward|lateral|downward|unclear",
    "key_roles": [
      {{
        "title": "job title",
        "company": "company name",
        "duration_months": number,
        "relevance_score": 0-100,
        "highlights": ["key responsibilities or achievements"]
      }}
    ]
  }},
  "professional_credibility": {{
    "score": 0-100,
    "profile_completeness": 0-100,
    "endorsements_count": number,
    "recommendations_count": number,
    "recommendations_quality": "strong|moderate|weak|none",
    "activity_level": "high|moderate|low|inactive"
  }},
  "network_quality": {{
    "score": 0-100,
    "connections_count": number,
    "industry_relevance": 0-100,
    "thought_leadership": "strong|moderate|weak|none"
  }},
  "red_flags": [
    {{
      "type": "inflated_title|date_inconsistency|vague_details|suspicious_endorsements|inactive",
      "severity": "low|medium|high",
      "description": "explanation"
    }}
  ],
  "cross_verification_needed": [
    "items to verify against resume or in interview"
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

    async def analyze_profile(
        self,
        linkedin_data: Dict[str, Any],
        linkedin_url: str,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """High-level method for LinkedIn profile analysis"""
        request = {
            "type": "linkedin_analysis",
            "linkedin_data": linkedin_data,
            "linkedin_url": linkedin_url,
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

        This method adapts the new analyze_profile interface to the old
        evaluate signature used by the swarm orchestrator.
        """
        if not linkedin_url:
            return {
                "score": 0.5,
                "confidence": 0.3,
                "reasoning": "No LinkedIn profile provided",
                "metadata": {"has_profile": False}
            }

        # Extract LinkedIn data and job requirements from kwargs
        linkedin_data = kwargs.get("linkedin_data", {
            "profile_url": linkedin_url,
            "note": "LinkedIn scraping not implemented - placeholder data"
        })
        job_requirements = kwargs.get("job_requirements", {})

        # Call the new Claude-powered analysis
        result = await self.analyze_profile(linkedin_data, linkedin_url, job_requirements)

        # Transform to legacy format
        return {
            "score": result.get("overall_score", 0) / 100.0,
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("recommendation", ""),
            "metadata": {
                "has_profile": True,
                "experience_relevance": result.get("experience_relevance", {}),
                "professional_credibility": result.get("professional_credibility", {}),
                "network_quality": result.get("network_quality", {}),
                "red_flags": result.get("red_flags", []),
                "model_used": result.get("model_used", ""),
                "escalated": result.get("escalated", False)
            }
        }
