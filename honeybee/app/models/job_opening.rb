class JobOpening < ApplicationRecord
  belongs_to :company
  has_many :swarm_decisions, dependent: :destroy

  enum status: { draft: 0, open: 1, closed: 2, filled: 3 }, _default: :draft

  validates :title, presence: true
  validates :company, presence: true
  validates :status, presence: true

  # Multi-tenancy - all queries scoped to Current.company
  default_scope { where(company: Current.company) if Current.company.present? }

  # Scopes
  scope :active, -> { where(status: [:open]) }
  scope :inactive, -> { where(status: [:closed, :filled]) }
end
