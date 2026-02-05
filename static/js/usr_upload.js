
(() => {
  const form = document.getElementById("uxReportForm");
  const overlay = document.getElementById("uxMatch");
  const btn = form ? form.querySelector("button[type='submit']") : null;

  if (form) {
    form.addEventListener("submit", () => {
      if (overlay) overlay.classList.add("is-show");
      if (btn) {
        btn.disabled = true;
        btn.textContent = "MATCHING…";
      }
    });
  }

  // Avoid stuck overlay on back navigation
  window.addEventListener("pageshow", () => {
    if (overlay) overlay.classList.remove("is-show");
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Upload & Check Match";
    }
  });
})();

