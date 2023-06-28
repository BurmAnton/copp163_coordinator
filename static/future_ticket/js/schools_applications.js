function FilterFunction(col, filter_id) {
    setTimeout(function() {
        var input, filter, table, tr, td, i, txtValue;
        input = document.querySelector("#"+filter_id).parentElement.querySelector('button');
        filter = input.title.split(', ');
        table = document.querySelector(".applications-table");
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

function SearchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase().trim();
    table = document.querySelector(".applications-table");
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        let display = "none"
        let fields = [0, 1, 2, 4, 5]
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