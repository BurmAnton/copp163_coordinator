document.addEventListener('DOMContentLoaded', function() {
    console.log(document.querySelector('#switch-download'));
    document.querySelector('#switch-download').addEventListener('click', function() {
        document.querySelector('#download-application').style.display = 'none';
        document.querySelector('#upload-application').style.display = 'block';
    });
    document.querySelector('#switch-generate').addEventListener('click', function() {
        document.querySelector('#download-application').style.display = 'block';
        document.querySelector('#upload-application').style.display = 'none';
    });
    document.querySelector('#download-application #passport_series').addEventListener('input', function() {
        document.querySelector('#upload-application #passport_series').value = this.value;
    });
}); 