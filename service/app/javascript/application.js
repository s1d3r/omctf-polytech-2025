// Configure your import map in config/importmap.rb. Read more: https://github.com/rails/importmap-rails
import "@hotwired/turbo-rails"
import "controllers"
import { Notyf } from "notyf"

const notyf = new Notyf({
  position: { x: "right", y: "bottom" },
  types: [
    { type: "success", className: "notyf__toast--success" },
    { type: "error", className: "notyf__toast--error" },
  ],
})
window.notyf = notyf
