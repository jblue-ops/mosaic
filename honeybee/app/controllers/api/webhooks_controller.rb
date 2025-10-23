# frozen_string_literal: true

module Api
  ##
  # WebhooksController - Receives callbacks from Python AI service
  #
  # Python service sends evaluation results here after processing
  #
  class WebhooksController < ApplicationController
    skip_before_action :verify_authenticity_token
    before_action :verify_api_token

    ##
    # Receive swarm decision from Python service
    #
    # POST /api/webhooks/swarm_decision
    #
    # Params:
    #   - candidate_id: Integer
    #   - job_opening_id: Integer (optional)
    #   - agent_votes: Hash
    #   - consensus_details: Hash
    #   - overall_confidence: Float
    #   - bias_flags: Array
    #   - evaluated_at: DateTime
    #
    def swarm_decision
      Rails.logger.info("Received swarm decision webhook for Candidate ##{params[:candidate_id]}")

      candidate = Candidate.find(params[:candidate_id])
      job_opening = params[:job_opening_id] ? JobOpening.find(params[:job_opening_id]) : nil

      decision = SwarmDecision.create!(
        candidate:,
        job_opening:,
        decision_type: params[:decision_type] || "webhook",
        agent_votes: params[:agent_votes],
        consensus_details: params[:consensus_details],
        overall_confidence: params[:overall_confidence],
        bias_flags: params[:bias_flags] || [],
        evaluated_at: params[:evaluated_at] || Time.current
      )

      # Broadcast to UI via Turbo Stream
      broadcast_update(candidate, decision)

      render json: { status: "ok", decision_id: decision.id }, status: :created
    rescue ActiveRecord::RecordNotFound => e
      Rails.logger.error("Webhook error: #{e.message}")
      render json: { error: e.message }, status: :not_found
    rescue StandardError => e
      Rails.logger.error("Webhook error: #{e.message}")
      render json: { error: e.message }, status: :unprocessable_entity
    end

    private

    def verify_api_token
      token = request.headers["Authorization"]&.split(" ")&.last
      expected_token = ENV.fetch("AI_SERVICE_API_KEY", "development-key")

      return if ActiveSupport::SecurityUtils.secure_compare(token.to_s, expected_token)

      render json: { error: "Unauthorized" }, status: :unauthorized
    end

    def broadcast_update(candidate, decision)
      # TODO: Implement Turbo Stream broadcast
      # Turbo::StreamsChannel.broadcast_update_to(
      #   "candidate_#{candidate.id}_evaluations",
      #   target: "evaluation_status",
      #   partial: "candidates/evaluation_status",
      #   locals: { candidate:, decision: }
      # )
    end
  end
end
