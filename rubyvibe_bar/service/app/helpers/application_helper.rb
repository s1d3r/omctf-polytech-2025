module ApplicationHelper
  require "digest"
  require "cgi"

  def avatar_tag_for(user, size: :medium, **html_options)
    return unless user

    sizes = { small: 32, medium: 72, large: 120 }
    dimension = sizes[size] || size.to_i
    dimension = 48 if dimension.zero?
    base_classes = ["avatar", "avatar--#{size}"]
    extra_classes = Array(html_options.delete(:class))
    final_classes = (base_classes + extra_classes).compact

    html_options[:title] ||= user.nickname
    html_options[:"aria-label"] ||= user.nickname

    if (file_path = avatar_disk_path_for(user))
      image_tag(
        avatar_url_for(user, file_path),
        html_options.merge(
          class: final_classes.join(" "),
          alt: html_options[:alt] || user.nickname,
          width: dimension,
          height: dimension,
          data: html_options[:data],
          style: "object-fit: cover;"
        )
      )
    else
      placeholder_classes = (final_classes + ["avatar--placeholder"]).join(" ")
      content_tag(:div, user.nickname.to_s.first&.upcase || "?", html_options.merge(class: placeholder_classes))
    end
  end

  def formatted_datetime(value)
    value.strftime("%d.%m.%Y %H:%M")
  end

  private

  def avatar_disk_path_for(user)
    sha = Digest::SHA2.hexdigest(user.email.to_s)
    Dir.glob(Rails.root.join("public", "uploads", "avatar-#{sha}.*")).first
  end

  def avatar_url_for(user, path = nil)
    path ||= avatar_disk_path_for(user)
    return unless path

    filename = File.basename(path)
    "/show_avatar?file=#{CGI.escape(filename)}"
  end
end
