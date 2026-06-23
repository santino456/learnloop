/* Practice runtime */
document.addEventListener("DOMContentLoaded", () => {
  window.LearnLoopRuntime.init();

  // Mark as done
  document.querySelectorAll(".exercise-done input[type='checkbox']").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const label = checkbox.closest(".exercise-done");
      label.classList.toggle("checked", checkbox.checked);
    });
  });

  // Choice exercises
  document.querySelectorAll(".exercise[data-kind='choice']").forEach((exercise) => {
    const options = exercise.querySelectorAll(".choice-option");
    const checkBtn = exercise.querySelector(".exercise-check");
    const feedback = exercise.querySelector(".exercise-feedback");
    const answerDiv = exercise.querySelector(".exercise-answer");
    const answer = exercise.dataset.answer?.trim();

    options.forEach((option) => {
      option.addEventListener("click", () => {
        options.forEach((o) => o.classList.remove("selected"));
        option.classList.add("selected");
        option.querySelector("input").checked = true;
        feedback?.setAttribute("hidden", "");
      });
    });

    if (checkBtn) {
      checkBtn.textContent = "检查答案";
      checkBtn.addEventListener("click", () => {
        const selected = exercise.querySelector(".choice-option.selected");
        if (!selected) {
          feedback?.removeAttribute("hidden");
          feedback.className = "exercise-feedback incorrect";
          feedback.textContent = "请先选择一个选项。";
          return;
        }
        const choice = selected.dataset.choice;
        options.forEach((o) => o.classList.remove("correct", "incorrect"));
        if (choice === answer) {
          selected.classList.add("correct");
          feedback?.removeAttribute("hidden");
          feedback.className = "exercise-feedback correct";
          feedback.textContent = "回答正确。";
          answerDiv?.removeAttribute("hidden");
        } else {
          selected.classList.add("incorrect");
          const correctOption = exercise.querySelector(`.choice-option[data-choice='${answer}']`);
          correctOption?.classList.add("correct");
          feedback?.removeAttribute("hidden");
          feedback.className = "exercise-feedback incorrect";
          feedback.textContent = "回答错误。正确答案是 " + answer + "。";
          answerDiv?.removeAttribute("hidden");
        }
      });
    }
  });

  // Fill-in-the-blank exercises
  document.querySelectorAll(".exercise[data-kind='fill']").forEach((exercise) => {
    const inputs = exercise.querySelectorAll(".ll-blank");
    const checkBtn = exercise.querySelector(".exercise-check");
    const feedback = exercise.querySelector(".exercise-feedback");

    if (checkBtn) {
      checkBtn.textContent = "检查答案";
      checkBtn.addEventListener("click", () => {
        let allCorrect = true;
        let anyEmpty = false;
        inputs.forEach((input) => {
          const expected = input.dataset.answer?.trim().toLowerCase();
          const value = input.value.trim().toLowerCase();
          if (!value) anyEmpty = true;
          if (value === expected) {
            input.classList.add("correct");
            input.classList.remove("incorrect");
          } else {
            input.classList.add("incorrect");
            input.classList.remove("correct");
            allCorrect = false;
          }
        });
        feedback?.removeAttribute("hidden");
        if (anyEmpty) {
          feedback.className = "exercise-feedback incorrect";
          feedback.textContent = "请填写所有空格。";
        } else if (allCorrect) {
          feedback.className = "exercise-feedback correct";
          feedback.textContent = "全部正确！";
        } else {
          feedback.className = "exercise-feedback incorrect";
          feedback.textContent = "有些答案不对，再想想。";
        }
      });
    }
  });

  // Spot-the-bug exercises
  document.querySelectorAll(".exercise[data-kind='bug']").forEach((exercise) => {
    const checkBtn = exercise.querySelector(".exercise-check");
    const feedback = exercise.querySelector(".exercise-feedback");
    const buggyLineNumbers = JSON.parse(exercise.dataset.buggyLines || "[]");

    if (checkBtn) {
      checkBtn.textContent = "检查";
      checkBtn.addEventListener("click", () => {
        const checked = Array.from(exercise.querySelectorAll(".bug-checkbox:checked")).map((cb) => Number(cb.dataset.line));
        let correct = checked.length === buggyLineNumbers.length && checked.every((n) => buggyLineNumbers.includes(n));
        exercise.querySelectorAll(".code-line").forEach((line) => {
          const lineNum = Number(line.dataset.line);
          line.classList.remove("revealed");
          if (buggyLineNumbers.includes(lineNum)) line.classList.add("buggy-line");
        });
        if (correct) {
          exercise.querySelectorAll(".buggy-line").forEach((line) => line.classList.add("revealed"));
        }
        feedback?.removeAttribute("hidden");
        feedback.className = correct ? "exercise-feedback correct" : "exercise-feedback incorrect";
        feedback.textContent = correct ? "找对全部错误行！" : "还没找全，再检查一遍。";
      });
    }
  });

  // Open exercises: reveal answer
  document.querySelectorAll(".exercise[data-kind='open']").forEach((exercise) => {
    const toggle = exercise.querySelector(".exercise-toggle");
    const answer = exercise.querySelector(".exercise-answer");
    if (!toggle || !answer) return;
    toggle.textContent = "显示答案";
    toggle.addEventListener("click", () => {
      const hidden = answer.hasAttribute("hidden");
      if (hidden) {
        answer.removeAttribute("hidden");
        toggle.textContent = "隐藏答案";
      } else {
        answer.setAttribute("hidden", "");
        toggle.textContent = "显示答案";
      }
    });
  });
});
