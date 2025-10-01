let imageIndex = 0;
let imageList = [];

document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll("#image-list img");
    images.forEach(img => imageList.push(img.src));
});

function switchImage() {
    imageIndex++;

    if (imageIndex >= imageList.length) {
        imageIndex = 0; // vrne na glavno sliko
    }

    document.getElementById("main-image").src = imageList[imageIndex];
}
