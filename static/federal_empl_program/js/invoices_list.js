function SearchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase().trim();
    table = document.querySelector("#groups-table");
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        let display = "none"
        let fields = [0, 1, 3]
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
        filter = input.parentElement.getElementsByClassName('selected');
        options = [];
        Array.from(filter).forEach(input =>{
            options.push(input.querySelector('.text').innerHTML)
        })
        table = document.querySelector("#groups-table");
        tr = table.getElementsByTagName("tr");
        
        if (options.length != 0){
            for (i = 1; i < tr.length; i++) {
                let display = "none"
                td = tr[i].getElementsByTagName("td")[col];
                group_id = td.dataset.id;
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    
                    if (options.includes(txtValue)) {
                        td.parentElement.classList.remove('disapear-'+filter_id);
                    }else{
                        td.parentElement.classList.add('disapear-'+filter_id);
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
