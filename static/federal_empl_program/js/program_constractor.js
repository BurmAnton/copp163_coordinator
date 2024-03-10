document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.stage-btn').forEach(step =>{
        step.addEventListener('click', () => {change_stage(step)})
    })

    document.querySelectorAll('.edit-module-btn').forEach(btn =>{
        btn.addEventListener('click', () => {
            let row = btn.parentElement.parentElement.parentElement;
            let delete_form = btn.parentElement.querySelector('form');
            btn.classList.toggle("active");
            if  (btn.classList.contains("active")){
                delete_form.style.display = 'block';
                row.querySelector('.module-name').style.display = 'none';
                row.querySelector('.change-module-input').style.display = 'block';
                row.querySelector('.change-module-btn').style.display = 'block';
            } else {
                delete_form.style.display = 'none';
                row.querySelector('.module-name').style.display = 'block';
                row.querySelector('.change-module-input').style.display = 'none';
                row.querySelector('.change-module-btn').style.display = 'none';
            }
        })
    })
})


function change_stage(btn){
    document.querySelector('.stage-btn.btn-primary').classList.add("btn-outline-primary");
    document.querySelector('.stage-btn.btn-primary').classList.remove("btn-primary");
    btn.classList.add("btn-primary");
    btn.classList.remove("btn-outline-primary"); 

    window.history.replaceState(null, null, `?s=${btn.dataset.stage}`);
    let steps = document.querySelectorAll('.stage')

    steps.forEach(step =>{
        step.style.display = 'none';
        if (step.dataset.stage == btn.dataset.stage) {
            step.style.display = 'block';
        }
    })
}