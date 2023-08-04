document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.delay-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.getElementById('competence_switch').style.display = 'none';
    document.getElementById('program_switch').addEventListener('click', () => program_switch());
    document.getElementById('competence_switch').addEventListener('click', () => competence_switch());
    document.getElementById('delays_btn').addEventListener('click', () => delays_switch());
})

function program_switch(){
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'table-row';
    })
    document.querySelectorAll('.non-delay-stage').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.competence-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.competence-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.delay-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.getElementById('program_switch').style.display = 'none';
    document.getElementById('competence_switch').style.display = 'flex';
    document.getElementById('view_name').innerText = 'Программа подготовки';
}

function competence_switch(){
    document.querySelectorAll('.competence-row').forEach(program=> {
        program.style.display = 'table-row';
    })
    document.querySelectorAll('.competence-cell').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.non-delay-stage').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.delay-cell').forEach(program=> {
        program.style.display = 'none';
    })

    document.getElementById('competence_switch').style.display = 'none';
    document.getElementById('program_switch').style.display = 'flex';
    document.getElementById('view_name').innerText = 'Компетенция';
}

function delays_switch(){
    document.querySelectorAll('.competence-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.competence-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.non-delay-stage').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.delay-cell').forEach(program=> {
        program.style.display = 'table-cell';
    })
}