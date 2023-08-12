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