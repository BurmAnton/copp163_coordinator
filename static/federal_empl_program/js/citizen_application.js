document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.second-step').forEach(input =>{
        input.style.display = 'none';
    });
    document.querySelectorAll('.first-step').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.first-step-mandatory')});
    });
    document.querySelector('#Competence').addEventListener('input', () => {cheak_step('.second-step-mandatory')});
    document.querySelectorAll('.second-step-mandatory-select').forEach(input =>{
        input.addEventListener('change', () => {cheak_step('.second-step-mandatory')});
    });
    document.querySelector('.btn-forward').addEventListener('click', () => {
        document.querySelectorAll('.first-step').forEach(input =>{
            input.style.display = 'none';
        });
        document.querySelectorAll('.second-step').forEach(input =>{
            input.style.display = 'block';
        });
        document.querySelector('.btn-forward').style.display = 'none';
        document.querySelector('.btn-backward').style.display = 'block';
    })
    document.querySelector('.btn-backward').addEventListener('click', () => {
        document.querySelectorAll('.second-step').forEach(input =>{
            input.style.display = 'none';
        });
        document.querySelectorAll('.first-step').forEach(input =>{
            input.style.display = 'flex';
        });
        document.querySelector('.btn-backward').style.display = 'none';
        document.querySelector('.btn-forward').style.display = 'block';
    })
})

function cheak_step(step_name){
    let is_filled = true;
    document.querySelectorAll(step_name).forEach(input => {
        if (input.firstElementChild.value === "") {
            is_filled = false;
        };
    });
    if (step_name == '.second-step-mandatory') {
        is_filled = true;
        if (document.querySelector('#Competence').value === "") {
            is_filled = false;
        };
    }
    document.querySelectorAll(`${step_name}-select`).forEach(input => {
        if (input.value === "") {
            is_filled = false;
        };
    });
    if (step_name == '.second-step-mandatory') {
        if (is_filled) {activate_submit_btn()}
        else {disable_submit_btn()};
    } else {
        if (is_filled) {activate_forward_btn()}
        else {disable_forward_btn()};
    }
};

function activate_forward_btn(){
    button = document.querySelector('.btn-forward');
    button.classList.remove('disabled');
    button.classList.remove('btn-secondary');
    button.classList.add('btn-primary');
};

function disable_submit_btn(){
    button = document.querySelector('.btn-submit');
    button.classList.add('disabled');
    button.classList.add('btn-secondary');
    button.classList.remove('btn-primary');
};

function activate_submit_btn(){
    button = document.querySelector('.btn-submit');
    button.classList.remove('disabled');
    button.classList.remove('btn-secondary');
    button.classList.add('btn-primary');
};

function disable_forward_btn(){
    button = document.querySelector('.btn-forward');
    button.classList.add('disabled');
    button.classList.add('btn-secondary');
    button.classList.remove('btn-primary');
};
