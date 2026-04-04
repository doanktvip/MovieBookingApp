document.body.classList.add('ddn-background');

document.addEventListener("DOMContentLoaded", function() {
    var nav = document.querySelector('.navbar-default');
    if(nav) {
        nav.classList.add('ddn-glass');
        nav.style.border = 'none';
    }
    var links = document.querySelectorAll('.navbar-default a');
    links.forEach(function(link) {
        link.style.color = 'white';
    });

    var mainContainer = document.querySelector('body > .container');
    var navbar = document.querySelector('.navbar');

    if (navbar && mainContainer) {
        mainContainer.parentNode.insertBefore(navbar, mainContainer);

        var navInnerContainer = navbar.querySelector('.container');
        if (navInnerContainer) {
            navInnerContainer.classList.remove('container');
            navInnerContainer.classList.add('container-fluid');
        }

        mainContainer.style.marginTop = '20px';
    }
});
document.documentElement.style.backgroundColor = '#000000';
document.documentElement.style.backgroundImage = 'radial-gradient(ellipse at 50% 0%, #5c0a0a 0%, #240404 40%, #000000 85%)';