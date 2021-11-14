document.addEventListener('DOMContentLoaded', function() {
    console.log("fuck!")
    document.querySelector(".form").addEventListener('click', () =>{
        document.querySelectorAll(".dropdown-item").forEach(field =>{
            field.addEventListener('click', () =>{
                reg_adm = field.firstElementChild.innerHTML
                if(reg_adm==="Департамент образования Администрации городского округа Тольятти"){
                    reg_adm="DEPTOL"
                }
                if(reg_adm==="Северное управление"){
                    reg_adm="NADM"
                }
                if(reg_adm==="Кинельское управление"){
                    reg_adm="KINADM"
                }
                if(reg_adm==="Самарское управление"){
                    reg_adm="SAMADM"
                }
                if(reg_adm==="Западное управление"){
                    reg_adm="WADM"
                }
                if(reg_adm==="Тольяттинское управление министерства образования и науки Самарской области"){
                    reg_adm="TADM"
                }
                if(reg_adm==="Северо-Западное управление"){
                    reg_adm="NWADM"
                }
                if(reg_adm==="Юго-Западное управление"){
                    reg_adm="SWADM"
                }
                if(reg_adm==="Поволжское управление"){
                    reg_adm="POVADM"
                }
                if(reg_adm==="Южное управление"){
                    reg_adm="SADM"
                }
                if(reg_adm==="Департамент образования Администрации городского округа Самара"){
                    reg_adm="DEPSAM"
                }
                if(reg_adm==="Юго-Восточное управление"){
                    reg_adm="SEADM"
                }
                if(reg_adm==="Отрадненское управление"){
                    reg_adm="OTRADM"
                }
                if(reg_adm==="Центральное управление"){
                    reg_adm="CENTADM"
                }
                if(reg_adm==="Северо-Восточное управление"){
                    reg_adm="NEADM"
                }
                if(reg_adm==="Выберите тер. управление"){
                    reg_adm="ALL"
                }
                document.querySelectorAll(".school").forEach(row =>{
                    if (row.classList.contains(reg_adm)){
                        row.style.display = 'table-row';
                        console.log(reg_adm)
                    }else{
                        row.style.display = 'none';
                        console.log(reg_adm)
                    }
                })
                document.querySelectorAll(".ter_adm").forEach(row =>{
                    if (row.classList.contains(reg_adm)){
                        row.style.display = 'table-row';
                        console.log(reg_adm)
                    }else{
                        row.style.display = 'none';
                        console.log(reg_adm)
                    }
                })
            })
        })
    })
})
