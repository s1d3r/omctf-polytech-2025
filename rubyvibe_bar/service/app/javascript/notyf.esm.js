const DEFAULT_DURATION = 3000

class Notyf {
  constructor(options = {}) {
    this.position = options.position || { x: "right", y: "bottom" }
    this.types = options.types || []
    this.container = document.createElement("div")
    this.container.className = "notyf-container"
    this.container.dataset.position = `${this.position.x}-${this.position.y}`
    document.body.appendChild(this.container)
  }

  success(message) {
    this._show(message, "success")
  }

  error(message) {
    this._show(message, "error")
  }

  open({ type, message }) {
    if (type === "error") return this.error(message)
    return this.success(message)
  }

  _show(message, type) {
    const toast = document.createElement("div")
    toast.className = `notyf-toast is-${type}`
    toast.textContent = message
    this.container.appendChild(toast)

    requestAnimationFrame(() => toast.classList.add("is-visible"))

    setTimeout(() => {
      toast.classList.remove("is-visible")
      setTimeout(() => toast.remove(), 300)
    }, DEFAULT_DURATION)
  }
}

export { Notyf }
