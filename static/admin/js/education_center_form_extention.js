document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.field-education_center').style.display = 'none';
    fetch(`/education_centers`)
    .then(response => response.json())
    .then(center =>{
        if (center != false){
            console.log(center)
            ed_centers = document.getElementById('id_education_center')
            opts = document.getElementById('id_education_center').options
            var sel = document.getElementById('id_education_center');
            var opts = sel.options;
            for (var opt, j = 0; opt = opts[j]; j++) {
                console.log(opt.innerHTML)
                if (opt.innerHTML == center) {
                sel.selectedIndex = j;
                break;
                }
            }
        }
    });
})