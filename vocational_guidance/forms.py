from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Импортируемый файл", max_length=100,
    widget=forms.ClearableFileInput)
