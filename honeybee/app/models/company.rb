class Company < ApplicationRecord
  # Multi-tenant root entity
  has_many :users, dependent: :destroy
  has_many :candidates, dependent: :destroy
  has_many :employees, dependent: :destroy
  has_many :job_openings, dependent: :destroy

  validates :name, presence: true
  validates :ats_provider, inclusion: { in: %w[ashby greenhouse none], allow_nil: true }

  # Encrypt sensitive ATS credentials
  encrypts :ats_credentials, deterministic: false, ignore_case: true
end
