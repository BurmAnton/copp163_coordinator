document.addEventListener('DOMContentLoaded', function() {
    stage = document.querySelector('.stage').innerHTML;
    stages = [1,2,3,4]

    if (stage == "Профориентация"){ current_stage = 1; stages = [2,3,4]; }
    else if (stage == "Запись в группу"){ current_stage = 2; stages = [1,3,4]; }
    else if (stage == "Подача заявки"){ current_stage = 3; stages = [2,1,4]; }
    else { current_stage = 4; stages = [2,3,1]; }

    for (stage in stages){
        stage_body = document.querySelector('.stage-'+ stages[stage] + '.stage-body')
        stage_body.style.display = 'none'
        
        stage_number = document.querySelector('.stage-' + stages[stage] + '.stage-number-current')
        stage_number.classList.remove("stage-number-current")
        if (stages[stage] < current_stage) {
            stage_number.classList.add("stage-number-hidden")

            stage_check = document.querySelector('.stage-' + stages[stage] + '.stage-check-hidden')
            stage_check.classList.remove("stage-check-hidden")
            stage_check.classList.add("stage-check")
        } else {
            stage_number.classList.add("stage-number")
        }
        
        stage_end = document.querySelector('.stage-' + stages[stage] + '.stage-end-btn')
        stage_end.classList.remove("stage-end-btn")
        stage_end.classList.add("stage-end-btn-hidden")

        stage_end = document.querySelector('.stage-' + stages[stage] + '.deploy-btn-hidden')
        stage_end.classList.remove("deploy-btn-hidden")
        stage_end.classList.add("deploy-btn")
    }
})