document.addEventListener('DOMContentLoaded', function() {
    set_average_quota_cost();
    set_average_cost(document.querySelector('.table-72'));
    set_average_cost(document.querySelector('.table-144'));
    set_average_cost(document.querySelector('.table-256'));
    
    document.querySelectorAll('.program_price').forEach(input =>{
        input.addEventListener('change', (event) =>{
            price = event.currentTarget;
            quota = price.parentElement.parentElement.querySelector('.program_quota');
            
            set_average_cost(price.parentElement.parentElement.parentElement);
            set_average_quota_cost();
        })
    })
    document.querySelectorAll('.program_quota').forEach(input =>{
        input.addEventListener('change', (event) =>{
            quota = event.currentTarget;
            price = quota.parentElement.parentElement.querySelector('.program_price');

            set_average_cost(quota.parentElement.parentElement.parentElement);
            set_average_quota_cost();
        })
    })
})

function check_request_conditions() {

}

function set_average_cost(table){
    var programs_sum = parseFloat(0.0);
    var quotas_count = 0;
    
    table.querySelectorAll('.program_sum').forEach(input =>{
        price = input.parentElement.querySelector('.program_price');
        quota = input.parentElement.querySelector('.program_quota');
        sum_td = price.parentElement.parentElement.querySelector('.program_sum');
        sum = (parseFloat(price.value.replace(',', '.'))*quota.value).toFixed(2);
        sum_td.innerHTML = `${sum} руб`;
        programs_sum += parseFloat(price.value.replace(',', '.'))*quota.value;
        console.log(programs_sum)
        if (quota.value != 0) {
            quotas_count += + quota.value;
        }
    })
    let average_cost = programs_sum / quotas_count;
    if (isNaN(average_cost)) {average_cost = 0;}
    
    if (table.querySelector('.quota_count') != null) {
        table.querySelector('.quota_count').innerHTML = `${quotas_count} квота`;
        table.querySelector('.bracket_sum').innerHTML = `${programs_sum.toFixed(2)} руб`;
        table.querySelector('.average_cost').innerHTML = `${average_cost.toFixed(2)} руб`;
    }
    
}

function set_average_quota_cost(){
    var programs_sum = 0;
    var quotas_count = 0;
    document.querySelectorAll('.program_sum').forEach(input =>{
        price = input.parentElement.querySelector('.program_price');
        quota = input.parentElement.querySelector('.program_quota');
        programs_sum += parseFloat(price.value.replace(',', '.'))*quota.value;
        if (quota.value != 0) {
            quotas_count += + quota.value;
        }
    })

    let average_cost = programs_sum / quotas_count;
    if (isNaN(average_cost)) {average_cost = 0;}

    document.querySelector('.quota_count_quota').innerHTML = `${quotas_count} квота`;
    document.querySelector('.bracket_sum_quota').innerHTML = `${programs_sum.toFixed(2)} руб`;
    document.querySelector('.average_cost_quota').innerHTML = `${average_cost.toFixed(2)} руб`;
}
