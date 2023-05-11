document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.collapse-img').forEach(collapse =>{
        collapse.addEventListener('click', (img) => {
            console.log(img);
            img.srcElement.classList.toggle("rot");
        })
    })
})