class ApplicationController < ActionController::Base
  include Authentication

  # Multi-tenancy: Current.company is automatically set via Authentication concern
  # All models with default_scope will filter by Current.company

  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  # For Pundit authorization (to be set up later)
  # include Pundit::Authorization
end
