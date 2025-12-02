import PhotoSwipeLightbox from '/static/store/photoswipe-lightbox.esm.js';

document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('zoom-btn');
    if (!button) {
        return;  // Brez warn-a za production
    }
    const images = window.PRODUCT_IMAGES || [];
    if (!images.length) {
        return;
    }

    const PhotoSwipe = () => import('/static/store/photoswipe.esm.js');

    const lightbox = new PhotoSwipeLightbox({
    dataSource: images,
    pswpModule: PhotoSwipe,
    showHideAnimationType: 'zoom',
    imageFit: 'contain'  // <-- TO: Ohrani aspect ratio brez popačenja (slika se skalira proporcionalno)
    // Opcijsko: Če hočeš manj padding-a okoli: padding: { top: 20, bottom: 20, left: 20, right: 20 }
});
    lightbox.init();

    button.addEventListener('click', () => {
        lightbox.loadAndOpen(0);
    });
});