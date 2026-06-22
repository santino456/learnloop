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

  initCopyButtons();
  initPracticeExercises();
  initAskButtons();
  initDrawer();
  initMarkDone();
  initOpenToggles();
  loadQuestions();

  function initCopyButtons() {
    document.querySelectorAll("pre").forEach((pre) => {
      const code = pre.querySelector("code");
      if (!code) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(code.textContent || "");
          btn.textContent = "Copied";
          btn.classList.add("copied");
          setTimeout(() => {
            btn.textContent = "Copy";
            btn.classList.remove("copied");
          }, 1500);
        } catch (_e) {
          btn.textContent = "Failed";
          setTimeout(() => { btn.textContent = "Copy"; }, 1500);
        }
      });
      pre.appendChild(btn);
    });
  }

  function initPracticeExercises() {
    document.querySelectorAll(".exercise").forEach((container) => {
      const kind = container.dataset.kind || "open";
      const checkBtn = container.querySelector(".exercise-check");
      const toggle = container.querySelector(".exercise-toggle");
      const answer = container.querySelector(".exercise-answer");
      const feedback = container.querySelector(".exercise-feedback");

      if (kind === "choice") initChoice(container, checkBtn, toggle, answer, feedback);
      if (kind === "fill") initFill(container, checkBtn, toggle, answer, feedback);
      if (kind === "bug") initBug(container, checkBtn, toggle, answer, feedback);

      if (toggle && answer) {
        toggle.addEventListener("click", () => toggleAnswer(answer, toggle));
      }
    });
  }

  function initChoice(container, checkBtn, toggle, answer, feedback) {
    const options = container.querySelectorAll(".choice-option");
    const correct = (container.dataset.correct || "").toUpperCase();
    options.forEach((label) => {
      const input = label.querySelector("input");
      input.addEventListener("change", () => {
        options.forEach((opt) => opt.classList.remove("selected"));
        label.classList.add("selected");
      });
    });
    if (!checkBtn) return;
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
        showFeedback(feedback, "Correct!" + (answer ? " See the explanation below." : ""), "correct");
      } else {
        showFeedback(feedback, "Not quite. The correct answer is highlighted.", "incorrect");
      }
      if (toggle && answer) toggle.removeAttribute("hidden");
      checkBtn.disabled = true;
    });
  }

  function initFill(container, checkBtn, toggle, answer, feedback) {
    const inputs = container.querySelectorAll(".ll-blank");
    const answers = (container.dataset.answers || "").split(";").map((s) => s.trim());
    if (!checkBtn) return;
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

  function initBug(container, checkBtn, toggle, answer, feedback) {
    const buggy = (container.dataset.buggyLines || "").split(",").filter(Boolean).map(Number);
    const checkboxes = container.querySelectorAll(".bug-checkbox");
    if (!checkBtn) return;
    checkBtn.addEventListener("click", () => {
      const selected = Array.from(checkboxes)
        .filter((cb) => cb.checked)
        .map((cb) => Number(cb.dataset.line));
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

  function toggleAnswer(answer, toggle) {
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
  }

  function showFeedback(el, text, state) {
    if (!el) return;
    el.removeAttribute("hidden");
    el.classList.remove("correct", "incorrect", "neutral");
    if (state) el.classList.add(state);
    el.textContent = text;
  }

  function initAskButtons() {
    document.querySelectorAll("[data-ask-section]").forEach((button) => {
      button.addEventListener("click", () => openAsk(button));
    });
  }

  function initDrawer() {
    document.querySelector("[data-open-drawer]")?.addEventListener("click", () => {
      drawer?.classList.add("open");
      loadQuestions();
    });
    document.querySelector("[data-close-drawer]")?.addEventListener("click", () => {
      drawer?.classList.remove("open");
    });
  }

  function initMarkDone() {
    document.querySelectorAll(".exercise-done input[type='checkbox']").forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        const label = checkbox.closest(".exercise-done");
        label.classList.toggle("checked", checkbox.checked);
        let doneText = label.querySelector(".done-text");
        if (checkbox.checked && !doneText) {
          doneText = document.createElement("span");
          doneText.className = "done-text";
          doneText.textContent = " Done";
          label.appendChild(doneText);
        } else if (!checkbox.checked && doneText) {
          doneText.remove();
        }
      });
    });
  }

  function initOpenToggles() {
    document.querySelectorAll(".exercise[data-kind='open'], .checkpoint").forEach((container) => {
      const toggle = container.querySelector(".exercise-toggle, .checkpoint-toggle");
      const answer = container.querySelector(".exercise-answer, .checkpoint-answer");
      if (!toggle || !answer) return;
      toggle.addEventListener("click", () => toggleAnswer(answer, toggle));
    });
  }

  function openAsk(button) {
    document.querySelectorAll(".ask-form").forEach((node) => node.remove());
    const template = document.getElementById("ask-template");
    if (!template) return;
    const form = template.content.firstElementChild.cloneNode(true);
    const anchor = button.closest("[data-section-id]") || lesson || document.querySelector(".page");
    anchor.insertAdjacentElement("afterend", form);
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
        question,
      };
      try {
        const response = await fetch(`${config.apiBase}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
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
      list.innerHTML = questions.length
        ? questions.map(renderQuestion).join("")
        : "<p>No questions yet.</p>";
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
})();
