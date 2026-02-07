/**
 * Experiment Renderer
 *
 * Handles applying experiment variants to DOM elements.
 * Supports three binding types: text, attr, and class.
 */

(function() {
  'use strict';

  /**
   * Apply an experiment variant to a DOM element
   * @param {HTMLElement} element - The target DOM element
   * @param {object} binding - The experiment binding configuration
   * @param {*} value - The experiment variant value
   */
  function applyExperiment(element, binding, value) {
    try {
      switch (binding.type) {
        case "text":
          // Replace element text content
          element.textContent = value;
          break;

        case "attr":
          // Set an attribute value
          if (!binding.attr) {
            throw new Error("Missing 'attr' property for type='attr' binding");
          }
          element.setAttribute(binding.attr, value);
          break;

        case "class":
          // Toggle a CSS class based on truthy/falsy value
          if (!binding.className) {
            throw new Error("Missing 'className' property for type='class' binding");
          }
          element.classList.toggle(binding.className, !!value);
          break;

        default:
          throw new Error(`Unknown binding type: ${binding.type}`);
      }

      // Remove the data-hidden attribute to reveal the element
      element.removeAttribute("data-hidden");
    } catch (error) {
      console.error("[Statsig] Failed to apply experiment:", binding, error);
      // On error, still reveal the element with its default content
      element.removeAttribute("data-hidden");
    }
  }

  /**
   * Pre-hide all experiment target elements to prevent flicker
   * @param {object} experimentConfig - The experiment configuration object
   */
  function preHideExperimentElements(experimentConfig) {
    for (const key of Object.keys(experimentConfig)) {
      const binding = experimentConfig[key];
      const element = document.querySelector(binding.selector);

      if (element) {
        element.setAttribute("data-hidden", "");
      }
    }
  }

  /**
   * Reveal all hidden elements (fallback for errors)
   */
  function revealAllHiddenElements() {
    const hiddenElements = document.querySelectorAll('[data-hidden]');
    hiddenElements.forEach(el => el.removeAttribute('data-hidden'));
  }

  // Expose to window for other modules
  window.StatsigRenderer = {
    applyExperiment: applyExperiment,
    preHideExperimentElements: preHideExperimentElements,
    revealAllHiddenElements: revealAllHiddenElements
  };
})();
