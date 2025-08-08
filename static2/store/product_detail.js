document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");
    setTimeout(() => {
      alerts.forEach(alert => {
        alert.style.transition = "opacity 0.5s ease-out";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500); // Počakaj, da se animacija zaključi, nato odstrani
      });
    }, 3000); // 3000 ms = 3 sekunde
  });
function updateDisplayedText(selectElement) {
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var text = selectedOption.getAttribute('data-original-text');
    // Tu lahko nastaviš tekst na nek element ali kamorkoli želiš
    console.log(text);
}
