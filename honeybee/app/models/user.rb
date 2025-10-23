class User < ApplicationRecord
  belongs_to :company

  has_secure_password
  has_many :sessions, dependent: :destroy

  enum role: { recruiter: 0, hiring_manager: 1, admin: 2 }, _default: :recruiter

  normalizes :email_address, with: ->(e) { e.strip.downcase }

  validates :email_address, presence: true, uniqueness: true
  validates :role, presence: true
end
