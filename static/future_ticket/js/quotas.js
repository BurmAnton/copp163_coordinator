function SearchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase().trim();
    table = document.querySelector(".quotas-table");
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        let display = "none"
        let fields = [0, 1, 4, 5, 6]
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
        filter = input.title.split(', ');
        table = document.querySelector(".quotas-table");
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
    table = document.querySelector(".quotas-table");
    column = table.getElementsByTagName("TH")[col];
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
      for (i = 1; i < (rows.length - 1); i++) {
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

  $('#some-field').keyup(function(e){
    if (e.keyCode == '13') {
       e.preventDefault();
       $(this).append("<br />\n");
    }
  });