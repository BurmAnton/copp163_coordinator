from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Счёт на оплату", max_length=100,
    widget=forms.ClearableFileInput)

class ImportTicketDataForm(forms.Form):
    import_file = forms.FileField(label="Скан заявки", max_length=100,
    widget=forms.ClearableFileInput)

class ImportSchoolOrderDataForm(forms.Form):
    import_file = forms.FileField(label="Скан приказа", max_length=100,
    widget=forms.ClearableFileInput)