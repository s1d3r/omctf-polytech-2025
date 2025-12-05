import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.observe()
    this.processToasts()
  }

  disconnect() {
    if (this.observer) this.observer.disconnect()
  }

  observe() {
    if (this.observer) this.observer.disconnect()
    this.observer = new MutationObserver(() => this.processToasts())
    this.observer.observe(this.element, { childList: true, subtree: true })
  }

  processToasts() {
    const notifier = window.notyf
    if (!notifier) return

    this.element.querySelectorAll(".flash--toast").forEach((el) => {
      const type = el.dataset.toastType === "error" ? "error" : "success"
      const msg = el.dataset.toastMessage || el.textContent.trim()
      if (type === "error") {
        notifier.error(msg)
      } else {
        notifier.success(msg)
      }
      el.remove()
    })
  }
}
