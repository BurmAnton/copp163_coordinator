document.addEventListener('DOMContentLoaded', function() {
    document.querySelector(".nav-link-fp").classList.remove("active")
    setTimeout(function(){
        document.querySelectorAll('.filter-option-inner-inner').forEach(selector => {
            selector.click();
        })
        document.querySelector('.navbar-brand').click();
    }, 300);

    setTimeout(function(){
        document.querySelectorAll(".dropdown-item").forEach(dropdown => {
            dropdown.addEventListener('click', () => {
                setTimeout(function(){
                    filter()
                }, 100)
            });
        })
        document.querySelectorAll(".actions-btn").forEach(dropdown => {
            dropdown.addEventListener('click', () => {
                setTimeout(function(){
                    filter()
                }, 100)
            });
        })
    }, 2000);
})

function filter(){

    let options = []
    document.querySelectorAll(".option-type").forEach(option => {
        if (option.classList.contains("selected")){
            options.push(option.lastElementChild.innerHTML)
        }
    })
    console.log(options)
    let cities = []
    document.querySelectorAll(".option-city").forEach(city => {
        if (city.classList.contains("selected")){
            cities.push(city.lastElementChild.innerHTML)
        }
    })
    let centers = []
    document.querySelectorAll(".option-ed").forEach(center => {
        if (center.classList.contains("selected")){
            centers.push(center.lastElementChild.innerHTML)
        }
    })
    let competencies = []
    document.querySelectorAll(".option-competence").forEach(competence => {
        if (competence.classList.contains("selected")){
            competencies.push(competence.lastElementChild.innerHTML)
        }
    })
    document.querySelectorAll(".col").forEach(card => {
        card.style.display = "block"
        if (!(options.includes("Оффлайн"))&&(card.dataset.type === "on")){
            card.style.display = "none"
        }
        if (!(options.includes("Онлайн")) && card.dataset.type === "off"){
            card.style.display = "none"
        }
        if (!(options.includes("Оффлайн"))&&!(options.includes("Онлайн"))){
            card.style.display = "block"
        }
        if ((options.includes("Оффлайн"))&&(options.includes("Онлайн"))){
            card.style.display = "block"
        }
        ed_center_selector = document.querySelector("[data-id='ed_center']")
        if (ed_center_selector.title != 'Центры обучения'){
            if (!centers.includes(card.dataset.education_center)){
                card.style.display = "none"
            }
        }
        competencies_selector = document.querySelector("[data-id='competence']")
        if (competencies_selector.title != 'Компетенции'){
            if (!competencies.includes(card.dataset.competence)){
                card.style.display = "none"
            }
        }
        cities_selector = document.querySelector("[data-id='city']")
        if (cities_selector.title != 'Населённые пункты'){
            if (!cities.includes(card.dataset.city)){
                card.style.display = "none"
            }
        }
    })
}
