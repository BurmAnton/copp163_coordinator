from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Счёт на оплату", max_length=100,
    widget=forms.ClearableFileInput)

class ImportTicketDataForm(forms.Form):
    import_file = forms.FileField(label="Скан заявки", max_length=100,
    widget=forms.ClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(ImportTicketDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ImportTicketContractForm(forms.Form):
    import_file = forms.FileField(label="Скан договора", max_length=100,
    widget=forms.ClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(ImportTicketContractForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ImportSchoolOrderDataForm(forms.Form):
    import_file = forms.FileField(label="Скан приказа", max_length=100,
    widget=forms.ClearableFileInput)