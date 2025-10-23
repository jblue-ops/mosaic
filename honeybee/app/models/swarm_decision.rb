class SwarmDecision < ApplicationRecord
  # AI evaluation audit trail
  belongs_to :candidate
  belongs_to :job_opening, optional: true

  validates :candidate, presence: true
  validates :decision_type, presence: true
  validates :overall_confidence, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 1 }, allow_nil: true

  # Scopes
  scope :recent, -> { order(evaluated_at: :desc) }
  scope :high_confidence, -> { where('overall_confidence >= ?', 0.8) }
  scope :with_bias_flags, -> { where.not(bias_flags: []) }

  # Helper methods
  def has_bias_concerns?
    bias_flags.present? && bias_flags.any?
  end

  def agent_count
    agent_votes&.keys&.count || 0
  end
end
