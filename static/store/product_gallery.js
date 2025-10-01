let currentSlide = 0;

function openSlider(startIndex) {
  currentSlide = startIndex;
  document.getElementById("sliderModal").style.display = "block";
  showSlide();
}

function closeSlider() {
  document.getElementById("sliderModal").style.display = "none";
}

function showSlide() {
  const slides = document.getElementsByClassName("slider-image");
  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slides[currentSlide].style.display = "block";
}

function prevSlide() {
  const slides = document.getElementsByClassName("slider-image");
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  showSlide();
}

function nextSlide() {
  const slides = document.getElementsByClassName("slider-image");
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide();
}
