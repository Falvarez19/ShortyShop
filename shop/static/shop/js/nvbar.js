document.addEventListener("DOMContentLoaded", function() {
    window.addEventListener("scroll", function() {
        let navbar = document.querySelector(".navbar");
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
});
