let values = ['Upload', `<i class=" text-primary fa-solid fa-upload fa-bounce fa-xl"></i>`, 'Add Course'];
let currentIndex = 0;
let uploadElem = document.querySelector('#upload-nav');

setInterval(() => {
    uploadElem.innerHTML = values[currentIndex];
    currentIndex++;
    if (currentIndex === 2) {
        currentIndex = 0;
    }

}, 10000)