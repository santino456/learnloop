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

  // Collapsible reference cards
  document.querySelectorAll(".card").forEach((card) => {
    const toggle = card.querySelector(".card-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
      const expanded = card.classList.toggle("expanded");
      toggle.setAttribute("aria-expanded", String(expanded));
    });
  });

  // Copy buttons for code blocks
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
      }
    });
    pre.appendChild(btn);
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
    const card = button.closest(".card") || button.closest("[data-section-id]");
    (card || document.querySelector(".lesson")).insertAdjacentElement("afterend", form);
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
