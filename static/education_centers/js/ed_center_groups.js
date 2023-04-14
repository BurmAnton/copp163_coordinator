document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#id_import_file').forEach(input =>{
        input.classList.add("form-control");
        input.style.width = "250px";
        input.style.margin = "auto";
        input.parentElement.parentElement.querySelector('label').remove();
    })    
})