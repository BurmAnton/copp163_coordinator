document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.parent-step').forEach(field =>{
        field.addEventListener('input', () => {
            cheak_parent_step()
        })
    })
    document.querySelector('.parent-step-end').addEventListener('click', () => {
        document.querySelector('.parent-step-end').style.display = 'none';
        document.querySelectorAll('.first-step').forEach(field =>{
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.first-step-select').forEach(field =>{
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.first-step-optional').forEach(field =>{
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.parent-step').forEach(field => {
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.parent-step-optional').forEach(field => {
            field.style.display = 'none';
        })
        document.querySelector('.step-title').firstElementChild.innerHTML = "Шаг 2/3: Данные ребенка";
        document.querySelector('.parent-step-back').style.display = 'block';
        document.querySelector('.first-step-end').style.display = 'block';
    })
    document.querySelector('.parent-step-back').addEventListener('click', () => {
        document.querySelector('.parent-step-end').style.display = 'block';
        document.querySelectorAll('.first-step').forEach(field =>{
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.first-step-select').forEach(field =>{
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.first-step-optional').forEach(field =>{
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.parent-step').forEach(field => {
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.parent-step-optional').forEach(field => {
            field.style.display = 'block';
        })
        document.querySelector('.step-title').firstElementChild.innerHTML = "Шаг 1/3: Данные родетеля";
        document.querySelector('.parent-step-back').style.display = 'none';
        document.querySelector('.first-step-end').style.display = 'none';
        document.querySelector('.first-step-hidden').style.display = 'none';
    })
    document.querySelectorAll('.first-step').forEach(field =>{
        field.addEventListener('input', () => {
            cheak_first_step()
        })
    })
    document.querySelectorAll('.first-step-select').forEach(field =>{
        field.addEventListener('change', () => {
            cheak_first_step()
        })
    })
    document.querySelector('.first-step-end').addEventListener('click', () => {
        let button = document.querySelector('.first-step-end')
        document.querySelectorAll('.finale-step').forEach(field =>{
            field.style.display = 'block';
            button.style.display = 'none';
        })
        document.querySelectorAll('.first-step').forEach(field => {
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.first-step-select').forEach(field => {
            field.parentElement.style.display = 'none';
        })
        document.querySelectorAll('.first-step-optional').forEach(field => {
            field.parentElement.style.display = 'none';
        })
        document.querySelector('.first-step-hidden').style.display = 'none';
        document.querySelector('.step-title').firstElementChild.innerHTML = "Шаг 3/3: Данные для авторизации";
        document.querySelector('.first-step-back').style.display = 'block';
        document.querySelector('.parent-step-back').style.display = 'none';
        document.querySelector('.first-step-end').style.display = 'none';
    })
    document.querySelector('.first-step-back').addEventListener('click', () => {
        let button = document.querySelector('.first-step-end')
        document.querySelectorAll('.finale-step').forEach(field =>{
            field.style.display = 'none';
            button.style.display = 'block';
        })
        document.querySelectorAll('.first-step').forEach(field => {
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.first-step-select').forEach(field => {
            field.parentElement.style.display = 'block';
        })
        document.querySelectorAll('.first-step-optional').forEach(field => {
            field.style.display = 'block';
        })
        document.querySelector('.step-title').firstElementChild.innerHTML = "Шаг 2/3: Данные ребенка";
        document.querySelector('.first-step-back').style.display = 'none';
        document.querySelector('.parent-step-back').style.display = 'block';
    })
    document.querySelector('#disability-check').addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            document.querySelector('#form-disability').style.display = "block";
        } else {
            document.querySelector('#form-disability').style.display = "none";
        }
    })
    
    let first = true;
    document.querySelector('form').addEventListener('click', () =>{
        if (first){
            document.querySelectorAll(".dropdown-toggle").forEach(element => {
                element.click();
            })
            document.querySelector("#Name").select();
            first = false;
        }
        document.querySelectorAll(".dropdown-toggle").forEach(element => {
            element.addEventListener('click', () =>{
                document.querySelectorAll(".city").forEach(element => {
                    element.addEventListener('click', () => {
                        city = element.firstElementChild.innerHTML;
                        const schools = [];
                        document.querySelectorAll(".school").forEach(school => {
                            if (school.dataset.school != city){
                                schools.push(school.innerHTML)
                            }
                        });
                        document.querySelectorAll("a.school").forEach(dropdown => {
                            if (schools.includes(dropdown.firstElementChild.innerHTML)){
                                dropdown.style.display = "none";
                            }else{
                                dropdown.style.display = "block";
                            }
                        });
                    });
                });
            });    
        })
    })
})
function cheak_parent_step(){
    let fields_is_filled = true
    let button = document.querySelector('.parent-step-end')
    document.querySelectorAll('.parent-step').forEach(field => {
        if (!field.value) {
            fields_is_filled = false
        }
    })
    if (fields_is_filled){
        button.classList.remove('disabled')
        button.classList.remove('btn-secondary')
        button.classList.add('btn-primary')
    } else {
        button.classList.add('disabled')
        button.classList.add('btn-secondary')
        button.classList.remove('btn-primary')
    }
}

function cheak_first_step(){
    let fields_is_filled = true
    let button = document.querySelector('.first-step-end')
    document.querySelectorAll('.first-step').forEach(field => {
        if (!field.value) {
            fields_is_filled = false
        }
    })
    document.querySelectorAll('.first-step-select').forEach(select => {
        console.log(select.value)
        if (select.value === "") {
            fields_is_filled = false
        }
    })
    if (fields_is_filled){
        button.classList.remove('disabled')
        button.classList.remove('btn-secondary')
        button.classList.add('btn-primary')
    } else {
        button.classList.add('disabled')
        button.classList.add('btn-secondary')
        button.classList.remove('btn-primary')
    }
}