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
    
    document.querySelector('.cumulative-switch').addEventListener('click', () =>{
        let btn = document.querySelector('.cumulative-switch');
        btn.classList.toggle("btn-primary");
        btn.classList.toggle('btn-outline-primary');
        if (btn.classList.contains('btn-primary')) {
            btn.innerHTML = 'Показать нарастающий итог';
            document.querySelector('.graphic').style.display = 'flex';
            document.querySelector('.cumulative-graphic').style.display = 'none';
        } else {
            btn.innerHTML = 'Показать данные по неделям';
            document.querySelector('.graphic').style.display = 'none';
            document.querySelector('.cumulative-graphic').style.display = 'flex';
        } 
        
    })
})