from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from easy_select2 import Select2, Select2Multiple, apply_select2, select2_modelform_meta

from .models import AbilimpicsWinner, Competence, EducationCenter, EducationProgram

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


class AbilimpicsWinnerCreationForm(UserCreationForm):

    class Meta:
        model = AbilimpicsWinner
        fields = ('email',)


class AbilimpicsWinnerChangeForm(UserChangeForm):
    qs = Competence.objects.all()
    competence = forms.ModelChoiceField(queryset=qs, widget=Select2(),
                                         label="Компетенция")
    qs = EducationProgram.objects.all()
    program = forms.ModelChoiceField(queryset=qs, widget=Select2(),
                                      label="Программа", required=False)
    qs = EducationCenter.objects.all()
    ed_center = forms.ModelChoiceField(queryset=qs, widget=Select2(),
                                        label="ЦО", required=False)
    class Meta:
        model = AbilimpicsWinner
        fields = ('email', 'first_name', 'middle_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(AbilimpicsWinnerChangeForm, self).__init__(*args, **kwargs)
        self.fields['ed_center'].widget.attrs['style'] = "width:600px"
        self.fields['competence'].widget.attrs['style'] = "width:600px"
        self.fields['program'].widget.attrs['style'] = "width:600px"

