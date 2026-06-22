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

  // Judgment cards: reveal author perspective, tradeoffs, pitfalls
  document.querySelectorAll(".exercise[data-kind='case']").forEach((exercise) => {
    const compare = exercise.querySelector(".exercise-compare");
    const reveal = exercise.querySelector(".judgment-reveal");
    const sections = exercise.querySelectorAll(".judgment-section");
    if (compare && reveal) {
      compare.addEventListener("click", () => {
        reveal.removeAttribute("hidden");
        sections.forEach((section) => section.removeAttribute("hidden"));
        compare.setAttribute("aria-expanded", "true");
        compare.textContent = "Compared";
        compare.disabled = true;
      });
    }
  });

  // Legacy case exercises without judgment markers still get reveal behavior
  document.querySelectorAll(".exercise:not([data-kind='case'])").forEach((exercise) => {
    const toggle = exercise.querySelector(".exercise-toggle");
    if (toggle) {
      toggle.textContent = "Reveal reasoning";
    }
    const task = exercise.querySelector(".exercise-task");
    const options = task?.querySelector("ul, ol");
    if (options) {
      options.classList.add("exercise-options");
      options.querySelectorAll("li").forEach((li) => {
        li.addEventListener("click", () => {
          options.querySelectorAll("li").forEach((item) => item.classList.remove("selected"));
          li.classList.add("selected");
        });
      });
    }
  });

  // Toggle reasoning/answer
  document.querySelectorAll(".exercise-toggle, .checkpoint-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const container = button.closest(".exercise, .checkpoint");
      const answer = container.querySelector(".exercise-answer, .checkpoint-answer");
      if (!answer) return;
      const hidden = answer.hasAttribute("hidden");
      if (hidden) {
        answer.removeAttribute("hidden");
        button.setAttribute("aria-expanded", "true");
        button.textContent = container.classList.contains("exercise") ? "Hide reasoning" : "Hide answer";
      } else {
        answer.setAttribute("hidden", "");
        button.setAttribute("aria-expanded", "false");
        button.textContent = container.classList.contains("exercise") ? "Reveal reasoning" : "Show answer";
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
    const heading = button.closest("[data-section-id]") || button.closest(".card");
    (heading || document.querySelector(".lesson")).insertAdjacentElement("afterend", form);
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
