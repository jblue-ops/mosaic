class CapabilityAssessment < ApplicationRecord
  # Polymorphic - can belong to Candidate OR Employee
  belongs_to :person, polymorphic: true
  belongs_to :skill

  enum proficiency: { beginner: 0, intermediate: 1, advanced: 2, expert: 3 }
  enum verification_source: {
    ai_agent: 0,
    github: 1,
    linkedin: 2,
    manual: 3,
    resume: 4
  }, _prefix: :verified_by

  validates :person, presence: true
  validates :skill, presence: true
  validates :proficiency, presence: true
  validates :confidence_score, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 1 }, allow_nil: true
end
