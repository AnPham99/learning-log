"use strict";

const menuButton = document.querySelector("[data-menu]");
const sidebar = document.querySelector("#sidebar");
if (menuButton && sidebar) {
  const mobile = window.matchMedia("(max-width: 760px)");
  const setMenu = (open) => {
    sidebar.classList.toggle("is-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
    const hidden = mobile.matches && !open;
    sidebar.inert = hidden;
    sidebar.setAttribute("aria-hidden", String(hidden));
  };
  menuButton.addEventListener("click", () => {
    setMenu(!sidebar.classList.contains("is-open"));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && sidebar.classList.contains("is-open")) {
      setMenu(false);
      menuButton.focus();
    }
  });
  document.addEventListener("click", (event) => {
    if (!sidebar.contains(event.target) && !menuButton.contains(event.target)) setMenu(false);
  });
  mobile.addEventListener("change", () => setMenu(false));
  setMenu(false);
}

const editor = document.querySelector("[data-editor]");
const characterCount = document.querySelector("[data-character-count]");
if (editor && characterCount) {
  const updateCount = () => {
    characterCount.textContent = `${[...editor.value].length.toLocaleString("vi-VN")} ký tự`;
  };
  editor.addEventListener("input", updateCount);
  updateCount();
}
