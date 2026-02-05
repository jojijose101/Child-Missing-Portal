
(() => {
  const loader = document.getElementById("cpLoader");
  const form = document.querySelector("form.cp-form");

  if (form) {
    form.addEventListener("submit", () => {
      loader.classList.add("is-show");
      const btn = form.querySelector("button[type='submit']");
      if (btn) {
        btn.textContent = "UPLOADING…";
        btn.classList.add("is-disabled");
      }
    });
  }

  // safety: hide loader on back navigation
  window.addEventListener("pageshow", () => {
    loader.classList.remove("is-show");
  });
})();
