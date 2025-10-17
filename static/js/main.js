// Message dans la console
document.addEventListener("DOMContentLoaded", function() {
    console.log("Maison App frontend chargé !");
});

// Confirmation avant suppression
function confirmDelete() {
    return confirm("Voulez-vous vraiment supprimer cette maison ?");
}

// Exemple : alerte de test
function showAlert(message) {
    alert(message);
}

let lastScrollTop = 0;
const navbar = document.getElementById("navbar");

window.addEventListener("scroll", function() {
let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

if (scrollTop > lastScrollTop) {
    // Scroll vers le bas -> cacher navbar
    navbar.style.top = "-80px";
} else {
    // Scroll vers le haut -> afficher navbar
    navbar.style.top = "0";
}
lastScrollTop = scrollTop;
});
