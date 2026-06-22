/* Case runtime */
document.addEventListener("DOMContentLoaded", () => {
  window.LearnLoopRuntime.init();

  // Judgment reveal
  document.querySelectorAll(".exercise[data-kind='case']").forEach((exercise) => {
    const compareBtn = exercise.querySelector(".exercise-compare");
    const reveal = exercise.querySelector(".judgment-reveal");
    const sections = exercise.querySelectorAll(".judgment-section");
    if (!compareBtn || !reveal) return;
    compareBtn.textContent = "对比作者视角";
    compareBtn.addEventListener("click", () => {
      const isOpen = reveal.classList.contains("open");
      if (isOpen) {
        reveal.classList.remove("open");
        sections.forEach((s) => s.setAttribute("hidden", ""));
        compareBtn.textContent = "对比作者视角";
      } else {
        reveal.classList.add("open");
        sections.forEach((s) => s.removeAttribute("hidden"));
        compareBtn.textContent = "收起";
      }
    });
  });

  // Checkpoint reveal
  document.querySelectorAll(".checkpoint").forEach((container) => {
    const toggle = container.querySelector(".checkpoint-toggle");
    const answer = container.querySelector(".checkpoint-answer");
    if (!toggle || !answer) return;
    toggle.textContent = "显示提示";
    toggle.addEventListener("click", () => {
      const hidden = answer.hasAttribute("hidden");
      if (hidden) {
        answer.removeAttribute("hidden");
        toggle.textContent = "隐藏提示";
      } else {
        answer.setAttribute("hidden", "");
        toggle.textContent = "显示提示";
      }
    });
  });
});
