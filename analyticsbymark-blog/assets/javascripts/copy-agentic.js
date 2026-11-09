/* Opt in with SuperFences attributes: ```{ .markdown .copy-prompt } or
 * ```{ .markdown .copy-skill }. Copies only code text; skill downloads SKILL.md.
 * Language-first fences also work when their renderer preserves these classes.
 */
(() => {
  "use strict";

  const fallbackCopy = (text) => {
    const active = document.activeElement;
    const selection = window.getSelection();
    const ranges = selection ? Array.from({ length: selection.rangeCount }, (_, i) => selection.getRangeAt(i).cloneRange()) : [];
    const field = document.createElement("textarea");
    field.value = text;
    field.className = "abm-copy-fallback";
    field.setAttribute("aria-label", "Copy text");
    document.body.append(field);
    try {
      field.focus({ preventScroll: true });
      field.select();
      if (!document.execCommand("copy")) throw new Error("Copy failed");
    } finally {
      field.remove();
      if (active instanceof HTMLElement) active.focus({ preventScroll: true });
      if (selection) {
        selection.removeAllRanges();
        ranges.forEach((range) => selection.addRange(range));
      }
    }
  };

  const enhance = () => {
    document.querySelectorAll(".copy-prompt, .copy-skill").forEach((block) => {
      const pre = block.matches("pre") ? block : block.querySelector("pre") || block.closest("pre");
      const code = pre && pre.querySelector("code");
      if (!code || pre.dataset.abmCopy) return;
      pre.dataset.abmCopy = "true";
      const skill = block.classList.contains("copy-skill");
      const controls = document.createElement("div");
      controls.className = "abm-copy-controls";
      const status = document.createElement("span");
      status.className = "abm-copy-status";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      status.setAttribute("aria-atomic", "true");
      const text = () => {
        const copy = code.cloneNode(true);
        copy.querySelectorAll(".md-annotation, .md-code__nav, .linenos").forEach((node) => node.remove());
        return copy.textContent;
      };
      const button = (label, action) => {
        const element = document.createElement("button");
        element.type = "button";
        element.textContent = label;
        element.addEventListener("click", action);
        controls.append(element);
      };
      button(skill ? "Copy as skill" : "Copy as prompt", async () => {
        status.textContent = "";
        try {
          const value = text();
          if (navigator.clipboard && navigator.clipboard.writeText) {
            try { await navigator.clipboard.writeText(value); }
            catch { fallbackCopy(value); }
          } else {
            fallbackCopy(value);
          }
          status.textContent = "Copied";
        } catch {
          status.textContent = "Copy failed. Select and copy the code manually.";
        }
      });
      if (skill) button("Download SKILL.md", () => {
        let url;
        try {
          url = URL.createObjectURL(new Blob([text()], { type: "text/markdown;charset=utf-8" }));
          const link = document.createElement("a");
          link.href = url;
          link.download = "SKILL.md";
          document.body.append(link);
          link.click();
          link.remove();
          status.textContent = "SKILL.md downloaded";
        } catch {
          status.textContent = "Download failed. Select and copy the code manually.";
        } finally {
          if (url) setTimeout(() => URL.revokeObjectURL(url), 1000);
        }
      });
      controls.append(status);
      pre.insertAdjacentElement("afterend", controls);
    });
  };

  if (typeof document$ !== "undefined") document$.subscribe(enhance);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enhance, { once: true });
  else enhance();
})();
