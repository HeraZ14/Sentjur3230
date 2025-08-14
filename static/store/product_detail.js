document.addEventListener("DOMContentLoaded", function () {
    // --- ALERT fade-out ---
    const alerts = document.querySelectorAll(".alert");
    setTimeout(() => {
      alerts.forEach(alert => {
        alert.style.transition = "opacity 0.5s ease-out";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      });
    }, 3000);

    // --- ADD TO CART ---
    const form = document.getElementById('add-to-cart-form');
    const cartCounter = document.getElementById('cart-counter');

    if (form) { // preveri, če obrazec obstaja
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const url = "{% url 'add_to_cart' %}";
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.cart_count !== undefined) {
                    cartCounter.textContent = data.cart_count;
                    cartCounter.style.display = 'inline-block';
                    cartCounter.classList.add('shake');
                    setTimeout(() => cartCounter.classList.remove('shake'), 500);
                }
            })
            .catch(error => console.error('Napaka:', error));
        });
    }
});

// --- GLOBALNA FUNKCIJA ZA SELECT ---
function updateDisplayedText(selectElement) {
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var text = selectedOption.getAttribute('data-original-text');
    console.log(text);
}
