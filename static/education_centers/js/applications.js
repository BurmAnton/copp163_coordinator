document.addEventListener('DOMContentLoaded', function() {
    window.history.replaceState(null, null, `?p=${document.querySelector('.project-btn.btn-primary').dataset.project}`);
})