require "digest"

class ProfilesController < ApplicationController
  before_action :authenticate_user!

  def show; end

  def edit; end

  def update
    if avatar_params[:avatar].present?
      save_avatar_file!(avatar_params[:avatar])
      redirect_to profile_path, notice: "Аватар обновлён."
    else
      redirect_to profile_path, alert: "Выберите файл для загрузки."
    end
  rescue StandardError => e
    Rails.logger.error("Avatar upload failed: #{e.message}")
    redirect_to profile_path, alert: "Не удалось обновить аватар."
  end

  private

  def avatar_params
    params.require(:user).permit(:avatar)
  end

  def save_avatar_file!(uploaded_io)
    raise "Пустой файл" unless uploaded_io.respond_to?(:read)

    if uploaded_io.size > 10.megabytes
      raise "Файл слишком большой (максимум 10 МБ)"
    end

    allowed_types = %w[image/jpeg image/png image/webp]
    if uploaded_io.respond_to?(:content_type) && uploaded_io.content_type.present?
      unless allowed_types.include?(uploaded_io.content_type)
        raise "Недопустимый тип файла"
      end
    end

    ext = File.extname(uploaded_io.original_filename.presence || "").downcase
    ext = ".jpg" if ext.blank?

    uploads_dir = Rails.root.join("public", "uploads")
    FileUtils.mkdir_p(uploads_dir)

    sha = Digest::SHA2.hexdigest(current_user.email.to_s)
    pattern = uploads_dir.join("avatar-#{sha}.*")

    Dir.glob(pattern).each do |old_file|
      File.delete(old_file) rescue nil
    end

    target_path = uploads_dir.join("avatar-#{sha}#{ext}")
    File.open(target_path, "wb") { |file| file.write(uploaded_io.read) }
  end
end
