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
            let phones_str = phones_list.join(", ")
            console.log(phones_str)
            document.querySelector('.phone_input').value = phones_str;
            //emails
            let emails = row.querySelector('.emails')
            let emails_list = Array()
            emails.querySelectorAll('div').forEach(email => {
                emails_list.push(email.innerHTML)
            })
            let emails_str = emails_list.join(", ")
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
function SearchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase().trim();
    table = document.querySelector(".contact-list");
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        let display = "none"
        let fields = [1, 2, 4, 5, 6, 7, 8, 9]
        fields.forEach(col => {
            td = tr[i].getElementsByTagName("td")[col];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    display = "";
                }
            }    
        })
        tr[i].style.display = display;
    }
}
function FilterFunction(col, filter_id) {
    setTimeout(function() {
        var input, filter, table, tr, td, i, txtValue;
        input = document.querySelector("#"+filter_id).parentElement.querySelector('button');
        console.log(input.title)
        filter = input.title.split(', ');
        table = document.querySelector(".contact-list");
        tr = table.getElementsByTagName("tr");
        
        if (!filter[0].includes('Выберите')){
            if (col === 6){
                for (i = 1; i < tr.length; i++) {
                    let display = "none"
                    td = tr[i].getElementsByTagName("td")[col];
                    if (td) {
                        td.querySelectorAll('div').forEach(div =>{
                            if (filter.includes(div.innerHTML)) {
                                tr[i].classList.remove('disapear-'+filter_id);
                            }else{
                                tr[i].classList.add('disapear-'+filter_id);
                            }
                        });
                    }    
                }
            }else{
                for (i = 1; i < tr.length; i++) {
                    let display = "none"
                    td = tr[i].getElementsByTagName("td")[col];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        console.log(td.textContent)
                        console.log(td.innerText)
                        if (filter.includes(txtValue)) {
                            tr[i].classList.remove('disapear-'+filter_id);
                        }else{
                            tr[i].classList.add('disapear-'+filter_id);
                        }
                    }    
                } 
            }
        } else {
            for (i = 1; i < tr.length; i++) {
                tr[i].classList.remove('disapear-'+filter_id);
            }
        }
    }, 300);

}

function sortTable(col) {
    var table, rows, switching, i, x, y, shouldSwitch, column, sorted;
    table = document.querySelector(".contact-list");
    column = table.getElementsByTagName("TH")[col-1];
    sorted = column.classList.contains('sorted');
    document.querySelectorAll('.th-sort-backward').forEach(img => {
        img.classList.add('disappear')
    })
    document.querySelectorAll('.th-sort').forEach(img => {
        img.classList.add('disappear')
    })
    if (sorted) {
        column.querySelector('.th-sort-backward').classList.toggle('disappear')
    } else {
        column.querySelector('.th-sort').classList.toggle('disappear')
    }
    switching = true;
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 2; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("TD")[col];
        y = rows[i + 1].getElementsByTagName("TD")[col];
        if (sorted) {
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                //if so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }else{
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                //if so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
      }
       //check if the two rows should switch place:
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
    column.classList.toggle('sorted');
  }