document.addEventListener('DOMContentLoaded', function() {
    let category = document.querySelector('#id_category');
    category.addEventListener('change', function(){
         change_docs_list(category.value);
    });
    mark_fields_with_Categories();
    change_docs_list(category.value);
})

function change_docs_list(category){
    console.log(category);
    console.log('change_docs_list');
    var doc = document.querySelector('.field-consent_pers_data').parentElement;
    var children = doc.children;
    for (var i = 0; i < children.length; i++) {
        if (!(children[i].classList.contains(category))&&!(children[i].classList.contains('DEF'))){
            children[i].style.display = 'none';
        }
        else{
            children[i].style.display = 'block';
        }
    }
    children[0].style.display = 'block';
}

function mark_fields_with_Categories(){
    var doc;
    doc = document.querySelector('.field-consent_pers_data');
    doc.classList.add('DEF');
    doc = document.querySelector('.field-pasport');
    doc.classList.add('DEF');
    doc = document.querySelector('.field-education_document');
    doc.classList.add('DEF');
    doc = document.querySelector('.field-resume');
    doc.classList.add('DEF');
    
    doc = document.querySelector('.field-worksearcher_certificate');
    doc.classList.add('JOBS');
    doc.classList.add('EMPS');
    

    doc = document.querySelector('.field-workbook');
    doc.classList.add('UEMP');
    doc.classList.add('EMPS');
    doc = document.querySelector('.field-unemployed_certificate');
    doc.classList.add('UEMP');
    doc.classList.add('EMPS');

    doc = document.querySelector('.field-senior_certificate');
    doc.classList.add('SC');

    doc = document.querySelector('.field-parental_leave_confirm');
    doc.classList.add('VACK');
    doc = document.querySelector('.field-birth_certificate');
    doc.classList.add('VACK');
    
    doc = document.querySelector('.field-birth_certificate_undr_seven');
    doc.classList.add('SCHK');
    doc = document.querySelector('.field-notIP_certificate');
    doc.classList.add('SCHK');
}