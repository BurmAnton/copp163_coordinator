document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.show-appls').addEventListener('click', () =>{
        document.querySelector('.show-appls').style.display = 'none';
        document.querySelector('.hide-appls').style.display = 'block';
        document.querySelectorAll('.qouta-duration').forEach(th => {
            th.setAttribute("colspan", 3)
        });
        document.querySelectorAll('.hide-col').forEach(th => {
            th.classList.add('show-col')
        });
    })
    document.querySelector('.hide-appls').addEventListener('click', () =>{
        document.querySelector('.hide-appls').style.display = 'none';
        document.querySelector('.show-appls').style.display = 'block';
        document.querySelectorAll('.qouta-duration').forEach(th => {
            th.setAttribute("colspan", 1)
        });
        document.querySelectorAll('.hide-col').forEach(th => {
            th.classList.remove('show-col')
        });
    })
})