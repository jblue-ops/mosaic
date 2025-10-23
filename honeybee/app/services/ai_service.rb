# frozen_string_literal: true

##
# AiService - HTTP client for communicating with Python AI service
#
# Handles all communication between Rails and the Python FastAPI service
# that orchestrates the 6 AI agents for candidate evaluation.
#
# Usage:
#   result = AiService.evaluate_candidate(
#     candidate_id: 123,
#     resume_url: "https://...",
#     linkedin_url: "https://linkedin.com/in/...",
#     github_url: "https://github.com/...",
#     job_opening_id: 456
#   )
#
class AiService
  include HTTParty

  base_uri ENV.fetch("AI_SERVICE_URL", "http://localhost:8000")
  default_timeout 30 # AI evaluation can take time

  class << self
    ##
    # Evaluate a candidate using the AI swarm
    #
    # @param candidate_id [Integer] Rails Candidate ID
    # @param resume_url [String, nil] URL to resume
    # @param linkedin_url [String, nil] LinkedIn profile URL
    # @param github_url [String, nil] GitHub profile URL
    # @param job_opening_id [Integer, nil] Rails JobOpening ID
    # @return [Hash] Evaluation results with agent votes and consensus
    # @raise [AiServiceError] If request fails
    #
    def evaluate_candidate(candidate_id:, resume_url: nil, linkedin_url: nil, github_url: nil, job_opening_id: nil)
      response = post(
        "/api/v1/evaluate",
        body: {
          candidate_id:,
          resume_url:,
          linkedin_url:,
          github_url:,
          job_opening_id:
        }.compact.to_json,
        headers: auth_headers
      )

      handle_response(response)
    end

    ##
    # Check health status of AI service and agents
    #
    # @return [Hash] Status of service and all agents
    #
    def agent_status
      response = get("/api/v1/agents/status", headers: auth_headers)
      handle_response(response)
    end

    ##
    # Basic health check
    #
    # @return [Boolean] True if service is healthy
    #
    def healthy?
      response = get("/api/v1/health", headers: auth_headers)
      response.success?
    rescue StandardError
      false
    end

    private

    def auth_headers
      {
        "Content-Type" => "application/json",
        "Authorization" => "Bearer #{ENV.fetch('AI_SERVICE_API_KEY', 'development-key')}"
      }
    end

    def handle_response(response)
      unless response.success?
        Rails.logger.error("AI Service error: #{response.code} - #{response.body}")
        raise AiServiceError, "AI Service returned #{response.code}: #{response.body}"
      end

      JSON.parse(response.body)
    rescue JSON::ParserError => e
      Rails.logger.error("Failed to parse AI Service response: #{e.message}")
      raise AiServiceError, "Invalid JSON response from AI Service"
    end
  end

  ##
  # Custom error class for AI service communication issues
  #
  class AiServiceError < StandardError; end
end
