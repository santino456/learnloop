(() => {
  const config = window.LEARNLOOP_CONFIG || { apiBase: window.location.origin };
  if (window.location.protocol === "file:") {
    document.getElementById("file-warning")?.classList.add("visible");
  }

  const lesson = document.querySelector(".lesson");
  const moduleId = lesson?.dataset.moduleId || "";
  const drawer = document.getElementById("question-drawer");
  const list = document.getElementById("question-list");
  const count = document.getElementById("question-count");

  // Interactive exercises
  document.querySelectorAll(".exercise").forEach((container) => {
    const kind = container.dataset.kind || "open";
    const checkBtn = container.querySelector(".exercise-check");
    const toggle = container.querySelector(".exercise-toggle");
    const answer = container.querySelector(".exercise-answer");
    const feedback = container.querySelector(".exercise-feedback");

    if (kind === "choice") {
      const options = container.querySelectorAll(".choice-option");
      const correct = (container.dataset.correct || "").toUpperCase();
      options.forEach((label) => {
        const input = label.querySelector("input");
        input.addEventListener("change", () => {
          options.forEach((opt) => opt.classList.remove("selected"));
          label.classList.add("selected");
        });
      });
      if (checkBtn) {
        checkBtn.addEventListener("click", () => {
          const selected = container.querySelector(".choice-option input:checked");
          if (!selected) {
            showFeedback(feedback, "Please select an answer.", "neutral");
            return;
          }
          const value = selected.value.toUpperCase();
          options.forEach((label) => {
            const letter = label.dataset.choice;
            label.classList.remove("correct", "incorrect");
            if (letter === correct) {
              label.classList.add("correct");
            } else if (letter === value) {
              label.classList.add("incorrect");
            }
          });
          if (value === correct) {
            showFeedback(feedback, "Correct! " + (answer ? "See the explanation below." : ""), "correct");
          } else {
            showFeedback(feedback, "Not quite. The correct answer is highlighted.", "incorrect");
          }
          if (toggle && answer) toggle.removeAttribute("hidden");
          checkBtn.disabled = true;
        });
      }
    }

    if (kind === "fill") {
      const inputs = container.querySelectorAll(".ll-blank");
      const answers = (container.dataset.answers || "").split(";").map((s) => s.trim());
      if (checkBtn) {
        checkBtn.addEventListener("click", () => {
          let allCorrect = true;
          inputs.forEach((input, idx) => {
            const expected = answers[idx] || "";
            const value = input.value.trim();
            input.classList.remove("correct", "incorrect");
            if (value.toLowerCase() === expected.toLowerCase()) {
              input.classList.add("correct");
            } else {
              input.classList.add("incorrect");
              allCorrect = false;
            }
          });
          if (allCorrect) {
            showFeedback(feedback, "Correct! All blanks match.", "correct");
          } else {
            showFeedback(feedback, "Some answers are incorrect. Try again or reveal the answer.", "incorrect");
          }
          if (toggle && answer) toggle.removeAttribute("hidden");
        });
      }
    }

    if (kind === "bug") {
      const buggy = (container.dataset.buggyLines || "").split(",").filter(Boolean).map(Number);
      const checkboxes = container.querySelectorAll(".bug-checkbox");
      if (checkBtn) {
        checkBtn.addEventListener("click", () => {
          const selected = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => Number(cb.dataset.line));
          const missed = buggy.filter((line) => !selected.includes(line));
          const extra = selected.filter((line) => !buggy.includes(line));
          checkboxes.forEach((cb) => {
            const line = Number(cb.dataset.line);
            const lineEl = cb.closest(".code-line");
            lineEl?.classList.remove("revealed");
            if (buggy.includes(line)) lineEl?.classList.add("revealed");
          });
          if (!missed.length && !extra.length) {
            showFeedback(feedback, "Correct! You identified the buggy line(s).", "correct");
          } else {
            showFeedback(feedback, "Not quite. Buggy lines are now highlighted; extra selections are not bugs.", "incorrect");
          }
          if (toggle && answer) toggle.removeAttribute("hidden");
        });
      }
    }

    if (toggle && answer) {
      toggle.addEventListener("click", () => {
        const hidden = answer.hasAttribute("hidden");
        if (hidden) {
          answer.removeAttribute("hidden");
          toggle.setAttribute("aria-expanded", "true");
          toggle.textContent = "Hide answer";
        } else {
          answer.setAttribute("hidden", "");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = "Show answer";
        }
      });
    }
  });

  function showFeedback(el, text, state) {
    if (!el) return;
    el.removeAttribute("hidden");
    el.classList.remove("correct", "incorrect");
    if (state === "correct") el.classList.add("correct");
    if (state === "incorrect") el.classList.add("incorrect");
    el.textContent = text;
  }

  // Open exercises: show/hide answer and mark-done checkbox
  document.querySelectorAll(".exercise[data-kind='open'], .checkpoint").forEach((container) => {
    const toggle = container.querySelector(".exercise-toggle, .checkpoint-toggle");
    const answer = container.querySelector(".exercise-answer, .checkpoint-answer");
    if (toggle && answer) {
      toggle.addEventListener("click", () => {
        const hidden = answer.hasAttribute("hidden");
        if (hidden) {
          answer.removeAttribute("hidden");
          toggle.setAttribute("aria-expanded", "true");
          toggle.textContent = container.classList.contains("exercise") ? "Hide answer" : "Hide answer";
        } else {
          answer.setAttribute("hidden", "");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = container.classList.contains("exercise") ? "Show answer" : "Show answer";
        }
      });
    }
  });

  document.querySelectorAll(".exercise-done input[type='checkbox']").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const label = checkbox.closest(".exercise-done");
      if (checkbox.checked) {
        label.classList.add("checked");
        if (!label.querySelector(".done-text")) {
          label.insertAdjacentHTML("beforeend", ' <span class="done-text">Done</span>');
        }
      } else {
        label.classList.remove("checked");
        label.querySelector(".done-text")?.remove();
      }
    });
  });

  document.querySelectorAll("[data-ask-section]").forEach((button) => {
    button.addEventListener("click", () => openAsk(button));
  });
  document.querySelector("[data-open-drawer]")?.addEventListener("click", () => {
    drawer?.classList.add("open");
    loadQuestions();
  });
  document.querySelector("[data-close-drawer]")?.addEventListener("click", () => {
    drawer?.classList.remove("open");
  });

  function openAsk(button) {
    document.querySelectorAll(".ask-form").forEach((node) => node.remove());
    const template = document.getElementById("ask-template");
    const form = template.content.firstElementChild.cloneNode(true);
    const heading = button.closest("[data-section-id]");
    heading.insertAdjacentElement("afterend", form);
    form.querySelector("textarea").focus();
    form.querySelector("[data-cancel]").addEventListener("click", () => form.remove());
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = form.querySelector("textarea").value.trim();
      const status = form.querySelector(".ask-status");
      if (!question) {
        status.textContent = "Write a question first.";
        return;
      }
      const payload = {
        module_id: moduleId,
        section_id: button.dataset.askSection,
        section_title: button.dataset.askTitle,
        question
      };
      try {
        const response = await fetch(`${config.apiBase}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(await response.text());
        status.textContent = "Saved to questions.jsonl";
        form.querySelector("textarea").value = "";
        await loadQuestions();
        setTimeout(() => form.remove(), 900);
      } catch (error) {
        status.textContent = "Could not save. Start the LearnLoop server and open this page through localhost.";
      }
    });
  }

  async function loadQuestions() {
    if (!list || !count) return;
    try {
      const response = await fetch(`${config.apiBase}/questions`);
      const questions = await response.json();
      count.textContent = questions.length;
      list.innerHTML = questions.length ? questions.map(renderQuestion).join("") : "<p>No questions yet.</p>";
    } catch (_error) {
      list.innerHTML = "<p>Questions are available after the local server starts.</p>";
    }
  }

  function renderQuestion(question) {
    return `<div class="question-item"><strong>${escapeHtml(question.section_title || question.section_id)}</strong><p>${escapeHtml(question.question)}</p><small>${escapeHtml(question.status || "")} · ${escapeHtml(question.id || "")}</small></div>`;
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value || "";
    return div.innerHTML;
  }

  loadQuestions();
})();
