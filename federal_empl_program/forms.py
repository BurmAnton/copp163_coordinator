from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Импортируемый файл", max_length=100,
    widget=forms.ClearableFileInput)


class ActDataForm(forms.Form):
    act_file = forms.FileField(label="Акт", max_length=100,
    widget=forms.ClearableFileInput, required=True)

    def __init__(self, *args, **kwargs):
        super(ActDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ActChangeDataForm(forms.Form):
    act_file = forms.FileField(label="Акт", max_length=100,
    widget=forms.ClearableFileInput, required=False)

    def __init__(self, *args, **kwargs):
        super(ActChangeDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class BillDataForm(forms.Form):
    bill_file = forms.FileField(label="Счёт", max_length=100,
    widget=forms.ClearableFileInput, required=False)

    def __init__(self, *args, **kwargs):
        super(BillDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'