class Current < ActiveSupport::CurrentAttributes
  attribute :session
  attribute :company  # Multi-tenancy: current company context

  delegate :user, to: :session, allow_nil: true

  # Automatically set company from user when session is set
  def session=(value)
    super
    self.company = user&.company
  end
end
