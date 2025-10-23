class Employee < ApplicationRecord
  # For Mosaic phase - internal employees
  belongs_to :company
  has_many :capability_assessments, as: :person, dependent: :destroy
  has_many :skills, through: :capability_assessments

  validates :name, presence: true
  validates :email, presence: true
  validates :company, presence: true

  # Multi-tenancy - all queries scoped to Current.company
  default_scope { where(company: Current.company) if Current.company.present? }
end
