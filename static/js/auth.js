(() => {
  const tabs = document.querySelectorAll(".cp-tab");
  const glow = document.querySelector(".cp-tab-glow");
  const panels = document.querySelectorAll(".cp-panel");

  function openPanel(selector){
    const panel = document.querySelector(selector);
    if (!panel) return;

    panels.forEach(p => {
      p.classList.remove("is-active");
      p.hidden = true;
    });

    panel.classList.add("is-active");
    panel.hidden = false;

    tabs.forEach((t, idx) => {
      const active = t.getAttribute("data-target") === selector;
      t.classList.toggle("is-active", active);
      t.setAttribute("aria-selected", String(active));
      if (active && glow) glow.style.transform = `translateX(${idx * 100}%)`;
    });
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => openPanel(btn.dataset.target));
  });

  document.querySelectorAll("[data-switch]").forEach((b) => {
    b.addEventListener("click", () => openPanel(b.getAttribute("data-switch")));
  });

  // ✅ OPEN correct tab on load
  if (location.hash === "#signup") {
    openPanel("#cpSignup");
  } else {
    const serverOpen = "{{ open|default:'login' }}";
    openPanel(serverOpen === "signup" ? "#cpSignup" : "#cpLogin");
  }
})();
