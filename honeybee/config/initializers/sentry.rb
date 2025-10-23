# frozen_string_literal: true

# Sentry error tracking configuration
# Only initialize if SENTRY_DSN is provided

if ENV["SENTRY_DSN"].present?
  Sentry.init do |config|
    config.dsn = ENV["SENTRY_DSN"]
    config.breadcrumbs_logger = [:active_support_logger, :http_logger]

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    config.traces_sample_rate = ENV.fetch("SENTRY_TRACES_SAMPLE_RATE", 0.1).to_f

    # Filter sensitive data
    config.send_default_pii = false

    # Set environment
    config.environment = Rails.env

    # Release tracking
    config.release = ENV.fetch("GIT_COMMIT_SHA", "unknown")
  end
end
