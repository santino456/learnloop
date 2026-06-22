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
  initCaseReveal();
  initLegacyOptions();
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

  function initCaseReveal() {
    document.querySelectorAll(".exercise[data-kind='case']").forEach((exercise) => {
      const compare = exercise.querySelector(".exercise-compare");
      const reveal = exercise.querySelector(".judgment-reveal");
      const sections = exercise.querySelectorAll(".judgment-section");
      if (!compare || !reveal) return;
      compare.addEventListener("click", () => {
        reveal.removeAttribute("hidden");
        sections.forEach((section) => section.removeAttribute("hidden"));
        reveal.classList.add("open");
        compare.disabled = true;
        compare.textContent = "Compared";
        compare.setAttribute("aria-expanded", "true");
      });
    });
  }

  function initLegacyOptions() {
    document.querySelectorAll(".exercise:not([data-kind='case'])").forEach((exercise) => {
      const toggle = exercise.querySelector(".exercise-toggle");
      if (toggle) toggle.textContent = "Reveal reasoning";
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
    document.querySelectorAll(".exercise:not([data-kind='case']), .checkpoint").forEach((container) => {
      const toggle = container.querySelector(".exercise-toggle, .checkpoint-toggle");
      const answer = container.querySelector(".exercise-answer, .checkpoint-answer");
      if (!toggle || !answer) return;
      toggle.addEventListener("click", () => {
        const hidden = answer.hasAttribute("hidden");
        if (hidden) {
          answer.removeAttribute("hidden");
          toggle.setAttribute("aria-expanded", "true");
          toggle.textContent = container.classList.contains("exercise") ? "Hide reasoning" : "Hide answer";
        } else {
          answer.setAttribute("hidden", "");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = container.classList.contains("exercise") ? "Reveal reasoning" : "Show answer";
        }
      });
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
