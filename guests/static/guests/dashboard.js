document.querySelectorAll("[data-open]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById(button.dataset.open)?.showModal();
  });
});

document.querySelectorAll("[data-close]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog")?.close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

let installPrompt = null;
window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event;
});

document.getElementById("install-app")?.addEventListener("click", async () => {
  if (!installPrompt) {
    document.getElementById("install-dialog")?.showModal();
    return;
  }
  await installPrompt.prompt();
  installPrompt = null;
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch((error) => {
      console.error("Could not register the Nimoli Bhandari Events service worker.", error);
    });
  });
}
