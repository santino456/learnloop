/* LearnLoop shared runtime — question drawer, ask form, copy buttons */
window.LearnLoopRuntime = (() => {
  const config = window.LEARNLOOP_CONFIG || { apiBase: window.location.origin };
  const apiBase = config.apiBase || window.location.origin;

  function init() {
    if (window.location.protocol === "file:") {
      document.getElementById("file-warning")?.classList.add("visible");
    }
    initCopyButtons();
    initAskButtons();
    initDrawer();
    initDecisionBlocks();
    initLibraryShell();
    initMath();
    loadQuestions();
  }

  function initCopyButtons() {
    document.querySelectorAll("pre").forEach((pre) => {
      const code = pre.querySelector("code");
      if (!code) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      btn.textContent = "复制";
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(code.textContent || "");
          btn.textContent = "已复制";
          btn.classList.add("copied");
          setTimeout(() => {
            btn.textContent = "复制";
            btn.classList.remove("copied");
          }, 1500);
        } catch (_e) {
          btn.textContent = "失败";
          setTimeout(() => { btn.textContent = "复制"; }, 1500);
        }
      });
      pre.appendChild(btn);
    });
  }

  function initAskButtons() {
    document.querySelectorAll("[data-ask-section]").forEach((button) => {
      button.addEventListener("click", () => openAsk(button));
    });
  }

  function initDrawer() {
    const drawer = document.getElementById("question-drawer");
    document.querySelector("[data-open-drawer]")?.addEventListener("click", () => {
      drawer?.classList.add("open");
      loadQuestions();
    });
    document.querySelector("[data-close-drawer]")?.addEventListener("click", () => {
      drawer?.classList.remove("open");
    });
  }

  function openAsk(button) {
    document.querySelectorAll(".ask-form").forEach((node) => node.remove());
    const template = document.getElementById("ask-template");
    if (!template) return;
    const form = template.content.firstElementChild.cloneNode(true);
    const lesson = document.querySelector(".lesson");
    const anchor = button.closest("[data-section-id]") || lesson || document.querySelector(".page");
    anchor.insertAdjacentElement("afterend", form);
    const textarea = form.querySelector("textarea");
    const status = form.querySelector(".ask-status");
    const submit = form.querySelector("[type='submit']");
    textarea.placeholder = "你对这一节有什么疑问？";
    textarea.focus();
    form.scrollIntoView({ block: "center", behavior: "smooth" });
    form.querySelector("[data-cancel]").textContent = "取消";
    submit.textContent = "保存问题";
    form.querySelector("[data-cancel]").addEventListener("click", () => form.remove());
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = textarea.value.trim();
      if (!question) {
        status.textContent = "请先写一个问题。";
        return;
      }
      const moduleId = lesson?.dataset.moduleId || "";
      const payload = {
        module_id: moduleId,
        section_id: button.dataset.askSection,
        section_title: button.dataset.askTitle,
        question,
      };
      try {
        status.textContent = "保存中…";
        submit.disabled = true;
        const response = await fetchWithTimeout(`${apiBase}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }, 8000);
        if (!response.ok) throw new Error(await response.text());
        status.textContent = "已保存到 questions.jsonl";
        textarea.value = "";
        await loadQuestions();
        setTimeout(() => form.remove(), 900);
      } catch (error) {
        status.textContent = "保存失败。请确认本地 LearnLoop 服务器仍在运行。";
      } finally {
        submit.disabled = false;
      }
    });
  }

  async function loadQuestions() {
    const list = document.getElementById("question-list");
    const count = document.getElementById("question-count");
    if (!list || !count) return;
    try {
      const response = await fetchWithTimeout(`${apiBase}/questions`, {}, 8000);
      const allQuestions = await response.json();
      const lesson = document.querySelector(".lesson");
      const moduleId = lesson?.dataset.moduleId || "";
      const moduleQuestions = allQuestions.filter((q) => q.module_id === moduleId);
      count.textContent = moduleQuestions.length;
      list.innerHTML = moduleQuestions.length
        ? renderQuestionGroups(moduleQuestions)
        : '<p class="question-empty">本模块还没有问题。</p>';
    } catch (_error) {
      list.innerHTML = '<p class="question-empty">启动本地服务器后，这里会显示本模块的问题。</p>';
    }
  }

  async function initLibraryShell() {
    if (!config.coursesUrl || document.querySelector(".ll-shell")) return;
    try {
      const response = await fetchWithTimeout(config.coursesUrl, {}, 8000);
      if (!response.ok) return;
      const courses = await response.json();
      if (!Array.isArray(courses) || courses.length === 0) return;
      document.body.classList.add("has-ll-shell");
      document.body.insertAdjacentHTML("afterbegin", renderLibraryShell(courses));
      document.querySelector("[data-shell-questions]")?.addEventListener("click", () => {
        document.getElementById("question-drawer")?.classList.add("open");
        loadQuestions();
      });
    } catch (_error) {
      // Static files and older single-course servers do not expose a course library.
    }
  }

  function renderLibraryShell(courses) {
    const items = courses.map((course) => {
      const active = course.id === config.courseId ? " active" : "";
      const error = course.error ? " error" : "";
      const href = course.error ? "#" : course.url;
      const meta = course.error ? "配置错误" : `${course.module_count || 0} modules`;
      return `<a class="ll-shell-course${active}${error}" href="${escapeHtml(href)}">
        <span>${escapeHtml(course.title || course.id)}</span>
        <small>${escapeHtml(meta)}</small>
      </a>`;
    }).join("");
    return `<aside class="ll-shell" aria-label="LearnLoop course library">
      <a class="ll-shell-home" href="${escapeHtml(config.libraryUrl || "/")}">LearnLoop</a>
      <nav class="ll-shell-courses">${items}</nav>
      <button class="ll-shell-questions" type="button" data-shell-questions>本模块问题</button>
    </aside>`;
  }

  function renderQuestionGroups(questions) {
    const grouped = {};
    questions.forEach((q) => {
      const key = q.section_id || "未分类";
      const title = q.section_title || key;
      if (!grouped[key]) grouped[key] = { title, items: [] };
      grouped[key].items.push(q);
    });
    return Object.values(grouped).map((group) => `
      <div class="question-section-group">
        <h3 class="question-section-title">${escapeHtml(group.title)}</h3>
        ${group.items.map(renderQuestion).join("")}
      </div>
    `).join("");
  }

  function renderQuestion(question) {
    return `<div class="question-item"><p>${escapeHtml(question.question)}</p><small>${escapeHtml(question.status || "")} · ${escapeHtml((question.id || "").slice(0, 8))}</small></div>`;
  }

  function initDecisionBlocks() {
    document.querySelectorAll(".ll-decision").forEach((decision) => {
      const toggle = decision.querySelector(".decision-toggle");
      const reveal = decision.querySelector(".decision-reveal");
      if (!toggle || !reveal) return;
      toggle.addEventListener("click", () => {
        const isHidden = reveal.hasAttribute("hidden");
        if (isHidden) {
          reveal.removeAttribute("hidden");
          toggle.setAttribute("aria-expanded", "true");
          toggle.textContent = "收起判断视角";
        } else {
          reveal.setAttribute("hidden", "");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = "显示判断视角";
        }
      });
    });
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value || "";
    return div.innerHTML;
  }

  async function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  function initMath() {
    const hasMath = document.querySelector(".math") !== null;
    if (!hasMath) return;
    window.MathJax = {
      tex: {
        inlineMath: [["$", "$"], ["\\(", "\\)"]],
        displayMath: [["$$", "$$"], ["\\[", "\\]"]],
      },
      svg: { fontCache: "global" },
    };
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    script.async = true;
    document.head.appendChild(script);
  }

  return { init, loadQuestions, openAsk, escapeHtml };
})();
