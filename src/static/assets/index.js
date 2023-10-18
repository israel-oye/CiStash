let values = ['Upload', `<i class="fa-solid fa-upload fa-bounce fa-xl"></i>`, 'Add Course'];
let currentIndex = 0;
let uploadElem = document.querySelector('#upload-nav');

if (uploadElem) {
    setInterval(() => {
        uploadElem.innerHTML = values[currentIndex];
        currentIndex++;
        if (currentIndex === 3) {
            currentIndex = 0;
        }

    }, 10000)
}

function nav_changer(media_query) {
    var toggleButton = document.querySelector('button.navbar-toggler');

    if (media_query.matches) {
        toggleButton.setAttribute('aria-controls', 'offcanvas');
        toggleButton.setAttribute('data-bs-toggle', 'offcanvas');
        toggleButton.setAttribute('data-bs-target', '#offcanvas');
    } else {
        toggleButton.setAttribute('aria-controls', 'navbarContent');
        toggleButton.setAttribute('data-bs-toggle', 'collapse');
        toggleButton.setAttribute('data-bs-target', '#navbarContent');
    }
}

var mq = window.matchMedia("(max-width: 767px)");
mq.addEventListener("change", nav_changer);
nav_changer(mq);