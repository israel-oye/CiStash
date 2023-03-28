document.querySelector("#upload-nav").addEventListener("mouseover", function() {
    var text = this.innerText
    this.innerHTML = `<i class="fa-solid fa-upload fa-bounce fa-xl"></i>`

    this.addEventListener("mouseout", function() {
        this.innerHTML = text
    })
})