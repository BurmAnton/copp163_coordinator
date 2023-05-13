document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.step-btn').forEach(step =>{
        step.addEventListener('click', (btn) => {
            document.querySelector('.step-btn.btn-primary').classList.add("btn-outline-primary");
            document.querySelector('.step-btn.btn-primary').classList.remove("btn-primary");
            btn.srcElement.classList.add("btn-primary");
            btn.srcElement.classList.remove("btn-outline-primary");

            let steps = document.querySelectorAll('.step')
            steps.forEach(step =>{
                step.style.display = 'none';
                if (step.dataset.step == btn.srcElement.dataset.step) {
                    step.style.display = 'block';
                }
            })
        })
    })
})
