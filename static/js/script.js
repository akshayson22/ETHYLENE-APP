// subtle UI niceties
document.addEventListener("DOMContentLoaded", () => {
  const btns = document.querySelectorAll(".btn");
  btns.forEach(b => {
    b.addEventListener("mousedown", () => b.style.transform = "translateY(1px) scale(0.995)");
    b.addEventListener("mouseup", () => b.style.transform = "");
    b.addEventListener("mouseleave", () => b.style.transform = "");
  });

  // Add click handler for header refresh
  const headerLogo = document.querySelector(".logo");
  const headerTitle = document.querySelector(".title-block");
  
  if (headerLogo) {
    headerLogo.addEventListener("click", () => {
      location.reload();
    });
  }
  
  if (headerTitle) {
    headerTitle.addEventListener("click", () => {
      location.reload();
    });
  }
});
