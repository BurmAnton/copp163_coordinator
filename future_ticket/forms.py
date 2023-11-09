from django import forms

class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Импорт программ", max_length=100,
    widget=forms.ClearableFileInput)

class ImportParticipantsForm(forms.Form):
    import_file = forms.FileField(label="Импорт участников", max_length=200,
    widget=forms.ClearableFileInput, required=True)

    def __init__(self, *args, **kwargs):
        super(ImportParticipantsForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ImportDocumentForm(forms.Form):
    import_file = forms.FileField(label="Загрузить документ", max_length=200,
    widget=forms.ClearableFileInput, required=True)

    def __init__(self, *args, **kwargs):
        super(ImportDocumentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'