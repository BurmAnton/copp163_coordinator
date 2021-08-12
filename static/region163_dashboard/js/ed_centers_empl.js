document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.getElementById('competence_switch').style.display = 'none';
    document.getElementById('program_switch').addEventListener('click', () => program_switch());
    document.getElementById('competence_switch').addEventListener('click', () => competence_switch());
})

function program_switch(){
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'table-row';
    })
    document.querySelectorAll('.competence-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.competence-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.getElementById('program_switch').style.display = 'none';
    document.getElementById('competence_switch').style.display = 'flex';
}

function competence_switch(){
    document.querySelectorAll('.competence-row').forEach(program=> {
        program.style.display = 'table-row';
    })
    document.querySelectorAll('.competence-cell').forEach(program=> {
        program.style.display = 'table-cell';
    })
    document.querySelectorAll('.program-cell').forEach(program=> {
        program.style.display = 'none';
    })
    document.querySelectorAll('.program-row').forEach(program=> {
        program.style.display = 'none';
    })
    document.getElementById('competence_switch').style.display = 'none';
    document.getElementById('program_switch').style.display = 'flex';
}