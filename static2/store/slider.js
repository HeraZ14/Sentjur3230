const slider = document.getElementById('slider')
const display = document.getElementById('rangeValue')
const hiddenInput = document.getElementById('selected_price')

// Prilagojene meje
const minValue = 10
const midValue = 100
const maxValue = 3230

// Do kje je "počasi" (v %)
const slowUntil = 80 // 80% slider vrednosti

slider.addEventListener('input', () => {
    const val = parseInt(slider.value)

    let result;
    if (val <= slowUntil) {
        // Linearna rast do 100 (počasi)
        result = minValue + (midValue - minValue) * (val / slowUntil)
    } else {
        // Eksponentna rast od 100 do 3230
        const percent = (val - slowUntil) / (100 - slowUntil) // od 0 do 1
        // Tu nastavi krivuljo – višja potenca = hitrejša rast
        result = midValue + Math.pow(percent, 2.5) * (maxValue - midValue)
    }

    const rounded = Math.round(result)
    display.textContent = rounded
    hiddenInput.value = rounded
})