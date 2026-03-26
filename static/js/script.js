document.addEventListener("DOMContentLoaded", () => {
  const actionButtons = document.querySelectorAll(".btn");
  actionButtons.forEach((button) => {
    button.addEventListener("mousedown", () => {
      button.style.transform = "translateY(1px) scale(0.995)";
    });

    button.addEventListener("mouseup", () => {
      button.style.transform = "";
    });

    button.addEventListener("mouseleave", () => {
      button.style.transform = "";
    });
  });

  const brandHome = document.querySelector(".brand-home");
  if (brandHome) {
    brandHome.addEventListener("click", () => {
      location.reload();
    });
  }
});
