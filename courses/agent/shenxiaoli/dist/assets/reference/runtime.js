/* Reference runtime */
document.addEventListener("DOMContentLoaded", () => {
  window.LearnLoopRuntime.init();

  // Collapsible cards
  document.querySelectorAll(".card").forEach((card) => {
    const header = card.querySelector(".card-header");
    const toggle = card.querySelector(".card-toggle");
    if (!header) return;
    header.addEventListener("click", (event) => {
      if (event.target.closest(".ask-btn")) return;
      const expanded = card.classList.toggle("expanded");
      toggle?.setAttribute("aria-expanded", String(expanded));
    });
  });

  // Card filter
  const filterInput = document.getElementById("card-filter");
  if (filterInput) {
    filterInput.placeholder = "搜索参考条目…";
    filterInput.addEventListener("input", () => {
      const term = filterInput.value.trim().toLowerCase();
      let any = false;
      document.querySelectorAll(".card").forEach((card) => {
        const title = card.querySelector(".card-title")?.textContent || "";
        const summary = card.querySelector(".card-summary")?.textContent || "";
        const body = card.querySelector(".card-body")?.textContent || "";
        const match = (title + summary + body).toLowerCase().includes(term);
        card.style.display = match ? "" : "none";
        if (match) any = true;
      });
      const noMatch = document.querySelector(".card-no-match");
      if (noMatch) noMatch.style.display = any ? "none" : "block";
    });
  }
});
