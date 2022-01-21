document.addEventListener('DOMContentLoaded', function() {
    //Скрываем форму регистрации и выбора типа регистрации
    document.querySelector('.reg-form').style.display = "none";
    document.querySelector('.reg-choice-form').style.display = "none";

    //Добавляем прослушивание кнопки регистрации
    document.querySelector('.reg-button').addEventListener('click', () => {choice()});
    
    document.querySelector("#form-disability").style.display = "none";
    document.querySelector('#disability-check').addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            document.querySelector('#form-disability').style.display = "block";
        } else {
            document.querySelector('#form-disability').style.display = "none";
        }
    })

    document.querySelectorAll('.parent-step-mandatory').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.parent-step-mandatory')});
    });
    document.querySelectorAll('.child-step-mandatory').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.child-step-mandatory')});
    });
    document.querySelectorAll('.child-step-mandatory-select').forEach(input =>{
        input.addEventListener('change', () => {cheak_step('.child-step-mandatory')});
    });

    document.querySelector('.btn-forward').addEventListener('click', () => {
        click_forward();
    });

    document.querySelector('.btn-backward').addEventListener("click", () => window.history.back());
    document.querySelector('.btn-submit').addEventListener('click', () =>{
        send_reg_info();
    });


    document.querySelectorAll('.auth-step').forEach(field => {
        field.style.display = 'none';
    })
    document.querySelector('.btn-submit').style.display = 'none';

    //Востановление пароля
    document.querySelector('.pass-recovery').addEventListener('click', () => {
        passRecovery();
    });
    document.querySelector('.btn-recovery-code').addEventListener('click', () => {
        passRecovery();
    });

    replaceState();
});

function replaceState(){
    //Определяем начальное состояние
    reg_choice_form = document.querySelector('.reg-choice-form');
    let state = {
        title: document.querySelector('title').innerHTML,
        form_title: 'auth',
        form_subtitle: 'none',
        sign_form: document.querySelector('.sign-form').style.display,
        recovery_form: document.querySelector('.pass-rec-form').style.display,
        recovery_btn: "Отправить",
        reg_choice_form: reg_choice_form.style.display,
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: document.querySelector('.reg-form').style.display,
        first_step: document.querySelector('.parent-step-mandatory').style.display,
        second_step: document.querySelector('.child-step-mandatory').style.display,
        last_step: document.querySelector('.auth-step').style.display
    }
    //Заменяем начальное состояние
    window.history.replaceState(state, null, "");
    renderState(state);
}

function renderState(state){
    //Меняем название страницы
    document.querySelector('title').innerHTML = state.title;
    //Меняем заголовок формы
    let form_title = 'Регистрация';
    if (state.form_title === 'auth') {
        form_title = 'Авторизация';
    }  else if (state.form_title === 'choice') {
        form_title = 'Выберите способ регистрации';
    } else if (state.form_title === 'recovery') {
        form_title = 'Востановление пароля';
    }
    document.querySelector('.form-title').firstElementChild.innerHTML = form_title;
    //Меняем подзаголовок формы
    if (state.form_subtitle != 'none'){
        document.querySelector('.step-title').firstElementChild.innerHTML = change_step_title(state.form_subtitle);
    }
    //Меняем форму
    document.querySelector('.sign-form').style.display = state.sign_form;

    document.querySelector('.pass-rec-form').style.display = state.recovery_form;
    document.querySelector('.btn-recovery-code').innerHTML =state.recovery_btn;
    if (state.recovery_btn === 'Ввести') {
        document.querySelector('.email-step').style.display = 'none';
        document.querySelector('.code-step').style.display = 'flex';
    } else if (state.recovery_btn === 'Сменить пароль') {
        document.querySelector('.code-step').style.display = 'none';
        document.querySelectorAll('.password-step').forEach(input =>{
            input.style.display = 'flex';
        });
    };

    document.querySelector('.reg-choice-form').style.display = state.reg_choice_form;
    document.querySelector('.reg-form').style.display = state.reg_form;

    if (state.reg_form != 'none') {
        if (state.first_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-forward').style.display = 'block';
            document.querySelector('.btn-submit').style.display = 'none';
            document.querySelector('.child-step-hidden').style.display = 'none';
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-backward').style.display = 'none';
            cheak_step('.parent-step-mandatory');
        } else if (state.second_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-forward').style.display = 'block';
            document.querySelector('.btn-submit').style.display = 'none';
            if (state.reg_choice === 'parent') {
                document.querySelector('.btn-backward').style.display = 'block';
            }
            cheak_step('.child-step-mandatory');
        } else if (state.last_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.child-step-hidden').style.display = 'none';
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelector('.btn-forward').style.display = 'none';
            document.querySelector('.btn-submit').style.display = 'block';
            document.querySelector('.btn-backward').style.display = 'block';
        };
    };
}

