document.addEventListener('DOMContentLoaded', function() {
    const input = document.querySelector('#id_import_file').classList;
    console.log(input);
    input.add('form-control');

    document.querySelector('.change_contact_btn').addEventListener("click", () => {
        document.querySelector('.change_contact_btn').classList.toggle("disappear")
        document.querySelector('.change_contact_panel').classList.toggle("disappear")

        let modal = document.querySelector('#ContactModal')
        modal.querySelectorAll('input').forEach(input =>{
            input.disabled = false;
        })
        modal.querySelectorAll('select').forEach(input =>{
            console.log(input)
            input.disabled = false;
            input.parentElement.querySelector('button').classList.toggle("disabled");
        })
        modal.querySelector('textarea').disabled = false;
    })

    document.querySelectorAll('.contact-row').forEach(row =>{
        row.addEventListener("click", () => {
            if (document.querySelector('.change_contact_btn').classList.contains("disappear")){
                document.querySelector('.change_contact_btn').classList.toggle("disappear")
                document.querySelector('.change_contact_panel').classList.toggle("disappear")

                let modal = document.querySelector('#ContactModal')
                modal.querySelectorAll('input').forEach(input =>{
                    input.disabled = true;
                })
                modal.querySelectorAll('select').forEach(input =>{
                    console.log(input)
                    input.disabled = true;
                    input.parentElement.querySelector('button').classList.toggle("disabled");
                })
                modal.querySelector('textarea').disabled = true;
            }

            let id = row.querySelector('.id').innerHTML;
            document.querySelector('.ID_input').value = id;
            let last_name = row.querySelector('.last_name').innerHTML;
            document.querySelector('.last_name_input').value = last_name;
            let first_name = row.querySelector('.first_name').innerHTML;
            document.querySelector('.first_name_input').value = first_name;
            let middle_name = row.querySelector('.middle_name').innerHTML;
            document.querySelector('.middle_name_input').value = middle_name;
            let job_title = row.querySelector('.job_title').innerHTML;
            document.querySelector('.job_title_input').value = job_title;
            let commentary = row.querySelector('.commentary').innerHTML;
            if (commentary != 'None'){
                document.querySelector('.commentary_input').value = commentary;
            }   
            //телефоны
            let phones = row.querySelector('.phones')
            let phones_list = Array()
            phones.querySelectorAll('div').forEach(phone => {
                phones_list.push(phone.innerHTML)
            })
            let phones_str = phones_list.join(" , ")
            document.querySelector('.phone_input').value = phones_str;
            //emails
            let emails = row.querySelector('.emails')
            let emails_list = Array()
            emails.querySelectorAll('div').forEach(email => {
                emails_list.push(email.innerHTML)
            })
            let emails_str = emails_list.join(" , ")
            document.querySelector('.email_input').value = emails_str;
            //Проекты
            let projects = row.querySelector('.projects');
            let projects_list = Array();
            for (const project of projects.children) {
                projects_list.push(project.innerHTML)
            }
            document.querySelector('.ContactModalBtn').click();
            document.querySelector('.project_input_selectpicker').disabled = false;
            let projects_input = document.querySelector('.project_input')
            projects_input.querySelector('.btn').click();
            let clicked_projects_list = Array();
            projects_input.querySelectorAll('li').forEach(option =>{
                let option_text = option.firstChild.lastChild.innerHTML
                if (option.firstChild.classList.contains('selected')){
                    option.firstChild.click();
                }
                if (projects_list.includes(option_text) && !clicked_projects_list.includes(option_text)){
                    option.firstChild.click();
                    clicked_projects_list.push(option_text);
                }
            })
            document.querySelector('.project_input_selectpicker').disabled = true;
            //Организация
            document.querySelector('.organization_input_selectpicker').disabled = false;
            let org = row.querySelector('.organization').innerHTML;

            let org_input = document.querySelector('.organization_input')
            org_input.querySelector('.btn').click();

            org_input.querySelectorAll('li').forEach(option =>{
                let option_text = option.firstChild.lastChild.innerHTML
                if (org === option_text){
                    option.firstChild.click();
                    clicked_projects_list.push(option_text);
                }
            })
            document.querySelector('.organization_input_selectpicker').disabled = true;
        })
    });
})