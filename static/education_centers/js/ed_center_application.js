document.addEventListener('DOMContentLoaded', function() {
    document.body.innerHTML = document.body.innerHTML.replace(/None/g, '');
    let stage = document.querySelector('.stage-h3').dataset.stage
    let user = document.querySelector('.stage-h3').dataset.user

    window.history.replaceState(null, null, `?p=${document.querySelector('.project-btn.btn-primary').dataset.project}&s=${document.querySelector('.step-btn.btn-primary').dataset.step}`);
    document.querySelectorAll('.step-btn').forEach(step =>{
        step.addEventListener('click', (btn) => {
            document.querySelector('.step-btn.btn-primary').classList.add("btn-outline-primary");
            document.querySelector('.step-btn.btn-primary').classList.remove("btn-primary");
            btn.srcElement.classList.add("btn-primary");
            btn.srcElement.classList.remove("btn-outline-primary"); 

            window.history.replaceState(null, null, `?p=${document.querySelector('.project-btn.btn-primary').dataset.project}&s=${btn.srcElement.dataset.step}`);
            let steps = document.querySelectorAll('.step')
            
            steps.forEach(step =>{
                step.style.display = 'none';
                if (step.dataset.step == btn.srcElement.dataset.step) {
                    step.style.display = 'block';
                }
            })
        })
    })
    document.querySelector('#IsNewProfession').addEventListener('click', (checkbox) => {
        if (checkbox.srcElement.checked) {
            document.querySelector('#Profession').parentElement.parentElement.style.display = 'none';
            document.querySelector('#Profession').required = false;
            document.querySelector('#NewProfession').parentElement.style.display = 'block';
            document.querySelector('#NewProfession').required = true;
            document.querySelector('#ProfEnviroment').parentElement.parentElement.style.display = 'block';
            document.querySelector('#ProfEnviroment').required = true;
        } else {
            document.querySelector('#Profession').parentElement.parentElement.style.display = 'block';
            document.querySelector('#Profession').required = true;
            document.querySelector('#NewProfession').parentElement.style.display = 'none';
            document.querySelector('#NewProfession').required = false;
            document.querySelector('#ProfEnviroment').parentElement.parentElement.style.display = 'none';
            document.querySelector('#ProfEnviroment').required = false;
        }
    })
    
})