function choice(){
    //Описывает состояние после нажатия кнопки "Регистрации" (шаг "Выбор способа регистрации")
    let state = {
        title: 'Регистрация | ЦОПП СО',
        form_title: "choice",
        form_subtitle: 'none',
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: "flex",
        reg_choice: document.querySelector('.reg-choice-form').dataset.choice,
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Добавляем и рендерим новое состояние в историю
    window.history.pushState(state, null, "/bilet/registration/choice");
    renderState(state);

    //Обработка кнопок "Назад/Вперёд"
    window.onpopstate = function (event) {
        if (event.state) { state = event.state; }
        renderState(state);
    };

    //Добавляем прослушивание кнопок выбора типа регистрации
    reg_choice_form = document.querySelector('.reg-choice-form');
    document.querySelectorAll('.option-btn').forEach(btn =>{
        btn.addEventListener('click', () => {
            if (btn.classList.contains('parent-option-btn')){
                reg_choice_form.dataset.choice = 'parent';
            }
            else {
                reg_choice_form.dataset.choice = 'child';
                document.querySelector('.btn-backward').style.display = 'none';
            }
            registration();
        });
    });
}

function registration(){
    let reg_choice_form = document.querySelector('.reg-choice-form');
    let subtitle = 'parent-step';
    let first_step = 'flex';
    let second_step = 'none';
    if (reg_choice_form.dataset.choice === 'child') {
        subtitle = 'child-step';
        second_step = 'flex';
        first_step = 'none';
    }
    
    let state = {
        title: 'Регистрация | ЦОПП СО',
        form_title: 'registration',
        form_subtitle: subtitle,
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: 'block',
        first_step: first_step,
        second_step: second_step,
        last_step: 'none'
    }

    window.history.pushState(state, null, `/bilet/registration/${reg_choice_form.dataset.choice}/1`);
    renderState(state);

    //Обработка кнопки "Назад"
    window.onpopstate = function (event) {
        if (event.state) { state = event.state; }
        renderState(state);
    };
}

function cheak_step(step_name){
    console.log(`cheak-${step_name}`);
    let is_filled = true;
    document.querySelectorAll(step_name).forEach(input => {
        console.log(`forEach`);
        if (input.firstElementChild.value === "") {
            is_filled = false;
        };
    });
    document.querySelectorAll(`${step_name}-select`).forEach(input => {
        if (input.value === "") {
            is_filled = false;
        };
    });

    if (is_filled) {activate_forward_btn()}
    else {disable_forward_btn()};

    disability_cheak = document.querySelector('.disability-check');
    if (!disability_cheak.checked){
        document.querySelector(".child-step-hidden").style.display = "none";
    }
    console.log(`is_filled: ${is_filled}`);
};

function activate_forward_btn(){
    button = document.querySelector('.btn-forward');
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

function change_step_title(step){
    option = document.querySelector('.reg-choice-form').dataset.choice;
    disability_label = document.querySelector(".disability-label");

    if (step === "parent-step"){
        return "Шаг 1/3: Данные родителя";
    } else if (step === "child-step") {
        if (option === 'parent'){
            disability_label.innerHTML = "У ребенка ОВЗ";
            return "Шаг 2/3: Данные ученика";
        } 
        disability_label.innerHTML = "Я отношусь к лицам с ОВЗ";
        return "Шаг 1/2: Личные данные";
    } else if (step === "auth-step") {
        if (option === 'parent'){
            return "Шаг 3/3: Данные для авторизации";
        }
        return "Шаг 2/2: Данные для авторизации";
    } else if (step === "email_recovery") {
        return "Введите Ваш email и мы пришлём вам код для востановления пароля.";
    } else if (step === "code_recovery") {
        return "На указанный email отправленно письмо с кодом подтверждения."
    } else if (step === "pass_recovery") {
        return "Создайте новый пароль для вашей учётной записи."
    }
}
     
function click_forward(){
    reg_choice_form = document.querySelector('.reg-choice-form');
    child_step = document.querySelector('.child-step');
    parent_step = document.querySelector('.parent-step');

    let first_step = 'none';
    let second_step  = 'none';
    let last_step  = 'none';
    let subtitle  = 'child-step';
    let path = '2';

    if (child_step.style.display != 'none'){
        second_step = 'none';
        last_step = 'flex';
        if (reg_choice_form.dataset.choice === 'parent') {
            path = '3';
        }
        subtitle = 'auth-step';
    } else if (parent_step.style.display != 'none'){
        first_step = 'none';
        second_step = 'flex';
    };
    
    let state = {
        title: document.querySelector('title').innerHTML,
        form_title: 'registration',
        form_subtitle: subtitle,
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: 'block',
        first_step: first_step,
        second_step: second_step,
        last_step: last_step
    }
    //Заменяем начальное состояние
    window.history.pushState(state, null, `/bilet/registration/${reg_choice_form.dataset.choice}/${path}`);
    renderState(state);
};

function send_reg_info(){
    console.log(document.querySelector("#Email").value)
    fetch('/bilet/registration/', {
        method: 'POST',
        body: JSON.stringify({
            email: document.querySelector("#Email").value,
            password: document.querySelector("#InputPasswordReg").value,
            confirmation: document.querySelector("#СonfirmPassword").value,
            
            first_name: document.querySelector("#Name").value,
            last_name: document.querySelector("#LastName").value,
            middle_name: document.querySelector("#MiddleName").value,
            birthday: document.querySelector("#Birthday").value,
            phone: document.querySelector("#Phone").value,
            disability_check: document.querySelector("#disability-check").value,
            disability_type: document.querySelector("#disability_type").value,
            
            school_id: document.querySelector("#School").value,
            grade_number: document.querySelector("#school_class").value,
            grade_letter: document.querySelector("#school_class_latter").value,
        })
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            if (result.message === "Account created successfully."){
                document.querySelector(".email-login").value = document.querySelector("#Email").value;
                document.querySelector("#InputPassword").value = document.querySelector("#InputPasswordReg").value;
                document.querySelector(".sign-button").click();
            }
        })
};

function passRecovery() {
    let form = document.querySelector('.pass-rec-form');
    let email_input = document.querySelector('.email-step');
    let code_input = document.querySelector('.code-step');
    //Определяем текущий шаг востановления пароля
    if (form.style.display === "none"){
        //Шаг 1. Запрашиваем email
        emailInput();
    } else if (email_input.style.display != "none") {
        //Шаг 2. Запрашиваем код из письма
        fetch('/bilet/password/recovery/1/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.message == 'Email exict') {
                codeInput();
            }
            else {}
        })
    } else if (code_input.style.display != "none") {
        fetch('/bilet/password/recovery/2/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
                code: document.querySelector(".code-recovery").value
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result.message == 'Code matches') {
                passChange();
            }
            else {}
        })
    } else {
        fetch('/bilet/password/recovery/3/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
                password: document.querySelector(".password-recovery").value,
                confirmation: document.querySelector(".confirmation-recovery").value
            }),
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message)
            if (result.message == 'Password changed') {
                document.querySelector(".email-login").value = document.querySelector(".email-recovery").value;
                document.querySelector("#InputPassword").value = document.querySelector(".password-recovery").value;
                document.querySelector(".sign-button").click();
            }
            else {}
        })
    }
}

function emailInput() {
    title = 'Востановление пароля';
    form_title = 'recovery';
    form_subtitle = 'email_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/bilet/registration/recovery/1`);
    renderState(state);
}   

function codeInput() {
    title = 'Востановление пароля';
    form_title = 'recovery';
    form_subtitle = 'code_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Ввести",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/bilet/registration/recovery/2`);
    renderState(state);
}

function passChange() {
    title = 'Востановление пароля';
    form_title = 'recovery';
    form_subtitle = 'pass_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Сменить пароль",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/bilet/registration/recovery/3`);
    renderState(state);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}