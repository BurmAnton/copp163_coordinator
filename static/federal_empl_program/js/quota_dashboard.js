function FilterFunction(col, filter_id) {
    setTimeout(function() {
        var input, filter, table, tr, td, i, txtValue;
        input = document.querySelector("#"+filter_id).parentElement.querySelector('button');
        filter = input.parentElement.getElementsByClassName('selected');
        options = [];
        Array.from(filter).forEach(input =>{
            options.push(input.querySelector('.text').innerHTML)
        })
        table = document.querySelector(".table");
        tr = table.getElementsByTagName("tr");
        
        if (options.length != 0){
            
            for (i = 2; i+1 < tr.length; i++) {
                let display = "none"
                console.log(tr[i])
                td = tr[i].getElementsByTagName("td")[col];
                
                ed_center_id = td.dataset.id;
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    
                    if (options.includes(txtValue)) {
                        document.querySelectorAll('.plan'+ed_center_id).forEach(group_tr => {
                            group_tr.classList.remove('disapear');
                            console.log(group_tr)
                        })
                    }else{
                        document.querySelectorAll('.plan'+ed_center_id).forEach(group_tr => {
                            group_tr.classList.add('disapear');
                        })
                    }
                }    
            }
        } else {
            for (i = 1; i < tr.length; i++) {
                tr[i].classList.remove('disapear');
            }
        }
    }, 300);
}