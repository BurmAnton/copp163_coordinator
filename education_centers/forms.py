from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from easy_select2 import Select2, Select2Multiple, apply_select2, select2_modelform_meta

from .models import AbilimpicsWinner, Competence, EducationCenter, EducationProgram
from federal_empl_program.validators import validate_pdf_extension, validate_word_extension


class ImportDataForm(forms.Form):
    import_file = forms.FileField(label="Счёт на оплату", max_length=200,
    widget=forms.ClearableFileInput)


class ImportTicketDataForm(forms.Form):
    import_file = forms.FileField(label="Скан заявки", max_length=200,
    widget=forms.ClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(ImportTicketDataForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ImportTicketContractForm(forms.Form):
    import_file = forms.FileField(label="Скан договора", max_length=200,
    widget=forms.ClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(ImportTicketContractForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ImportSchoolOrderDataForm(forms.Form):
    import_file = forms.FileField(label="Скан приказа", max_length=200,
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


class IRPOProgramForm(forms.Form):
    program_word = forms.FileField(
        label="Программа по шаблону ЦОПП (с шапкой ЦОПП) в Word", 
        max_length=100,
        widget=forms.ClearableFileInput(attrs={
            'accept': '.doc,.docx,.xml,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'data-ext': 'word'
        }), 
        required=False, 
        validators=[validate_word_extension]
    )
    program_pdf = forms.FileField(
        label="Программа по шаблону ЦОПП (с шапкой ЦОПП), подписанная работодателем  (pdf)", 
        max_length=100,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf', 'data-ext': 'pdf'}), 
        required=False,  
        validators=[validate_pdf_extension]
    )
    teacher_review = forms.FileField(
        label="Рецензия преподавателя (pdf)", 
        max_length=100,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf', 'data-ext': 'pdf'}), 
        required=False, 
        validators=[validate_pdf_extension]
    )
    employer_review = forms.FileField(
        label="Рецензия работодателя (pdf)", 
        max_length=100,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf', 'data-ext': 'pdf'}), 
        required=False, 
        validators=[validate_pdf_extension]
    )

    def __init__(self, *args, **kwargs):
        super(IRPOProgramForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control irpo-file-input'
            visible.field.widget.attrs['style'] = 'margin-bottom: 15px;'
            visible.field.widget.attrs['onchange'] = "validateFile(this)"
