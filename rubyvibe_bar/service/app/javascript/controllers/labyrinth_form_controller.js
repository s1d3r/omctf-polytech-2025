import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.element.addEventListener("turbo:submit-end", () => this.enableButton())
  }

  disconnect() {
    this.element.removeEventListener("turbo:submit-end", () => this.enableButton())
  }

  enableButton() {
    const btn = this.element.querySelector("input[type='submit'], button[type='submit']")
    if (btn) {
      btn.disabled = false
    }
  }
}
