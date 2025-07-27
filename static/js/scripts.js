// Accusation Pop-up triggers
document.addEventListener("DOMContentLoaded", () => {
  const continueBtn = document.getElementById("popup-continue-btn");
  const popupInitial = document.getElementById("popup-initial");
  const popupAccusation = document.getElementById("popup-accusation");
  const sceneContent = document.getElementById("scene-content");

  if (continueBtn && popupInitial && popupAccusation) {
    continueBtn.addEventListener("click", () => {
      popupInitial.style.display = "none";
      popupAccusation.style.display = "block";
      if (sceneContent) {
        sceneContent.style.display = "none"; // Optional; already hidden
      }
    });
  }
});
