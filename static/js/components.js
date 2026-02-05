// Cyberpunk Navbar toggle + footer year
(() => {
  const btn = document.querySelector(".cp-burger");
  const menu = document.getElementById("cpNavMenu");

  if (btn && menu) {
    const setExpanded = (val) => btn.setAttribute("aria-expanded", String(val));

    btn.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      setExpanded(open);
    });

    // Close menu when clicking a link (mobile)
    menu.addEventListener("click", (e) => {
      if (e.target.classList.contains("cp-link") || e.target.classList.contains("cp-btn")) {
        menu.classList.remove("is-open");
        setExpanded(false);
      }
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        menu.classList.remove("is-open");
        setExpanded(false);
      }
    });
  }

  const y = document.getElementById("cpYear");
  if (y) y.textContent = new Date().getFullYear();
})();
