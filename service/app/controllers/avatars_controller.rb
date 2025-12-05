class AvatarsController < ApplicationController
  def show
    filename = params[:file].to_s
    
    path = Rails.root.join("public", "uploads", filename)
    
    send_file path, disposition: :inline
  end
end