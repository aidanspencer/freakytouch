const totalImages = 24; // Total number of images in folder
const randomNumber = Math.floor(Math.random() * totalImages) + 1;
document.getElementById('randomImage').src = `/images/gifs/${randomNumber}.gif`;
document.getElementById('randomImage2').src = `/images/gifs/${randomNumber}.gif`;