document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#disability-check').addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            document.querySelector('#form-disability').style.display = "block";
        } else {
            document.querySelector('#form-disability').style.display = "none";
        }
    })
    
    let first = true;
    document.querySelector('form').addEventListener('click', () =>{
        if (first){
            document.querySelectorAll(".dropdown-toggle").forEach(element => {
                element.click();
                console.log("ok");
            })
            document.querySelector("#Name").select();
            first = false;
        }
        document.querySelectorAll(".dropdown-toggle").forEach(element => {
            element.addEventListener('click', () =>{
                document.querySelectorAll(".city").forEach(element => {
                    element.addEventListener('click', () => {
                        city = element.firstElementChild.innerHTML;
                        const schools = [];
                        document.querySelectorAll(".school").forEach(school => {
                            if (school.dataset.school != city){
                                schools.push(school.innerHTML)
                            }
                        });
                        document.querySelectorAll("a.school").forEach(dropdown => {
                            console.log(dropdown);
                            if (schools.includes(dropdown.firstElementChild.innerHTML)){
                                dropdown.style.display = "none";
                            }else{
                                dropdown.style.display = "block";
                            }
                        });
                        console.log("end");
                    });
                });
            });    
        })
    })
})
