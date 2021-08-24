document.addEventListener('DOMContentLoaded', function() {
    var competence_filter = document.querySelector('.admin-filter-Компетенция').firstElementChild.firstElementChild
    console.log(competence_filter)
    var opt = competence_filter.options[competence_filter.selectedIndex].text;
    console.log(opt)
    fetch(`federal_programs/employment/filter/competence/128`)
    .then(response => response.json())
    .then(competence =>{
        console.log(competence)
    });
})