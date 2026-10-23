// Swaps the title gifs for a random one from /images/gifs/. Loaded with `defer` so the images exist when it runs.
const totalImages = 45; // Number of numbered gifs (1.gif ... 45.gif) in /images/gifs/
const randomNumber = Math.floor(Math.random() * totalImages) + 1;
document.getElementById('randomImage').src = `/images/gifs/${randomNumber}.gif`;
document.getElementById('randomImage2').src = `/images/gifs/${randomNumber}.gif`;
