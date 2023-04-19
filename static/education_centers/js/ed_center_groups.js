document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#id_import_file').forEach(input =>{
        input.classList.add("form-control");
        input.style.width = "250px";
        //input.style.margin = "auto";
        input.parentElement.parentElement.querySelector('label').remove();
    })
    document.querySelectorAll('.act-modal .act_groups').forEach(input =>{
        input.addEventListener('change', (select) => {
            let groups_list = $(input).val()
            document.querySelectorAll('.act-modal .students_list').forEach(group => {
                if (groups_list.includes(group.dataset.group)) {
                    group.style.display = 'block';
                    group.querySelectorAll('input').forEach(input =>{
                        input.required = true;
                    })
                } else {
                    group.style.display = 'none';
                    group.querySelectorAll('input').forEach(input =>{
                        input.required = false;
                    })
                }
            })
        })
    })
})