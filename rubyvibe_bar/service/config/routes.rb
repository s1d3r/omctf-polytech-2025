Rails.application.routes.draw do
  devise_for :users, skip: [:registrations]

  as :user do
    get "users/sign_up", to: "devise/registrations#new", as: :new_user_registration
    post "users", to: "devise/registrations#create", as: :user_registration
  end

  resource :profile, only: %i[show edit update], controller: "profiles"

  resources :tasks do
    post :solve, on: :member
    resources :comments, only: %i[create destroy]
  end

  get "show_avatar", to: "avatars#show"
  get "about", to: "pages#about"
  get "up" => "rails/health#show", as: :rails_health_check
  get "service-worker" => "rails/pwa#service_worker", as: :pwa_service_worker
  get "manifest" => "rails/pwa#manifest", as: :pwa_manifest

  root "tasks#index"
end
