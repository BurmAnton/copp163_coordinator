document.addEventListener('DOMContentLoaded', function() {
    window.history.replaceState(null, null, `?p=${document.querySelector('.project-btn.btn-primary').dataset.project}`);
    document.querySelector('#CheckAll').addEventListener('click', (event) => {
        var checkbox = event.currentTarget.querySelector('.form-check-input');
        if (event.currentTarget.parentElement.classList.contains('selected-all-row')) {
            checkbox.checked = false;
        } else {
            checkbox.checked = true;
        }
        check_all_rows(checkbox);
    });

    document.querySelectorAll('.check-td').forEach(td =>{
        td.addEventListener('click', (event) =>{
            var checkbox = event.currentTarget.querySelector('.form-check-input');
            if (td.parentElement.classList.contains('selected-row')) {
                checkbox.checked = false;
            } else {
                checkbox.checked = true;
            }
            check_row(checkbox);
        })
    })

    document.querySelector('#change-status-btn').addEventListener('click', (event) => {
        change_statuses();
    })
})

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

 function change_statuses(){
    const data = {};
    data.centers_list = [];
    data.stage = document.querySelector('#stage-select').value;
    document.querySelectorAll('.center-checkbox').forEach(checkbox =>{
        if (checkbox.checked) {
            data.centers_list.push(checkbox.value);
        }
    })
    data.project = document.querySelector('h3').dataset.project;
    const data_stringify = JSON.stringify(data);
    console.log(data);
    fetch('/education_centers/applications?p=zan', {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            'Content-Type': 'application/json'
          },
        body: data_stringify,
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        if (result.message = 'Centers stage changed successfully.'){
            document.location.reload(true);
        }
    })
    
}

function check_all_rows(checkbox){
    if (checkbox.checked) {
        checkbox.parentElement.parentElement.parentElement.classList.add('selected-all-row');
        document.querySelectorAll('.center-checkbox').forEach(checkbox =>{
            checkbox.checked = true;
            checkbox.parentElement.parentElement.parentElement.classList.add('selected-row');
        })
    } else {
        checkbox.parentElement.parentElement.parentElement.classList.remove('selected-all-row');
        document.querySelectorAll('.center-checkbox').forEach(checkbox =>{
            checkbox.checked = false;
            checkbox.parentElement.parentElement.parentElement.classList.remove('selected-row');
        })
    }
    count_selected_rows();
}

function check_row(checkbox){
    if (checkbox.checked) {
        checkbox.parentElement.parentElement.parentElement.classList.add('selected-row');
        var inputs = document.querySelectorAll('.center-checkbox');
        var is_checked = true;
        for(var x = 0; x < inputs.length; x++) {
            is_checked = inputs[x].checked;
            if(is_checked === false) break;
        }
        if(is_checked) {
            document.querySelector('#CheckAll').querySelector('.form-check-input').checked = true;
            document.querySelector('#CheckAll').parentElement.classList.add('selected-all-row');
        }
    } else {
        checkbox.parentElement.parentElement.parentElement.classList.remove('selected-row');
        document.querySelector('#CheckAll').querySelector('.form-check-input').checked = false;
        document.querySelector('#CheckAll').parentElement.classList.remove('selected-all-row');
    }
    count_selected_rows();
}

function count_selected_rows(){
    var inputs = document.querySelectorAll('.center-checkbox');
    var is_checked = true;
    var counter = 0;
    for(var x = 0; x < inputs.length; x++) {
        is_checked = inputs[x].checked;
        if(is_checked){
            counter += 1;
        };
    }
    document.querySelector('.selected-row-count').innerHTML = counter;
}