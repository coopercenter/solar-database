const hamburger = document.getElementById('hamburger');
const menu = document.getElementById('menu-items');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active'); // animate hamburger
  menu.classList.toggle('active');
});


window.addEventListener('resize', () => {
    if (window.innerWidth > 993) {
        hamburger.classList.remove('active');
        menu.classList.remove('active');
    }
});