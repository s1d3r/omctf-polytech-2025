ActiveSupport.on_load(:active_record) do
  configs = ActiveRecord::Base.configurations.configs_for(env_name: Rails.env)
  next if configs.blank?

  begin
    ActiveRecord::Base.connection_pool.with_connection do |conn|
      adapter = conn.adapter_name.downcase
      next unless adapter.include?("sqlite")

      # Keep writes simple and immediate to the main DB file (no WAL side files).
      conn.execute("PRAGMA busy_timeout = 8000;")
      conn.execute("PRAGMA journal_mode = DELETE;")
      conn.execute("PRAGMA synchronous = NORMAL;")
      conn.execute("PRAGMA temp_store = MEMORY;")
    end
  rescue StandardError => e
    Rails.logger.warn("Skip sqlite PRAGMA setup: #{e.message}") if defined?(Rails)
  end
end
