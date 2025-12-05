class User < ApplicationRecord
  require "fileutils"
  require "digest"
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable

  has_many :tasks, dependent: :nullify
  has_many :comments, dependent: :destroy
  has_one_attached :avatar

  before_validation :ensure_nickname
  after_create :assign_random_avatar_from_pool

  validates :email, presence: true, uniqueness: true, length: { maximum: 120 }
  validates :nickname, presence: true
  validate :avatar_type_and_size

  private

  def ensure_nickname
    self.nickname = email.to_s.split("@").first if nickname.blank? && email.present?
  end

  def avatar_type_and_size
    return unless avatar.attached?

    unless avatar.content_type.in?(%w[image/jpeg image/png image/webp])
      errors.add(:avatar, "должен быть в формате JPG, PNG или WEBP")
    end

    if avatar.blob.byte_size > 10.megabytes
      errors.add(:avatar, "слишком большой (максимум 10 МБ)")
    end
  end

  def assign_random_avatar_from_pool
    uploads_dir = Rails.root.join("public", "uploads")
    pool_dir = Rails.root.join("public", "avatars_pool")

    files = Dir.glob(pool_dir.join("*")).select { |path| File.file?(path) }
    return if files.empty?

    sha = Digest::SHA2.hexdigest(email.to_s)
    existing = Dir.glob(uploads_dir.join("avatar-#{sha}.*"))
    return if existing.any?

    FileUtils.mkdir_p(uploads_dir)
    source = files.sample
    ext = File.extname(source)
    ext = ".jpg" if ext.blank?
    target = uploads_dir.join("avatar-#{sha}#{ext}")
    FileUtils.cp(source, target)
  rescue StandardError => e
    Rails.logger.warn("Failed to assign random avatar for user #{id}: #{e.message}")
  end
end
