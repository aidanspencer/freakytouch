// Handles the "Add a photo" form on /photos/. Shrinks the photo in the browser (which also strips its
// location data), then sends it to the upload Worker (worker/src/index.js), which opens a pull request.
const UPLOAD_URL = 'https://freakytouch-uploads.aidanspencer97.workers.dev/'; // Replace with your Worker's URL
const MAX_SIZE = 1600; // Longest side in pixels, same as MAX_SIZE in pull_photos.py

const form = document.getElementById('upload-form');
const uploadStatus = document.getElementById('upload-status');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const token = form.querySelector('[name="cf-turnstile-response"]')?.value;
    if (!token) {
        uploadStatus.textContent = 'Please wait for the CAPTCHA check to finish.';
        return;
    }

    const button = form.querySelector('button');
    button.disabled = true;
    uploadStatus.textContent = 'Uploading...';
    try {
        const data = new FormData();
        data.append('photo', await shrink(form.photo.files[0]), 'photo.jpg');
        data.append('caption', form.caption.value);
        data.append('cf-turnstile-response', token);
        const response = await fetch(UPLOAD_URL, { method: 'POST', body: data });
        const result = await response.json();
        uploadStatus.textContent = result.message;
        if (response.ok) form.reset();
    } catch (error) {
        uploadStatus.textContent = "Couldn't upload that photo. Try a JPG or PNG.";
    }
    turnstile.reset();
    button.disabled = false;
});

// Returns the photo as a JPEG whose longest side is at most MAX_SIZE.
async function shrink(file) {
    const img = new Image();
    img.src = URL.createObjectURL(file);
    await img.decode();
    const scale = Math.min(1, MAX_SIZE / Math.max(img.naturalWidth, img.naturalHeight));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(img.naturalWidth * scale);
    canvas.height = Math.round(img.naturalHeight * scale);
    const context = canvas.getContext('2d');
    context.fillStyle = 'white'; // transparent PNGs would otherwise turn black
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(img, 0, 0, canvas.width, canvas.height);
    URL.revokeObjectURL(img.src);
    return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.85));
}
