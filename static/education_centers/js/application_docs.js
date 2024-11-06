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
    document.querySelector('#generate-application').addEventListener('click', function() {
        document.querySelector('#download-application').style.display = 'none';
        document.querySelector('#upload-application').style.display = 'block';
        $('#success-alert').fadeTo(4000, 500).slideUp(4000, function(){
            $(".alert").slideUp(500);
        });
    });
    document.querySelector('#upload-application').addEventListener('submit', function() {
        $('#success-upload-alert').fadeTo(4000, 500).slideUp(4000, function(){
            $(".alert").slideUp(500);
        });
    });
    document.querySelector('#download-application #passport_series').addEventListener('input', function() {
        document.querySelector('#upload-application #passport_series').value = this.value;
    });
}); 