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
                }else{
                    quota_input.setAttribute('max', limit);
                }
                select.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector('.btn-primary').removeAttribute('disabled');
            }
        })
    })
    document.querySelectorAll('.edit-icon').forEach(icon => {
        console.log(icon);
        icon.addEventListener('click', (edit_icon) => {
            edit_icon.currentTarget.classList.toggle("selected");
            edit_icon = edit_icon.currentTarget.parentElement.parentElement;
            edit_icon.querySelector('.btn-outline-danger').classList.toggle("disapear");
            
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