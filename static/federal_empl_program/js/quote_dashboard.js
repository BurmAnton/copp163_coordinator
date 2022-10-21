document.addEventListener('DOMContentLoaded', function() {
    CountQuotes(1, 72)
    CountQuotes(1, 144)
    CountQuotes(1, 256)
    CountQuotes(2, 72)
    CountQuotes(2, 144)
    CountQuotes(2, 256)
    AddInputListener(1, 72)
    AddInputListener(1, 144)
    AddInputListener(1, 256)
    AddInputListener(2, 72)
    AddInputListener(2, 144)
    AddInputListener(2, 256)
})

function AddInputListener(qoute, lenght){
    document.querySelectorAll(`.quote_${qoute}_${lenght}_quote`).forEach(input =>{
        input.addEventListener('change', () => {
            CountQuotes(qoute, lenght)
            console.log(input.dataset.id)
            fetch('/quotes/dashboard/', {
                method: 'POST',
                body: JSON.stringify({
                    ed_center_id: input.dataset.id,
                    value: input.value,
                    qoute: qoute,
                    lenght: lenght
                })
                })
                .then(response => response.json())
                .then(result => {})
        });
    })
}

function CountQuotes(qoute, lenght){
    document.querySelectorAll(`.quote_${qoute}_${lenght}_remains`).forEach(cell =>{
        let id = cell.dataset.id
        let quote = document.querySelector(`.quote_${qoute}_${lenght}_quote_${id}`).value
        let fact = document.querySelector(`.quote_${qoute}_${lenght}_fact_${id}`).innerHTML
        cell.innerHTML = quote - fact
    })
}