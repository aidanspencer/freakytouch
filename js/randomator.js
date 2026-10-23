// Picks a random background image for the page. Loaded with `defer` so the body exists when it runs.
var images =
        [
            "/images/bg/035C.jpg",
            "/images/bg/036C.jpg",
            "/images/bg/081C.jpg",
            "/images/bg/096.GIF",
            "/images/bg/145.GIF",
            "/images/bg/150.GIF",
            "/images/bg/163.GIF",
            "/images/bg/170.GIF",
            "/images/bg/515.GIF"
        ];
function randomator() {
    document.getElementsByClassName("mainview")[0].style.backgroundImage = "url(" + images[Math.floor(Math.random() * images.length)] + ")";
}
randomator();
