(() => {
  // Copy phone
  const copyBtn = document.getElementById("cpCopyPhone");
  const phoneEl = document.getElementById("cpPhone");
  if (copyBtn && phoneEl) {
    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(phoneEl.textContent.trim());
        copyBtn.textContent = "COPIED";
        setTimeout(() => copyBtn.textContent = "Copy", 900);
      } catch (e) {
        copyBtn.textContent = "FAILED";
        setTimeout(() => copyBtn.textContent = "Copy", 900);
      }
    });
  }

  // Image zoom modal
  const modal = document.getElementById("cpModal");
  const modalImg = document.getElementById("cpModalImg");
  const closeBtn = document.getElementById("cpModalClose");

  function openModal(src){
    if (!modal || !modalImg) return;
    modalImg.src = src;
    modal.classList.add("is-show");
  }

  function closeModal(){
    if (!modal) return;
    modal.classList.remove("is-show");
    if (modalImg) modalImg.src = "";
  }

  document.querySelectorAll("[data-zoom], .cp-img").forEach(el => {
    el.addEventListener("click", () => {
      const src = el.getAttribute("data-zoom") || el.getAttribute("data-full");
      if (src) openModal(src);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (modal) modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
})();