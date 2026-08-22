// Result tabs
document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".result-panel").forEach((p) => p.classList.remove("active"));
    button.classList.add("active");
    const panel = document.getElementById(button.dataset.target);
    if (panel) panel.classList.add("active");
  });
});

// Keep the IVOE loops playing (some browsers pause autoplay video off-screen)
document.querySelectorAll(".loop video").forEach((v) => {
  v.play().catch(() => {});
});

// Copy BibTeX
const copyButton = document.getElementById("copyBib");
if (copyButton) {
  copyButton.addEventListener("click", async () => {
    const text = document.getElementById("bibtex").innerText;
    try {
      await navigator.clipboard.writeText(text);
      copyButton.textContent = "Copied";
      setTimeout(() => (copyButton.textContent = "Copy"), 1500);
    } catch (e) {
      copyButton.textContent = "Select manually";
    }
  });
}
