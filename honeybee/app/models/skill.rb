class Skill < ApplicationRecord
  # Shared skill taxonomy across all tenants
  has_many :capability_assessments, dependent: :destroy

  validates :name, presence: true, uniqueness: true
  validates :category, inclusion: { in: %w[technical soft domain], allow_nil: true }

  # Scopes
  scope :technical, -> { where(category: 'technical') }
  scope :soft, -> { where(category: 'soft') }
  scope :domain, -> { where(category: 'domain') }
end
