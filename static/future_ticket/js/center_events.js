document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.select-quota-profession').forEach(input => {
        input.addEventListener('change', (select) => {
            select = select.currentTarget;
            console.log(select)
            if (select.value != ""){
                quota = select.querySelector(`[value="${select.value}"]`).dataset.quota;
                quota_input = select.parentElement.parentElement.parentElement.querySelector('.reserved_quota');
                limit = (quota_input.dataset.limit)
                quota_input.removeAttribute('readonly');
                console.log(quota)
                console.log(limit)
                console.log(limit, quota, )
                if (parseInt(limit) > parseInt(quota)) {
                    quota_input.setAttribute('max', quota);
                    quota_input.parentElement.querySelector('.form-label').innerHTML = `Квота (Лимит: ${quota})`
                }else{
                    quota_input.setAttribute('max', limit);
                    quota_input.parentElement.querySelector('.form-label').innerHTML = `Квота (Лимит: ${limit})`
                }
                select.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector('.btn-primary').removeAttribute('disabled');
            }
        })
    })
    document.querySelectorAll('.edit-icon').forEach(icon => {
        icon.addEventListener('click', (edit_icon) => {
            edit_icon.currentTarget.classList.toggle("selected");
            edit_icon = edit_icon.currentTarget.parentElement.parentElement;
            edit_icon.querySelector('.btn-outline-danger').classList.toggle("disapear");
            
        })
    })
    document.querySelectorAll('.import-btn').forEach(btn => {
        btn.addEventListener('click', (import_btn) => {
            let event_card = import_btn.currentTarget.parentElement.parentElement;
            let profession = event_card.querySelector('.profession-hdr .tooltiptext').innerHTML;
            let event_date = event_card.dataset.event_date;
            let limit = event_card.dataset.limit;
            let event_id = event_card.dataset.event_id;
            console.log(event_id);
            let import_modal = document.querySelector('.import-participants-modal');
            import_modal.querySelector('#quota_profession').value = profession;
            import_modal.querySelector('#quota_event_date').value = event_date;
            import_modal.querySelector('#participants_limit').value = limit;
            import_modal.querySelector('#event_id').value = event_id;
        })
    })
    
})

$(function(){
	var inputs = $('.input');
	var paras = $('.description-flex-container').find('p');
	inputs.click(function(){
		var t = $(this),
				ind = t.index(),
				matchedPara = paras.eq(ind);
		
		t.add(matchedPara).addClass('active');
		inputs.not(t).add(paras.not(matchedPara)).removeClass('active');
	});
});