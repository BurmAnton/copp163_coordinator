from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Импорт программ", max_length=100,
    widget=forms.ClearableFileInput)