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

  const form = document.querySelector(".input-form");
  const updateButton = form?.querySelector('button[name="update"]');
  const hiddenEmailInput = form?.querySelector('input[name="collector_email"]');
  const modal = document.querySelector("[data-email-modal]");
  const modalForm = document.querySelector("[data-email-modal-form]");
  const modalEmailInput = modalForm?.querySelector('input[name="modal_email"]');
  const cancelButtons = document.querySelectorAll("[data-email-cancel]");
  let allowUpdateSubmit = false;

  const closeModal = () => {
    if (!modal || !modalForm || !hiddenEmailInput) {
      return;
    }

    modal.hidden = true;
    modalForm.reset();
    hiddenEmailInput.value = "";
  };

  const openModal = () => {
    if (!modal || !modalEmailInput) {
      return;
    }

    modal.hidden = false;
    modalEmailInput.focus();
  };

  if (form && updateButton && hiddenEmailInput && modal && modalForm && modalEmailInput) {
    form.addEventListener("submit", (event) => {
      const submitter = event.submitter;
      const isUpdateSubmit = !submitter || submitter.name === "update";

      if (!isUpdateSubmit) {
        return;
      }

      if (!allowUpdateSubmit) {
        event.preventDefault();
        openModal();
        return;
      }

      allowUpdateSubmit = false;
    });

    modalForm.addEventListener("submit", (event) => {
      event.preventDefault();

      if (!modalForm.reportValidity()) {
        return;
      }

      hiddenEmailInput.value = modalEmailInput.value.trim();
      allowUpdateSubmit = true;
      modal.hidden = true;
      form.requestSubmit(updateButton);
    });

    cancelButtons.forEach((button) => {
      button.addEventListener("click", () => {
        closeModal();
      });
    });

    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) {
        closeModal();
      }
    });
  }
});
