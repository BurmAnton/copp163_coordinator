document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#disability-check').addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            document.querySelector('#form-disability').style.display = "block";
        } else {
            document.querySelector('#form-disability').style.display = "none";
        }
    })
})