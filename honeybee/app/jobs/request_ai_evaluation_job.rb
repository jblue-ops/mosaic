# frozen_string_literal: true

##
# RequestAiEvaluationJob - Background job to request AI evaluation
#
# This job is enqueued when a recruiter requests a candidate evaluation.
# It calls the Python AI service asynchronously via AiService.
#
# The Python service will call back to Rails via webhook when complete.
#
class RequestAiEvaluationJob < ApplicationJob
  queue_as :ai_processing

  retry_on AiService::AiServiceError, wait: 5.seconds, attempts: 3
  discard_on ActiveRecord::RecordNotFound

  ##
  # Perform AI evaluation request
  #
  # @param candidate_id [Integer] ID of candidate to evaluate
  # @param job_opening_id [Integer, nil] Optional job opening ID
  #
  def perform(candidate_id, job_opening_id = nil)
    candidate = Candidate.find(candidate_id)
    job_opening = job_opening_id ? JobOpening.find(job_opening_id) : nil

    Rails.logger.info("Requesting AI evaluation for Candidate ##{candidate_id}")

    # Call Python AI service
    result = AiService.evaluate_candidate(
      candidate_id: candidate.id,
      resume_url: candidate.resume_data&.dig("url"),
      linkedin_url: candidate.linkedin_url,
      github_url: candidate.github_url,
      job_opening_id: job_opening&.id
    )

    # Store result immediately (Python service may also webhook)
    SwarmDecision.create!(
      candidate:,
      job_opening:,
      decision_type: "initial_screen",
      agent_votes: result["agent_votes"],
      consensus_details: result["consensus_details"],
      overall_confidence: result["overall_confidence"],
      bias_flags: result["bias_flags"] || [],
      evaluated_at: result["evaluated_at"] || Time.current
    )

    Rails.logger.info(
      "AI evaluation complete for Candidate ##{candidate_id} - " \
      "Confidence: #{result['overall_confidence']}"
    )

    # Broadcast to UI via Turbo Stream (if user is watching)
    broadcast_evaluation_complete(candidate, result)
  rescue AiService::AiServiceError => e
    Rails.logger.error("AI Service error for Candidate ##{candidate_id}: #{e.message}")
    # Job will be retried automatically
    raise
  end

  private

  def broadcast_evaluation_complete(candidate, result)
    # TODO: Implement Turbo Stream broadcast
    # This would update the UI in real-time when evaluation completes
    #
    # Turbo::StreamsChannel.broadcast_update_to(
    #   "candidate_#{candidate.id}_evaluations",
    #   target: "evaluation_status",
    #   partial: "candidates/evaluation_status",
    #   locals: { candidate: candidate, result: result }
    # )
  end
end
