

def validate_word_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Неверное расширение файла (принимает только doc/docx)!')
    

def validate_pdf_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', ]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Неверное расширение файла (принимает только pdf)!')