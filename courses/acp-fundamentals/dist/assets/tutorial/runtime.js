/* Tutorial runtime */
document.addEventListener("DOMContentLoaded", () => {
  window.LearnLoopRuntime.init();

  // Toggle reflection checkpoint answers
  document.querySelectorAll(".checkpoint").forEach((container) => {
    const toggle = container.querySelector(".checkpoint-toggle");
    const answer = container.querySelector(".checkpoint-answer");
    if (!toggle || !answer) return;
    toggle.textContent = "显示提示";
    toggle.addEventListener("click", () => {
      const hidden = answer.hasAttribute("hidden");
      if (hidden) {
        answer.removeAttribute("hidden");
        toggle.setAttribute("aria-expanded", "true");
        toggle.textContent = "隐藏提示";
      } else {
        answer.setAttribute("hidden", "");
        toggle.setAttribute("aria-expanded", "false");
        toggle.textContent = "显示提示";
      }
    });
  });
});
