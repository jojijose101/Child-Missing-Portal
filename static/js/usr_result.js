
(() => {
  // Copy station phone
  const copyBtn = document.getElementById("uxCopyPhone");
  const phoneEl = document.getElementById("uxStationPhone");
  if (copyBtn && phoneEl) {
    copyBtn.addEventListener("click", async () => {
      try{
        await navigator.clipboard.writeText(phoneEl.textContent.trim());
        copyBtn.textContent = "COPIED";
        setTimeout(() => copyBtn.textContent = "Copy", 900);
      } catch(e){
        copyBtn.textContent = "FAILED";
        setTimeout(() => copyBtn.textContent = "Copy", 900);
      }
    });
  }

  // Zoom modal
  const modal = document.getElementById("uxModal");
  const modalImg = document.getElementById("uxModalImg");
  const closeBtn = document.getElementById("uxModalClose");

  function openModal(src){
    modalImg.src = src;
    modal.classList.add("is-show");
  }
  function closeModal(){
    modal.classList.remove("is-show");
    modalImg.src = "";
  }

  document.querySelectorAll("[data-zoom], .ux-img").forEach(el => {
    el.addEventListener("click", () => {
      const src = el.getAttribute("data-zoom");
      if (src) openModal(src);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (modal) modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });
})();

