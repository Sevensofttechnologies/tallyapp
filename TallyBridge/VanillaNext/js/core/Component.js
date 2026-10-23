/**
 * VanillaNext Component Base Class (No-Module Version)
 */
(function (global) {
  global.VanillaNext = global.VanillaNext || {};
  global.VanillaNext.registry = {};

  global.VanillaNext.Component = class Component {
    constructor(element, options = {}) {
      this.element = element;
      this.options = { ...this.defaults, ...options };
      this.init();
    }

    get defaults() {
      return {};
    }

    init() {
      // Override in subclass
    }

    emit(name, detail = {}) {
      const event = new CustomEvent(name, {
        bubbles: true,
        cancelable: true,
        detail
      });
      this.element.dispatchEvent(event);
    }

    on(event, handler) {
      this.element.addEventListener(event, handler);
    }
  };
})(window);
