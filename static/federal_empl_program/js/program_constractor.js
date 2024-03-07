document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.stage-btn').forEach(step =>{
        step.addEventListener('click', (btn) => {
            document.querySelector('.stage-btn.btn-primary').classList.add("btn-outline-primary");
            document.querySelector('.stage-btn.btn-primary').classList.remove("btn-primary");
            btn.srcElement.classList.add("btn-primary");
            btn.srcElement.classList.remove("btn-outline-primary"); 

            window.history.replaceState(null, null, `?s=${btn.srcElement.dataset.stage}`);
            let steps = document.querySelectorAll('.stage')
            
            steps.forEach(step =>{
                step.style.display = 'none';
                if (step.dataset.stage == btn.srcElement.dataset.stage) {
                    step.style.display = 'block';
                }
            })
        })
    })
})