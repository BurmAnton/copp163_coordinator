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
            if (col === 6){
                for (i = 1; i < tr.length; i++) {
                    let display = "none"
                    td = tr[i].getElementsByTagName("td")[col];
                    if (td) {
                        td.querySelectorAll('div').forEach(div =>{
                            if (options.includes(div.innerHTML)) {
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
                        if (options.includes(txtValue)) {
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
    table = document.querySelector("#groups-table");
    tr = table.getElementsByTagName("tr");
    
    for (i = 1; i < tr.length; i++) {
        let display = "none"
        let fields = [0, 1, 2, 3]
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